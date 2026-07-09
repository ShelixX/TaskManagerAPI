from datetime import timedelta, datetime, timezone
import jwt
from pwdlib import PasswordHash
from app.config import settings
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models import User, RefreshToken
import hashlib
import uuid

SECRET_KEY = settings.secret_key

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def hash_token(token:str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(user: User) -> str:
    exp = utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user.id), "type": "access", "exp": exp}
    encode_jwt = jwt.encode(to_encode, key = SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

def decode_token(token: str) -> dict | None:
    try:
        decode_jwt = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return decode_jwt
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def create_refresh_token(user: User, db: Session, commit: bool = True) -> str:
    now = utc_now()
    exp = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    payload = {
        "sub": str(user.id),
        "jti": jti,
        "type": "refresh",
        "iat": now,
        "exp": exp
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    db_token = RefreshToken(
        jti = jti,
        token = hash_token(token),
        user_id = user.id,
        created_at = now,
        expires_at = exp
    )
    db.add(db_token)
    if commit:
        db.commit()
    return token

def rotate_refresh_token(refresh_token:str, db: Session) -> tuple[str, str]:
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )
    try:
        user_id_int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )
    token_hash = hash_token(refresh_token)
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti,
            RefreshToken.token == token_hash
        ).first()
    )
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or not found",
        )
    if db_token.user_id != user_id_int:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )
    if db_token.revoked:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == db_token.user_id,
            RefreshToken.revoked == False,
        ).update({"revoked": True})
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Refresh token reuse detected",
        )
    if db_token.expires_at.replace(tzinfo=timezone.utc) < utc_now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    user: User | None = db.query(User).filter(User.id == user_id_int).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    updated = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.jti == jti,
            RefreshToken.token == token_hash,
            RefreshToken.revoked == False,
        )
        .update({"revoked": True})
    )
    if updated != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or not found",
        )
    new_access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user, db, commit=False)
    db.commit()
    return new_access_token, new_refresh_token

def revoke_refresh_token(refresh_token: str, db: Session):
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )
    token_hash = hash_token(refresh_token)
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.jti == jti,
                RefreshToken.token == token_hash,
                RefreshToken.revoked == False
                ).first()
    )
    if db_token:
        db_token.revoked = True
        db.commit()
