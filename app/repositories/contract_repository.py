from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract


class ContractRepository:
    def __init__(self, session: Session) -> None:
        """Initialise le repository avec une session SQLAlchemy."""
        self.session = session

    def list_all(self) -> list[Contract]:
        """Retourne tous les contrats."""
        return self.list_filtered()

    def list_filtered(
        self, *, unsigned: bool = False, unpaid: bool = False
    ) -> list[Contract]:
        """Retourne les contrats filtrés (non signés / non payés)."""
        stmt = select(Contract)

        if unsigned:
            stmt = stmt.where(Contract.is_signed.is_(False))

        if unpaid:
            stmt = stmt.where(Contract.amount_due > 0)

        stmt = stmt.order_by(Contract.id)
        return list(self.session.scalars(stmt).all())

    def add(self, contract: Contract) -> Contract:
        """Ajoute un contrat en base."""
        self.session.add(contract)
        self.session.flush()
        return contract

    def get_by_id(self, contract_id: int) -> Contract | None:
        """Retourne un contrat par son id."""
        stmt = select(Contract).where(Contract.id == contract_id)
        return self.session.scalars(stmt).first()
