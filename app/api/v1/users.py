from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.repositories import permission as permission_repo
from app.repositories import user as user_repo
from app.schemas.permission import RoleAssign
from app.schemas.user import UserResponse
from app.services.authorization import has_permission

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Получить список пользователей с пагинацией

    Args:
        skip (int): Количество пропущенных записей
        limit (int): Максимальное количество записей

    Returns:
        list[UserResponse]: Список пользователей
    """
    if not await has_permission(db, current_user["user_id"], "users", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    users = await user_repo.get_all_users(db, skip=skip, limit=limit)
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            is_active=u.is_active,
            created_at=u.created_at,
            roles=[r.name for r in u.roles],
        )
        for u in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Получить пользователя по ID

    Args:
        user_id (UUID): Идентификатор пользователя

    Returns:
        UserResponse: Данные пользователя

    Raises:
        HTTPException: Если пользователь не найден
    """
    if not await has_permission(db, current_user["user_id"], "users", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    user = await user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        roles=[r.name for r in user.roles],
    )


@router.post("/{user_id}/roles", status_code=status.HTTP_204_NO_CONTENT)
async def assign_role(
    user_id: UUID,
    body: RoleAssign,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Назначить роль пользователю

    Args:
        user_id (UUID): Идентификатор пользователя
        body (RoleAssign): Идентификатор роли
    """
    if not await has_permission(db, current_user["user_id"], "roles", "assign"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    await permission_repo.assign_role_to_user(db, user_id, body.role_id)
