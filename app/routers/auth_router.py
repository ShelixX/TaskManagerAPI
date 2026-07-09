from fastapi import APIRouter, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app import bearer
from app import schemas
from app.dependencies import get_db
from app.services import auth
from app.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    access_token, refresh_token = await auth.login_user(form_data.username, form_data.password, db)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=60 * 60 * 24 * settings.refresh_token_expire_days,
        path="/auth"
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.CurrentUserResponse)
async def register(data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await auth.register_user(data, db)
    return {"message": "User has been created!", "user_data": user}

@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db)
):
    access_token, refresh_token = await auth.refresh_user_tokens(refresh_token, db)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=60 * 60 * 24 * settings.refresh_token_expire_days,
        path="/auth"
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db)
):
    await auth.logout_user(refresh_token, db)
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/auth"
    )
    return {"message": "Logged out"}

@router.get("/me", response_model=schemas.CurrentUserResponse)
async def get_current_user(user = Depends(bearer.get_current_user)):
    return {
        "message": "Current profile",
        "user_data": user
    }