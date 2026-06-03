from datetime import datetime, timezone

from fastapi import status
from fastapi.exceptions import HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories import user as user_repo
from app.schemas.auth import TokenResponse
from app.schemas.user import UserResponse


async def register_user(db: AsyncSession, data: dict) -> UserResponse:
    """Зарегистрировать нового пользователя

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        data (dict): Словарь с полями email и password

    Returns:
        UserResponse: Данные созданного пользователя

    Raises:
        HTTPException: Если email уже занят
    """
    user = await user_repo.get_user_by_email(db, data["email"])
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken"
        )
    created_user = await user_repo.create_user(
        db, {"email": data["email"], "password_hash": hash_password(data["password"])}
    )
    return UserResponse(
        id=created_user.id,
        email=created_user.email,
        is_active=created_user.is_active,
        created_at=created_user.created_at,
        roles=[role.name for role in created_user.roles],
    )


async def login_user(db: AsyncSession, data: dict, redis: Redis) -> TokenResponse:
    """Аутентифицировать пользователя

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        data (dict): Словарь с полями email и password
        redis (Redis): Клиент Redis для сохранения refresh токена

    Returns:
        TokenResponse: Пара access и refresh токенов

    Raises:
        HTTPException: Если email или пароль неверные, или пользователь неактивен
    """
    user = await user_repo.get_user_by_email(db, data["email"])
    if (
        not user
        or not user.is_active
        or not verify_password(data["password"], user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email or password incorrect",
        )
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    await redis.set(
        f"refresh_token:{user.id}",
        refresh_token,
        ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_tokens(refresh_token: str, redis: Redis) -> TokenResponse:
    """Обновить пару токенов по refresh_token

    Args:
        refresh_token (str): JWT refresh токен
        redis (Redis): Клиент Redis для проверки и обновления refresh токена

    Returns:
        TokenResponse: Новая пара access и refresh токенов

    Raises:
        HTTPException: Если refresh токен невалидный, истёк или отозван
    """
    decoded_token = decode_token(refresh_token)
    if not decoded_token or decoded_token.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    user_id = decoded_token.get("sub")
    stored_token = await redis.get(f"refresh_token:{user_id}")

    if not stored_token or stored_token != refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or invalid",
        )
    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})

    await redis.set(
        f"refresh_token:{user_id}",
        new_refresh,
        ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


async def logout(access_token: str, user_id: str, redis: Redis) -> bool:
    """Выполнить выход пользователя (инвалидировать токены)

    Args:
        access_token (str): JWT access токен (добавляется в blacklist)
        user_id (str): Идентификатор пользователя
        redis (Redis): Клиент Redis для blacklist и удаления refresh токена

    Returns:
        bool: True
    """
    if decoded_token := decode_token(access_token):
        exp = decoded_token.get("exp")
        ttl = exp - datetime.now(timezone.utc).timestamp()
        if ttl > 0:
            await redis.set(f"blacklist:{access_token}", user_id, ex=int(ttl))
    await redis.delete(f"refresh_token:{user_id}")
    return True
