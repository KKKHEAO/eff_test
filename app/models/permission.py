from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, role_permissions

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(50))

    roles: Mapped[list["Role"]] = relationship(  # noqa: F821 # type: ignore
        secondary=role_permissions,
        back_populates="permissions",
    )

    __table_args__ = (UniqueConstraint("resource", "action"),)