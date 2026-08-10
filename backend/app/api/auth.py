from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas.schemas import UserCreate, Login, Token
from ..utils.security import hash_password, verify_password, create_token
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
bearer = HTTPBearer()

@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "Email already registered.")
    user = User(email=email, password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=create_token(str(user.id)))

@router.post("/login", response_model=Token)
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower().strip()).first()
    if not user or not user.is_active or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials.")
    return Token(access_token=create_token(str(user.id)))

def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid or expired token.")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "User not found.")
    return user
