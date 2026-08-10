from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any

class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=12, max_length=128)

class Login(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TargetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target: str = Field(min_length=1, max_length=2048)
    scope: str = Field(default="", max_length=10000)
    authorization_confirmed: bool = False
    notes: str = Field(default="", max_length=10000)

class TargetOut(TargetCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ScanCreate(BaseModel):
    target_id: int
    profile: str = Field(default="Quick", pattern="^(Quick|Standard|Deep)$")
    scanners: List[str] = []

class ScanOut(BaseModel):
    id: int
    target_id: int
    profile: str
    status: str
    progress: int
    current_stage: str
    scanners: List[str]
    created_at: datetime
    error_message: str = ""
    model_config = ConfigDict(from_attributes=True)

class ScanEventOut(BaseModel):
    id: int
    level: str
    message: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FindingPatch(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(Open|Confirmed|False Positive|Fixed|Accepted Risk)$")

class FindingOut(BaseModel):
    id: int
    finding_id: str
    title: str
    severity: str
    confidence: str
    owasp_category: str
    cwe: str
    target: str
    endpoint: str
    method: str
    parameter: str
    evidence: str
    remediation: str
    references: List[Any]
    status: str
    first_seen: datetime
    last_seen: datetime
    model_config = ConfigDict(from_attributes=True)
