from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from app.core.security import decode_token
from app.db.session import get_redis

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis: Redis = Depends(get_redis),
):
    """Проверить access_token, извлечь user_id, проверить blacklist

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer токен из заголовка Authorization
        redis (Redis): Клиент Redis для проверки blacklist

    Returns:
        dict: Словарь с ключами user_id и token

    Raises:
        HTTPException: Если токен невалидный или отозван
    """
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        )

    # Проверка blacklist
    blacklisted = await redis.get(f"blacklist:{token}")
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
        )

    return {"user_id": payload.get("sub"), "token": token}
