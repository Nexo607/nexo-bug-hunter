import ipaddress, socket, secrets, re
from urllib.parse import urlparse
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from ..config import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
HOST_RE = re.compile(r"^[A-Za-z0-9.-]+$")

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd.verify(password, hashed)

def create_token(subject: str) -> str:
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(hours=12)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def request_id() -> str:
    return secrets.token_hex(12)

def validate_target(raw: str) -> str:
    value = raw.strip()
    parsed = urlparse(value if "://" in value else "https://" + value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise HTTPException(400, "Target must be a valid HTTP(S) URL or hostname.")
    host = parsed.hostname.rstrip(".")
    if len(host) > 253 or not HOST_RE.match(host) or ".." in host:
        raise HTTPException(400, "Invalid target hostname.")
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise HTTPException(400, "Restricted network targets are not allowed.")
    except ValueError:
        try:
            for item in socket.getaddrinfo(host, None, type=socket.SOCK_STREAM):
                addr = item[4][0]
                ip = ipaddress.ip_address(addr)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                    raise HTTPException(400, "Target resolves to a restricted network address.")
        except socket.gaierror:
            pass
    return value
