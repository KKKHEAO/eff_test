from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import permission as permission_repo


async def has_permission(
    db: AsyncSession,
    user_id: str,
    required_resource: str,
    required_action: str,
) -> bool:
    """Проверить, есть ли у пользователя право на resource + action

    Args:
        db (AsyncSession): Асинхронная сессия для БД
        user_id (str): Идентификатор пользователя
        required_resource (str): Название ресурса (например, "users", "reports")
        required_action (str): Название действия (например, "create", "read")

    Returns:
        bool: Есть ли у пользователя данное разрешение
    """
    permissions = await permission_repo.get_user_permissions(db, UUID(user_id))
    for perm in permissions:
        if perm.resource == required_resource and perm.action == required_action:
            return True
    return False
