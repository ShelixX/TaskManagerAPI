from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app import security
from app.repositories import users
from app import schemas
from app.models import User

def register_user(data: schemas.UserCreate, db: Session) -> User:
    if users.get_user_by_username(data.username, db = db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    return users.create_user(data, db)

def authenticate_user(username: str, password: str, db: Session) -> User:
    user = users.get_user_by_username(username, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not security.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is deactivated")
    return user

def login_user(username: str, password: str, db: Session) -> tuple[str, str]:
    user = authenticate_user(username, password, db)
    access_token = security.create_access_token(user)
    refresh_token = security.create_refresh_token(user, db)
    return access_token, refresh_token

def refresh_user_tokens(refresh_token: str | None, db: Session) -> tuple[str, str]:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    access_token, refresh_token = security.rotate_refresh_token(refresh_token, db)
    return access_token, refresh_token

def logout_user(refresh_token: str | None, db: Session):
    if not refresh_token:
        return
    try:
        security.revoke_refresh_token(refresh_token, db)
    except HTTPException:
        db.rollback()