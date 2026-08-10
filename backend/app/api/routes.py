import asyncio, csv, io, json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Target, Scan, Finding, User, ScanEvent, AuditLog
from ..schemas.schemas import TargetCreate, TargetOut, ScanCreate, ScanOut, FindingOut, FindingPatch, ScanEventOut
from ..utils.security import validate_target
from .auth import current_user
from ..scanners import REGISTRY, PROFILES
from ..workers.scan_worker import execute_scan

router = APIRouter(prefix="/api", tags=["platform"])

@router.get("/health")
def health():
    return {"status":"ok","service":"nexo-bug-hunter","version":"1.1.0"}

@router.get("/system/status")
def system_status():
    return {"service":"nexo-bug-hunter","status":"operational","scanner_modules":len(REGISTRY),"version":"1.1.0"}

@router.get("/scanner-catalog")
def scanner_catalog(user: User = Depends(current_user)):
    return [{"name":k,"description":v().description,"owasp_category":v().owasp_category,"enabled":k in ("headers","technology")} for k,v in REGISTRY.items()]

@router.post("/targets", response_model=TargetOut)
def create_target(data: TargetCreate, db: Session=Depends(get_db), user: User=Depends(current_user)):
    validate_target(data.target)
    if not data.authorization_confirmed:
        raise HTTPException(400, "Authorization confirmation is required.")
    obj = Target(owner_id=user.id, **data.model_dump())
    db.add(obj); db.add(AuditLog(user_id=user.id, action="target.created", target=data.target)); db.commit(); db.refresh(obj)
    return obj

@router.get("/targets", response_model=list[TargetOut])
def list_targets(db: Session=Depends(get_db), user: User=Depends(current_user)):
    return db.query(Target).filter(Target.owner_id==user.id).order_by(Target.id.desc()).all()

@router.delete("/targets/{target_id}")
def delete_target(target_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    obj=db.query(Target).filter(Target.id==target_id,Target.owner_id==user.id).first()
    if not obj: raise HTTPException(404,"Target not found.")
    if db.query(Scan).filter(Scan.target_id==obj.id, Scan.status.in_(["queued","running"])).first():
        raise HTTPException(409,"Target has an active scan.")
    db.delete(obj); db.add(AuditLog(user_id=user.id, action="target.deleted", target=obj.target)); db.commit()
    return {"deleted":True}

@router.post("/scans", response_model=ScanOut)
async def create_scan(data:ScanCreate, db:Session=Depends(get_db), user:User=Depends(current_user)):
    target=db.query(Target).filter(Target.id==data.target_id,Target.owner_id==user.id).first()
    if not target: raise HTTPException(404,"Target not found.")
    if not target.authorization_confirmed: raise HTTPException(400,"Target authorization is not confirmed.")
    scanners = data.scanners or PROFILES[data.profile]
    unknown = [x for x in scanners if x not in REGISTRY]
    if unknown: raise HTTPException(400, f"Unknown scanner(s): {', '.join(unknown)}")
    scan=Scan(owner_id=user.id,target_id=target.id,profile=data.profile,scanners=scanners,status="queued",current_stage="Queued")
    db.add(scan); db.add(AuditLog(user_id=user.id, action="scan.created", target=target.target, metadata_json={"profile":data.profile})); db.commit(); db.refresh(scan)
    asyncio.create_task(execute_scan(scan.id))
    return scan

@router.get("/scans", response_model=list[ScanOut])
def list_scans(db:Session=Depends(get_db), user:User=Depends(current_user)):
    return db.query(Scan).filter(Scan.owner_id==user.id).order_by(Scan.id.desc()).all()

@router.get("/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    obj=db.query(Scan).filter(Scan.id==scan_id,Scan.owner_id==user.id).first()
    if not obj: raise HTTPException(404,"Scan not found.")
    return obj

@router.get("/scans/{scan_id}/events", response_model=list[ScanEventOut])
def scan_events(scan_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    scan=db.query(Scan).filter(Scan.id==scan_id,Scan.owner_id==user.id).first()
    if not scan: raise HTTPException(404,"Scan not found.")
    return db.query(ScanEvent).filter(ScanEvent.scan_id==scan_id).order_by(ScanEvent.id.asc()).all()

@router.post("/scans/{scan_id}/cancel", response_model=ScanOut)
def cancel_scan(scan_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    obj=db.query(Scan).filter(Scan.id==scan_id,Scan.owner_id==user.id).first()
    if not obj: raise HTTPException(404,"Scan not found.")
    if obj.status in ("queued","running"):
        obj.status="cancelled"; obj.current_stage="Cancelled"; db.add(AuditLog(user_id=user.id, action="scan.cancelled", target=obj.target.target)); db.commit(); db.refresh(obj)
    return obj

@router.get("/findings", response_model=list[FindingOut])
def findings(db:Session=Depends(get_db), user:User=Depends(current_user)):
    return db.query(Finding).join(Scan).filter(Scan.owner_id==user.id).order_by(Finding.id.desc()).all()

@router.get("/findings/{finding_id}", response_model=FindingOut)
def finding(finding_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    obj=db.query(Finding).join(Scan).filter(Finding.id==finding_id,Scan.owner_id==user.id).first()
    if not obj: raise HTTPException(404,"Finding not found.")
    return obj

@router.patch("/findings/{finding_id}", response_model=FindingOut)
def patch_finding(finding_id:int, data:FindingPatch, db:Session=Depends(get_db), user:User=Depends(current_user)):
    obj=db.query(Finding).join(Scan).filter(Finding.id==finding_id,Scan.owner_id==user.id).first()
    if not obj: raise HTTPException(404,"Finding not found.")
    if data.status: obj.status=data.status
    db.add(AuditLog(user_id=user.id, action="finding.updated", metadata_json={"finding_id":finding_id,"status":data.status})); db.commit(); db.refresh(obj)
    return obj

@router.get("/exports/findings.json")
def export_json(db:Session=Depends(get_db), user:User=Depends(current_user)):
    rows=findings(db,user)
    payload=[FindingOut.model_validate(x).model_dump(mode="json") for x in rows]
    return Response(json.dumps(payload, indent=2), media_type="application/json", headers={"Content-Disposition":"attachment; filename=nexo-findings.json"})

@router.get("/exports/findings.csv")
def export_csv(db:Session=Depends(get_db), user:User=Depends(current_user)):
    rows=findings(db,user)
    out=io.StringIO(); writer=csv.writer(out)
    writer.writerow(["Finding","Severity","Confidence","OWASP","Target","Endpoint","Status","First Seen","Last Seen"])
    for x in rows:
        writer.writerow([x.title,x.severity,x.confidence,x.owasp_category,x.target,x.endpoint,x.status,x.first_seen.isoformat(),x.last_seen.isoformat()])
    return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=nexo-findings.csv"})
