from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime
    roles: list[str] = []

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None
