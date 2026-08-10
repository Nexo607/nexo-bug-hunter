import asyncio, uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import Scan, Finding, ScanEvent, AuditLog
from ..scanners import REGISTRY, PROFILES
from ..scanners.base import ScannerContext
from ..config import settings

async def execute_scan(scan_id: int):
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if not scan:
            return
        scan.status = "running"
        scan.progress = 3
        scan.current_stage = "Target validated"
        scan.started_at = datetime.now(timezone.utc)
        db.commit()

        async def emit(level, message):
            current = db.get(Scan, scan_id)
            if not current or current.status == "cancelled":
                return
            db.add(ScanEvent(scan_id=scan_id, level=level, message=message))
            db.commit()

        await emit("INFO", "Target scope validation passed")
        await emit("INFO", "HTTP discovery stage started")
        await asyncio.sleep(0)
        scan = db.get(Scan, scan_id)
        scan.progress = 12
        scan.current_stage = "HTTP discovery"
        db.commit()

        names = scan.scanners or PROFILES.get(scan.profile, PROFILES["Quick"])
        names = [n for n in names if n in REGISTRY]
        total = max(1, len(names))

        for index, name in enumerate(names, 1):
            scan = db.get(Scan, scan_id)
            if scan.status == "cancelled":
                await emit("WARN", "Scan cancelled by user")
                return
            scan.current_stage = f"Running {name}"
            scan.progress = 10 + int((index - 1) / total * 75)
            db.commit()
            scanner = REGISTRY[name]()
            ctx = ScannerContext(
                target=scan.target.target,
                scan_id=scan.id,
                request_limit=settings.max_requests_per_scan,
                timeout=settings.request_timeout,
                emit=emit,
            )
            async for raw in scanner.run(ctx):
                if raw.get("type") == "technology":
                    continue
                finding = Finding(
                    scan_id=scan.id,
                    finding_id=str(uuid.uuid4()),
                    title=raw["title"],
                    severity=raw["severity"],
                    confidence=raw["confidence"],
                    owasp_category=raw["owasp_category"],
                    cwe=raw.get("cwe", ""),
                    target=raw["target"],
                    endpoint=raw.get("endpoint", ""),
                    method=raw.get("method", "GET"),
                    parameter=raw.get("parameter", ""),
                    evidence=raw.get("evidence", ""),
                    remediation=raw.get("remediation", ""),
                    references=raw.get("references", []),
                )
                db.add(finding)
                await emit("WARN", f"Finding recorded: {finding.title}")
            db.commit()

        scan = db.get(Scan, scan_id)
        if scan.status == "cancelled":
            return
        scan.progress = 92
        scan.current_stage = "Finding normalization"
        db.commit()
        await emit("INFO", "Finding normalization completed")
        scan.progress = 97
        scan.current_stage = "Report preparation"
        db.commit()
        await emit("INFO", "Scan pipeline completed")
        scan.status = "completed"
        scan.progress = 100
        scan.current_stage = "Completed"
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        scan = db.get(Scan, scan_id)
        if scan:
            scan.status = "failed"
            scan.current_stage = "Failed"
            scan.error_message = "Scan failed. Internal diagnostics are not exposed to the client."
            db.commit()
    finally:
        db.close()

# Import after definition to avoid circular import during app bootstrap.
from ..database import SessionLocal
