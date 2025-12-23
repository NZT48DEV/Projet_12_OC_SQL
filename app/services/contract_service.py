from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.contract_repository import ContractRepository


def list_contracts(session: Session, current_employee: Employee) -> list:
    """
    Retourne la liste des contrats.
    Pré-requis: utilisateur authentifié (current_employee déjà résolu côté CLI).
    """
    repo = ContractRepository(session)
    return repo.list_all()
