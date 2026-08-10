from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    targets = relationship("Target", back_populates="owner")
    scans = relationship("Scan", back_populates="owner")

class Target(Base):
    __tablename__ = "targets"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    target: Mapped[str] = mapped_column(String(2048))
    scope: Mapped[str] = mapped_column(Text, default="")
    authorization_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    owner = relationship("User", back_populates="targets")
    scans = relationship("Scan", back_populates="target")

class ScanProfile(Base):
    __tablename__ = "scan_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    scanners: Mapped[list] = mapped_column(JSON, default=list)
    concurrency: Mapped[int] = mapped_column(Integer, default=2)
    request_limit: Mapped[int] = mapped_column(Integer, default=50)

class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("targets.id"), index=True)
    profile: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    current_stage: Mapped[str] = mapped_column(String(80), default="Queued")
    scanners: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str] = mapped_column(Text, default="")
    owner = relationship("User", back_populates="scans")
    target = relationship("Target", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    events = relationship("ScanEvent", back_populates="scan", cascade="all, delete-orphan")

class ScanEvent(Base):
    __tablename__ = "scan_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), index=True)
    level: Mapped[str] = mapped_column(String(16), default="INFO")
    message: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    scan = relationship("Scan", back_populates="events")

class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), index=True)
    finding_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(20), index=True)
    confidence: Mapped[str] = mapped_column(String(20))
    owasp_category: Mapped[str] = mapped_column(String(120))
    cwe: Mapped[str] = mapped_column(String(80), default="")
    target: Mapped[str] = mapped_column(String(2048))
    endpoint: Mapped[str] = mapped_column(String(2048), default="")
    method: Mapped[str] = mapped_column(String(12), default="GET")
    parameter: Mapped[str] = mapped_column(String(255), default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    remediation: Mapped[str] = mapped_column(Text, default="")
    references: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="Open", index=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    scan = relationship("Scan", back_populates="findings")

class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey("findings.id"), index=True)
    request_excerpt: Mapped[str] = mapped_column(Text, default="")
    response_excerpt: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), index=True)
    format: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True)
    target: Mapped[str] = mapped_column(String(2048), default="")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
