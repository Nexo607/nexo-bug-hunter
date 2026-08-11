import httpx
from urllib.parse import urlparse
from ..core.db import Session
from ..core.config import settings
from ..core.safety import public_host
from ..models import Scan,Event,Finding
from ..scanners.catalog import SCANNERS
async def run_scan(scan_id,target,profile):
    try:
        if not public_host(urlparse(target).hostname or ""): raise ValueError("Target resolves to a private, loopback, reserved, or otherwise non-public address.")
        limits=httpx.Limits(max_connections=settings.max_concurrency,max_keepalive_connections=settings.max_concurrency)
        async with httpx.AsyncClient(timeout=settings.request_timeout,limits=limits,headers={"User-Agent":"NEXO-Bug-Hunter/3.0"}) as client:
            selected=SCANNERS if profile in ("standard","deep") else SCANNERS[:2]
            for i,s in enumerate(selected,1):
                async with Session() as db:
                    q=await db.get(Scan,scan_id)
                    if not q or q.status=="CANCELLED": return
                    q.status="SCANNING";q.progress=int((i-1)/len(selected)*90)
                    db.add(Event(scan_id=scan_id,stage=s.name,message=s.description));await db.commit()
                results=await s.run(target,client)
                async with Session() as db:
                    q=await db.get(Scan,scan_id);q.requests+=1
                    for x in results:
                        if hasattr(x,"title"):
                            db.add(Finding(scan_id=scan_id,title=x.title,severity=x.severity,confidence=x.confidence,category=x.category,cwe=x.cwe,url=x.url,method=x.method,parameter=x.parameter,evidence=x.evidence,impact=x.impact,remediation=x.remediation))
                    await db.commit()
            async with Session() as db:
                q=await db.get(Scan,scan_id);q.progress=100;q.status="COMPLETED"
                from sqlalchemy import select
                q.findings=len((await db.execute(select(Finding).where(Finding.scan_id==scan_id))).scalars().all())
                db.add(Event(scan_id=scan_id,stage="COMPLETED",message="Scan completed with evidence-producing modules."));await db.commit()
    except Exception as e:
        async with Session() as db:
            q=await db.get(Scan,scan_id)
            if q:q.status="FAILED";q.error=str(e)[:500]
            db.add(Event(scan_id=scan_id,stage="ERROR",message=str(e)[:500]));await db.commit()
