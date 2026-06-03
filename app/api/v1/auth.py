from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db, get_redis
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    """Зарегистрировать нового пользователя

    Args:
        body (UserCreate): Email и пароль

    Returns:
        UserResponse: Данные созданного пользователя
    """
    return await auth_service.register_user(db, body.model_dump())


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """Аутентифицировать пользователя и получить токены

    Args:
        body (LoginRequest): Email и пароль

    Returns:
        TokenResponse: Access и refresh токены
    """
    return await auth_service.login_user(db, body.model_dump(), redis)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, redis: Redis = Depends(get_redis)):
    """Обновить токены по refresh_token

    Args:
        body (RefreshRequest): Refresh токен

    Returns:
        TokenResponse: Новая пара access и refresh токенов
    """
    return await auth_service.refresh_tokens(body.refresh_token, redis)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    redis: Redis = Depends(get_redis),
    current_user: dict = Depends(get_current_user),
):
    """Выполнить выход (инвалидировать токены)

    Requires access token в заголовке Authorization.
    """
    await auth_service.logout(current_user["token"], current_user["user_id"], redis)
