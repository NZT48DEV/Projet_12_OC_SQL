from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.client import Client
from app.models.employee import Employee


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # --- Relations ---
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False,
    )
    client: Mapped["Client"] = relationship(
        "Client",
        lazy="joined",
    )

    sales_contact_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
    )
    sales_contact: Mapped["Employee"] = relationship(
        "Employee",
        lazy="joined",
    )

    # --- Données métier ---
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    amount_due: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    is_signed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # --- Timestamps ---
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        onupdate=lambda: datetime.now(timezone.utc),
    )
