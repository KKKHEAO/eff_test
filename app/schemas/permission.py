from pydantic import BaseModel


class PermissionCreate(BaseModel):
    resource: str
    action: str


class PermissionResponse(BaseModel):
    id: int
    resource: str
    action: str

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    permission_ids: list[int] = []


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    permissions: list[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleAssign(BaseModel):
    user_id: str
    role_id: int
