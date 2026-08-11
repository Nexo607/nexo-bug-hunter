from datetime import datetime,timezone
from sqlalchemy import String,Text,DateTime,Boolean,Integer,Float
from sqlalchemy.orm import Mapped,mapped_column
from ..core.db import Base
def now(): return datetime.now(timezone.utc)
class Target(Base):
    __tablename__="targets"; id:Mapped[int]=mapped_column(primary_key=True)
    url:Mapped[str]=mapped_column(String(2048),unique=True,index=True)
    authorized:Mapped[bool]=mapped_column(Boolean,default=False); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Scan(Base):
    __tablename__="scans"; id:Mapped[int]=mapped_column(primary_key=True)
    target_id:Mapped[int]=mapped_column(Integer,index=True); profile:Mapped[str]=mapped_column(String(30),default="standard")
    status:Mapped[str]=mapped_column(String(30),default="QUEUED"); progress:Mapped[int]=mapped_column(Integer,default=0)
    requests:Mapped[int]=mapped_column(Integer,default=0); findings:Mapped[int]=mapped_column(Integer,default=0)
    error:Mapped[str|None]=mapped_column(Text,nullable=True); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Event(Base):
    __tablename__="scan_events"; id:Mapped[int]=mapped_column(primary_key=True)
    scan_id:Mapped[int]=mapped_column(Integer,index=True); stage:Mapped[str]=mapped_column(String(80))
    message:Mapped[str]=mapped_column(Text); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Finding(Base):
    __tablename__="findings"; id:Mapped[int]=mapped_column(primary_key=True); scan_id:Mapped[int]=mapped_column(Integer,index=True)
    title:Mapped[str]=mapped_column(String(300)); severity:Mapped[str]=mapped_column(String(20))
    confidence:Mapped[int]=mapped_column(Integer); category:Mapped[str]=mapped_column(String(120))
    cwe:Mapped[str|None]=mapped_column(String(50),nullable=True); url:Mapped[str]=mapped_column(String(2048))
    method:Mapped[str]=mapped_column(String(10),default="GET"); parameter:Mapped[str|None]=mapped_column(String(300),nullable=True)
    evidence:Mapped[str]=mapped_column(Text); impact:Mapped[str]=mapped_column(Text); remediation:Mapped[str]=mapped_column(Text)
    status:Mapped[str]=mapped_column(String(30),default="Potential"); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
