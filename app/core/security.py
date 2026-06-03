from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Захэшировать пароль

    Args:
        password (str): Пароль в открытом виде

    Returns:
        str: Хэшированный пароль
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль

    Args:
        plain_password (str): Пароль в открытом виде
        hashed_password (str): Хэшированный пароль из БД

    Returns:
        bool: Совпадает ли пароль
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Создать access token (короткоживущий)

    Args:
        data (dict): Данные для payload токена (например, {"sub": user_id})

    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Создать refresh token (долгоживущий)

    Args:
        data (dict): Данные для payload токена (например, {"sub": user_id})

    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Декодировать и проверить JWT токен

    Args:
        token (str): JWT токен

    Returns:
        dict | None: Payload токена или None, если токен невалидный
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.JWTError:
        return None
