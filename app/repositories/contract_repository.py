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

    def add(self, contract: Contract) -> Contract:
        self.session.add(contract)
        self.session.flush()
        return contract

    def get_by_id(self, contract_id: int) -> Contract | None:
        stmt = select(Contract).where(Contract.id == contract_id)
        return self.session.scalars(stmt).first()
