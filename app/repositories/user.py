from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(db: AsyncSession, data: dict) -> User:
    """Создать пользователя

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        data (dict): Словарь, содержащий пароль в хешированном виде

    Returns:
        User: Созданный пользователь
    """
    user = User(**data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Получить пользователя по id

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        user_id (UUID): Идентификатор пользователя в БД

    Returns:
        User | None: Пользователь
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Получить пользователя по email

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        email (str): email пользователя

    Returns:
        User | None: Пользователь
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[User]:
    """Получить пользователей с пагинацией

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        skip (int): offset для запроса
        limit (int): limit для запроса

    Returns:
        list[User]: Список пользователей
    """
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user_id: UUID, data: dict) -> User | None:
    """Обновить данные пользователя, если он есть

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        user_id (UUID): идентификатор пользователя
        data (dict): обновляемые поля

    Returns:
        User | None: Обновленный пользователь
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    for key, value in data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_by_id(db: AsyncSession, user_id: UUID) -> bool:
    """Удалить пользователя, если он есть

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        user_id (UUID): идентификатор пользователя

    Returns:
        bool: Результат удаления
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True
