from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, user_roles, role_permissions


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship(  # noqa: F821 # type: ignore
        secondary=user_roles,
        back_populates="roles",
    )
    permissions: Mapped[list["Permission"]] = relationship(  # noqa: F821 # type: ignore
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
