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


def update_client(
    session: Session,
    current_employee: Employee,
    *,
    client_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    company_name: str | None = None,
) -> Client:
    repo = ClientRepository(session)
    client = repo.get_by_id(client_id)

    if client is None:
        raise ValidationError("Client introuvable.")

    if current_employee.role == Role.SUPPORT:
        raise PermissionDeniedError("Accès interdit.")

    if (
        current_employee.role == Role.SALES
        and client.sales_contact_id != current_employee.id
    ):
        raise PermissionDeniedError(
            "Un commercial ne peut modifier que ses propres clients."
        )

    if first_name is not None:
        first_name = first_name.strip()
        if not first_name:
            raise ValidationError("Le prénom ne peut pas être vide.")
        client.first_name = first_name

    if last_name is not None:
        last_name = last_name.strip()
        if not last_name:
            raise ValidationError("Le nom ne peut pas être vide.")
        client.last_name = last_name

    if email is not None:
        email = email.strip().lower()
        if not email:
            raise ValidationError("L'email ne peut pas être vide.")
        existing = repo.get_by_email(email)
        if existing and existing.id != client.id:
            raise ClientAlreadyExistsError("Un client avec cet email existe déjà.")
        client.email = email

    if phone is not None:
        client.phone = phone.strip() or None

    if company_name is not None:
        client.company_name = company_name.strip() or None

    session.commit()
    return client
