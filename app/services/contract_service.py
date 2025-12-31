from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.employee_repository import EmployeeRepository


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


def update_contract(
    session: Session,
    current_employee: Employee,
    *,
    contract_id: int,
    total_amount: Decimal | None = None,
    amount_due: Decimal | None = None,
) -> Contract:
    """
    UPDATE Contract

    Règles métier :
    - ROLE.SALES et ROLE.MANAGEMENT autorisés
    - Un SALES ne peut modifier que ses contrats (sales_contact_id)
    - total_amount > 0 si fourni
    - amount_due >= 0 si fourni
    - amount_due <= total_amount (en tenant compte des valeurs finales)
    - La signature n'est pas modifiable ici (utiliser `sign_contract`)
    """
    if current_employee.role not in {Role.SALES, Role.MANAGEMENT}:
        raise PermissionDeniedError(
            "Seuls les commerciaux et les managers peuvent modifier un contrat."
        )

    repo = ContractRepository(session)
    contract = repo.get_by_id(contract_id)
    if contract is None:
        raise NotFoundError("Contrat introuvable.")

    if (
        current_employee.role == Role.SALES
        and contract.sales_contact_id != current_employee.id
    ):
        raise PermissionDeniedError(
            "Un commercial ne peut modifier que ses propres contrats."
        )

    # Nettoyage/validation des valeurs fournies
    if total_amount is not None and total_amount <= 0:
        raise ValidationError("Le montant total doit être supérieur à 0.")

    if amount_due is not None and amount_due < 0:
        raise ValidationError("Le montant restant ne peut pas être négatif.")

    # Calcul des valeurs finales pour vérifier la cohérence
    final_total = total_amount if total_amount is not None else contract.total_amount
    final_due = amount_due if amount_due is not None else contract.amount_due

    if final_due > final_total:
        raise ValidationError("Le montant restant ne peut pas dépasser le total.")

    # Application des modifications
    if total_amount is not None:
        contract.total_amount = total_amount
    if amount_due is not None:
        contract.amount_due = amount_due

    session.commit()
    return contract


def reassign_contract(
    session: Session,
    current_employee: Employee,
    *,
    contract_id: int,
    new_sales_contact_id: int,
) -> Contract:
    """
    Réassigne un contrat à un autre commercial.

    Règles métier :
    - MANAGEMENT : peut réassigner n'importe quel contrat
    - SALES : peut réassigner uniquement SES contrats (sales_contact_id == current_employee.id)
    - SUPPORT : interdit
    - Le nouvel employé doit exister, être ROLE.SALES et être actif
    """
    if current_employee.role not in {Role.SALES, Role.MANAGEMENT}:
        raise PermissionDeniedError(
            "Seuls les commerciaux et les managers peuvent réassigner un contrat."
        )

    repo = ContractRepository(session)
    contract = repo.get_by_id(contract_id)
    if contract is None:
        raise NotFoundError("Contrat introuvable.")

    if (
        current_employee.role == Role.SALES
        and contract.sales_contact_id != current_employee.id
    ):
        raise PermissionDeniedError(
            "Un commercial ne peut réassigner que ses propres contrats."
        )

    emp_repo = EmployeeRepository(session)
    new_sales = emp_repo.get_by_id(new_sales_contact_id)
    if new_sales is None:
        raise NotFoundError("Employé introuvable.")
    if new_sales.role != Role.SALES:
        raise ValidationError("L'employé assigné doit avoir le rôle SALES.")
    if not new_sales.is_active:
        raise ValidationError("Impossible d'assigner un employé désactivé.")

    contract.sales_contact_id = new_sales_contact_id
    session.commit()
    return contract
