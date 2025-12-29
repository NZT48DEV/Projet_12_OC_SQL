from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository


class PermissionDeniedError(Exception):
    """Accès interdit (règle métier)."""


class ValidationError(Exception):
    """Données invalides."""


class NotFoundError(Exception):
    """Entité introuvable."""


def list_contracts(session: Session, current_employee: Employee):
    repo = ContractRepository(session)
    return repo.list_all()


def create_contract(
    session: Session,
    current_employee: Employee,
    *,
    client_id: int,
    total_amount: Decimal,
    amount_due: Decimal,
    is_signed: bool = False,
) -> Contract:
    """
    CREATE Contract

    Règles métier :
    - Seuls ROLE.SALES et ROLE.MANAGEMENT peuvent créer un contrat
    - Le client doit exister
    - sales_contact_id = client.sales_contact_id
    - amount_due <= total_amount
    """
    if current_employee.role not in {Role.SALES, Role.MANAGEMENT}:
        raise PermissionDeniedError(
            "Seuls les commerciaux et les managers peuvent créer un contrat."
        )

    if total_amount <= 0:
        raise ValidationError("Le montant total doit être supérieur à 0.")
    if amount_due < 0:
        raise ValidationError("Le montant restant ne peut pas être négatif.")
    if amount_due > total_amount:
        raise ValidationError("Le montant restant ne peut pas dépasser le total.")

    client_repo = ClientRepository(session)
    client = client_repo.get_by_id(client_id)
    if client is None:
        raise NotFoundError("Client introuvable.")

    contract = Contract(
        client_id=client.id,
        sales_contact_id=client.sales_contact_id,
        total_amount=total_amount,
        amount_due=amount_due,
        is_signed=is_signed,
    )

    repo = ContractRepository(session)
    repo.add(contract)
    session.commit()

    return contract


def sign_contract(
    session: Session,
    current_employee: Employee,
    *,
    contract_id: int,
) -> Contract:
    """
    SIGN Contract

    Règles métier :
    - Seul ROLE.MANAGEMENT peut signer un contrat
    - Le contrat doit exister
    - Si déjà signé -> erreur
    """
    if current_employee.role != Role.MANAGEMENT:
        raise PermissionDeniedError("Seuls les managers peuvent signer un contrat.")

    repo = ContractRepository(session)
    contract = repo.get_by_id(contract_id)
    if contract is None:
        raise NotFoundError("Contrat introuvable.")

    if contract.is_signed:
        raise ValidationError("Le contrat est déjà signé.")

    contract.is_signed = True
    session.commit()

    return contract
