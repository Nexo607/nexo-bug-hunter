import asyncio
from fastapi import FastAPI,HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .core.config import settings
from .core.db import Base,engine,get_db
from .core.safety import normalize
from .models import Target,Scan,Finding,Event
from .scanners.catalog import CATALOG
from .workers.runner import run_scan
app=FastAPI(title="NEXO Bug Hunter",version=settings.version,description="Authorized AppSec automation platform")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",")],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.on_event("startup")
async def start():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
class Login(BaseModel):username:str;password:str
class TargetIn(BaseModel):target:str;authorization_confirmed:bool
class ScanIn(BaseModel):target_id:int;authorization_confirmed:bool;profile:str="standard"
class FindingPatch(BaseModel):status:str
@app.get("/api/health")
async def health():return {"status":"ok","service":"nexo-bug-hunter","version":settings.version}
@app.get("/api/system/status")
async def system():return {"status":"operational","version":settings.version,"scanner_count":len(CATALOG)}
@app.post("/api/auth/login")
async def login(x:Login):
    if x.username!=settings.login_username or x.password!=settings.login_password:raise HTTPException(401,"Invalid credentials")
    return {"access_token":"session","username":x.username}
@app.get("/api/scanner-catalog")
async def catalog():return CATALOG
@app.get("/api/targets")
async def targets(db:AsyncSession=Depends(get_db)):return (await db.execute(select(Target).order_by(Target.id.desc()))).scalars().all()
@app.post("/api/targets")
async def add(x:TargetIn,db:AsyncSession=Depends(get_db)):
    if not x.authorization_confirmed:raise HTTPException(403,"Authorization confirmation is required")
    try:u=normalize(x.target)
    except ValueError as e:raise HTTPException(400,str(e))
    t=Target(url=u,authorized=True);db.add(t)
    try:await db.commit()
    except Exception:await db.rollback();raise HTTPException(409,"Target already exists")
    await db.refresh(t);return t
@app.delete("/api/targets/{id}")
async def delete(id:int,db:AsyncSession=Depends(get_db)):
    t=await db.get(Target,id)
    if not t:raise HTTPException(404,"Target not found")
    await db.delete(t);await db.commit();return {"deleted":True}
@app.get("/api/scans")
async def scans(db:AsyncSession=Depends(get_db)):return (await db.execute(select(Scan).order_by(Scan.id.desc()))).scalars().all()
@app.post("/api/scans")
async def scan(x:ScanIn,db:AsyncSession=Depends(get_db)):
    if not x.authorization_confirmed:raise HTTPException(403,"Authorization confirmation is required")
    t=await db.get(Target,x.target_id)
    if not t or not t.authorized:raise HTTPException(403,"Target is not authorized")
    if x.profile not in ("quick","standard","deep"):raise HTTPException(400,"Invalid scan profile")
    s=Scan(target_id=t.id,profile=x.profile);db.add(s);await db.commit();await db.refresh(s);asyncio.create_task(run_scan(s.id,t.url,x.profile));return s
@app.get("/api/scans/{id}")
async def scan_get(id:int,db:AsyncSession=Depends(get_db)):
    s=await db.get(Scan,id)
    if not s:raise HTTPException(404,"Scan not found")
    return s
@app.get("/api/scans/{id}/events")
async def events(id:int,db:AsyncSession=Depends(get_db)):return (await db.execute(select(Event).where(Event.scan_id==id).order_by(Event.id))).scalars().all()
@app.post("/api/scans/{id}/cancel")
async def cancel(id:int,db:AsyncSession=Depends(get_db)):
    s=await db.get(Scan,id)
    if not s:raise HTTPException(404,"Scan not found")
    s.status="CANCELLED";await db.commit();return s
@app.get("/api/findings")
async def findings(db:AsyncSession=Depends(get_db)):return (await db.execute(select(Finding).order_by(Finding.id.desc()))).scalars().all()
@app.get("/api/findings/{id}")
async def finding(id:int,db:AsyncSession=Depends(get_db)):
    f=await db.get(Finding,id)
    if not f:raise HTTPException(404,"Finding not found")
    return f
@app.patch("/api/findings/{id}")
async def finding_patch(id:int,x:FindingPatch,db:AsyncSession=Depends(get_db)):
    if x.status not in {"Potential","Open","Confirmed","False Positive","Fixed","Accepted Risk"}:raise HTTPException(400,"Invalid status")
    f=await db.get(Finding,id)
    if not f:raise HTTPException(404,"Finding not found")
    f.status=x.status;await db.commit();return f
