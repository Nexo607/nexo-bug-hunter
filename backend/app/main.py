import time, secrets
from collections import defaultdict, deque
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .database import Base, engine
from .api.routes import router
from .api.auth import router as auth_router
from . import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NEXO Bug Hunter API",
    version=settings.version,
    description="Authorized application-security assessment API. Findings are derived from real scanner output only."
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type"],
)

_buckets = defaultdict(deque)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path in ("/api/health","/docs","/redoc","/openapi.json"):
        return await call_next(request)
    key = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = _buckets[key]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.rate_limit_per_minute:
        rid = secrets.token_hex(12)
        return JSONResponse(status_code=429, content={"error":True,"message":"Rate limit exceeded.","code":"RATE_LIMITED","request_id":rid})
    bucket.append(now)
    return await call_next(request)

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = secrets.token_hex(12)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    rid = secrets.token_hex(12)
    return JSONResponse(status_code=500, content={"error":True,"message":"Internal server error.","code":"INTERNAL_ERROR","request_id":rid})

app.include_router(auth_router)
app.include_router(router)

@app.get("/")
def root():
    return {"service":"NEXO Bug Hunter","version":settings.version,"docs":"/docs"}
