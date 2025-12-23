from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract


class ContractRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Contract]:
        stmt = select(Contract).order_by(Contract.id)
        return list(self.session.scalars(stmt).all())
