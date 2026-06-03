from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.repositories import permission as permission_repo
from app.schemas.permission import (
    PermissionCreate,
    PermissionResponse,
    RoleCreate,
    RoleResponse,
)
from app.services.authorization import has_permission

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/permissions", response_model=list[PermissionResponse])
async def get_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not await has_permission(db, current_user["user_id"], "permissions", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return await permission_repo.get_all_permissions(db)


@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    body: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not await has_permission(db, current_user["user_id"], "permissions", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return await permission_repo.create_permission(db, body.model_dump())


@router.get("/roles", response_model=list[RoleResponse])
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not await has_permission(db, current_user["user_id"], "roles", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return await permission_repo.get_all_roles(db)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not await has_permission(db, current_user["user_id"], "roles", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    role = await permission_repo.create_role(
        db, {"name": body.name, "description": body.description}
    )
    if body.permission_ids:
        role = await permission_repo.assign_permissions_to_role(
            db, role.id, body.permission_ids
        )
    return role


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not await has_permission(db, current_user["user_id"], "roles", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    role = await permission_repo.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.put("/roles/{role_id}/permissions", response_model=RoleResponse)
async def update_role_permissions(
    role_id: int,
    permission_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not await has_permission(db, current_user["user_id"], "roles", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    role = await permission_repo.assign_permissions_to_role(db, role_id, permission_ids)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role
