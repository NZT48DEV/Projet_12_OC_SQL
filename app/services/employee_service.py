from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.authorization import AuthorizationError, require_role
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.models.event import Event
from app.repositories.employee_repository import EmployeeRepository


class NotFoundError(Exception):
    """Ressource introuvable."""


class PermissionDeniedError(Exception):
    """Accès refusé (permissions insuffisantes)."""


class ValidationError(Exception):
    """Données invalides / action impossible."""


def deactivate_employee(
    session: Session,
    current_employee: Employee,
    employee_id: int,
) -> Employee:
    """
    Désactive un employé (soft delete).
    - MANAGEMENT uniquement
    - interdit de se désactiver soi-même
    - si déjà désactivé => ValidationError
    """
    try:
        require_role(current_employee.role, allowed={Role.MANAGEMENT})
    except AuthorizationError as exc:
        raise PermissionDeniedError(str(exc)) from exc

    if current_employee.id == employee_id:
        raise ValidationError("Impossible de se désactiver soi-même.")

    repo = EmployeeRepository(session)
    employee = repo.get_by_id(employee_id)
    if employee is None:
        raise NotFoundError("Employé introuvable.")

    if not employee.is_active:
        raise ValidationError("Employé déjà désactivé.")

    employee.is_active = False
    employee.deactivated_at = datetime.now(timezone.utc)
    employee.reactivated_at = None

    session.commit()
    session.refresh(employee)
    return employee


def reactivate_employee(
    session: Session,
    current_employee: Employee,
    employee_id: int,
) -> Employee:
    """
    Réactive un employé précédemment désactivé.
    - MANAGEMENT uniquement
    - l'employé doit exister et être désactivé
    """
    try:
        require_role(current_employee.role, allowed={Role.MANAGEMENT})
    except AuthorizationError as exc:
        raise PermissionDeniedError(str(exc)) from exc

    repo = EmployeeRepository(session)
    employee = repo.get_by_id(employee_id)
    if employee is None:
        raise NotFoundError("Employé introuvable.")

    if employee.is_active:
        raise ValidationError("Employé déjà actif.")

    employee.is_active = True
    employee.deactivated_at = None
    employee.reactivated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(employee)
    return employee


def hard_delete_employee(
    session: Session,
    current_employee: Employee,
    employee_id: int,
    *,
    confirm_employee_id: int,
) -> None:
    """
    Supprime définitivement un employé (hard delete).
    - MANAGEMENT uniquement
    - double confirmation : confirm_employee_id doit matcher employee_id
    - interdit de se supprimer soi-même
    - interdit si l'employé est référencé (clients/contrats/événements)
    """
    try:
        require_role(current_employee.role, allowed={Role.MANAGEMENT})
    except AuthorizationError as exc:
        raise PermissionDeniedError(str(exc)) from exc

    if employee_id != confirm_employee_id:
        raise ValidationError("Confirmation invalide : l'ID ne correspond pas.")

    if current_employee.id == employee_id:
        raise ValidationError("Impossible de se supprimer soi-même.")

    repo = EmployeeRepository(session)
    employee = repo.get_by_id(employee_id)
    if employee is None:
        raise NotFoundError("Employé introuvable.")

    # Vérifie les références (FK) : bloque si > 0
    clients_count = (
        session.query(func.count(Client.id))
        .filter(Client.sales_contact_id == employee_id)
        .scalar()
        or 0
    )

    contracts_count = (
        session.query(func.count(Contract.id))
        .filter(Contract.sales_contact_id == employee_id)
        .scalar()
        or 0
    )

    events_count = (
        session.query(func.count(Event.id))
        .filter(Event.support_contact_id == employee_id)
        .scalar()
        or 0
    )

    if clients_count or contracts_count or events_count:
        raise ValidationError(
            "Suppression définitive impossible : employé référencé "
            f"(clients={clients_count}, contrats={contracts_count}, événements={events_count})."
        )

    session.delete(employee)
    session.commit()
