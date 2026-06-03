from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.models.base import user_roles, role_permissions


async def create_permission(db: AsyncSession, data: dict) -> Permission:
    """Создать разрешение

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        data (dict): Словарь с полями resource и action

    Returns:
        Permission: Созданное разрешение
    """
    permission = Permission(**data)
    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission


async def get_all_permissions(db: AsyncSession) -> list[Permission]:
    """Получить список всех разрешений

    Args:
        db (AsyncSession): Асинхронная сессия для БД

    Returns:
        list[Permission]: Список разрешений
    """
    stmt = select(Permission)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_permission_by_id(db: AsyncSession, perm_id: int) -> Permission | None:
    """Получить разрешение по id

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        perm_id (int): Идентификатор разрешения

    Returns:
        Permission | None: Разрешение
    """
    stmt = select(Permission).where(Permission.id == perm_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_role(db: AsyncSession, data: dict) -> Role:
    """Создать роль

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        data (dict): Словарь с полями name, description и permission_ids

    Returns:
        Role: Созданная роль
    """
    role = Role(**data)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def get_all_roles(db: AsyncSession) -> list[Role]:
    """Получить список всех ролей

    Args:
        db (AsyncSession): Асинхронная сессия для БД

    Returns:
        list[Role]: Список ролей
    """
    stmt = select(Role)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_role_by_id(db: AsyncSession, role_id: int) -> Role | None:
    """Получить роль по id

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        role_id (int): Идентификатор роли

    Returns:
        Role | None: Роль
    """
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def assign_permissions_to_role(
    db: AsyncSession, role_id: int, permission_ids: list[int]
) -> Role | None:
    """Привязать разрешения к роли (сначала удалить старые, потом добавить новые)

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        role_id (int): Идентификатор роли
        permission_ids (list[int]): Список идентификаторов разрешений

    Returns:
        Role | None: Обновленная роль
    """
    await db.execute(
        role_permissions.delete().where(role_permissions.c.role_id == role_id)
    )
    for perm_id in permission_ids:
        await db.execute(
            role_permissions.insert().values(role_id=role_id, permission_id=perm_id)
        )
    await db.commit()
    return await get_role_by_id(db, role_id=role_id)


async def assign_role_to_user(db: AsyncSession, user_id: UUID, role_id: int) -> bool:
    """Назначить роль пользователю

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        user_id (UUID): Идентификатор пользователя
        role_id (int): Идентификатор роли

    Returns:
        bool: Результат назначения
    """
    stmt = user_roles.insert().values(user_id=user_id, role_id=role_id)
    await db.execute(stmt)
    await db.commit()
    return True


async def get_user_permissions(db: AsyncSession, user_id: UUID) -> list[Permission]:
    """Получить все разрешения пользователя через его роли

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        user_id (UUID): Идентификатор пользователя

    Returns:
        list[Permission]: Список разрешений пользователя
    """
    stmt = (
        select(Permission)
        .join(role_permissions, Permission.id == role_permissions.c.permission_id)
        .join(Role, role_permissions.c.role_id == Role.id)
        .join(user_roles, Role.id == user_roles.c.role_id)
        .join(User, user_roles.c.user_id == User.id)
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
