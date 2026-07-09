from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import security
from app.repositories import users
from app import schemas
from app.models import User

async def register_user(data: schemas.UserCreate, db: AsyncSession) -> User:
    if await users.get_user_by_username(data.username, db = db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    return await users.create_user(data, db)

async def authenticate_user(username: str, password: str, db: AsyncSession) -> User:
    user = await users.get_user_by_username(username, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not await security.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is deactivated")
    return user

async def login_user(username: str, password: str, db: AsyncSession) -> tuple[str, str]:
    user = await authenticate_user(username, password, db)
    access_token = security.create_access_token(user)
    refresh_token = await security.create_refresh_token(user, db)
    return access_token, refresh_token

async def refresh_user_tokens(refresh_token: str | None, db: AsyncSession) -> tuple[str, str]:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    access_token, refresh_token = await security.rotate_refresh_token(refresh_token, db)
    return access_token, refresh_token

async def logout_user(refresh_token: str | None, db: AsyncSession):
    if not refresh_token:
        return
    try:
        await security.revoke_refresh_token(refresh_token, db)
    except HTTPException:
        await db.rollback()