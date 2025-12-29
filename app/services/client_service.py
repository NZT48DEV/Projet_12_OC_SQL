from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.employee import Employee, Role
from app.repositories.client_repository import ClientRepository


class PermissionDeniedError(Exception):
    """L'utilisateur n'a pas le droit d'effectuer cette action."""


class ValidationError(Exception):
    """Données invalides côté métier."""


class ClientAlreadyExistsError(Exception):
    """Email déjà utilisé par un autre client."""


def list_clients(session: Session, current_employee: Employee) -> list[Client]:
    repo = ClientRepository(session)
    return repo.list_all()


def create_client(
    session: Session,
    current_employee: Employee,
    *,
    first_name: str,
    last_name: str,
    email: str,
    phone: str | None = None,
    company_name: str | None = None,
) -> Client:
    if current_employee.role != Role.SALES:
        raise PermissionDeniedError("Seuls les commerciaux peuvent créer un client.")

    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    email = (email or "").strip().lower()
    phone = (phone or "").strip() or None
    company_name = (company_name or "").strip() or None

    if not first_name:
        raise ValidationError("Le prénom est requis.")
    if not last_name:
        raise ValidationError("Le nom est requis.")
    if not email:
        raise ValidationError("L'email est requis.")

    repo = ClientRepository(session)

    if repo.get_by_email(email) is not None:
        raise ClientAlreadyExistsError("Un client avec cet email existe déjà.")

    client = Client(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
        sales_contact_id=current_employee.id,
    )

    try:
        repo.add(client)
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise ClientAlreadyExistsError("Un client avec cet email existe déjà.") from exc

    return client
