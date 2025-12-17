from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Role(PyEnum):
    MANAGEMENT = "MANAGEMENT"
    SALES = "SALES"
    SUPPORT = "SUPPORT"


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (UniqueConstraint("email", name="uq_employees_email"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)

    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
