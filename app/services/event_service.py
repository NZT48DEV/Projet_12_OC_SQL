from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.employee import Employee, Role
from app.models.event import Event
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository


class PermissionDeniedError(Exception):
    """Accès interdit (règle métier)."""


class ValidationError(Exception):
    """Données invalides."""


class NotFoundError(Exception):
    """Entité introuvable."""


def list_events(session: Session, current_employee: Employee) -> list[Event]:
    """
    Liste tous les événements.
    Authentification requise (gérée côté CLI).
    """
    repo = EventRepository(session)
    return repo.list_all()


def create_event(
    session: Session,
    current_employee: Employee,
    *,
    client_id: int,
    contract_id: int,
    start_date: datetime,
    end_date: datetime,
    location: str,
    attendees: int,
    notes: str | None = None,
) -> Event:
    """
    CREATE Event

    Règles métier :
    - SALES uniquement
    - client appartenant au commercial
    - contrat signé obligatoire
    - contrat appartenant au client
    """
    if current_employee.role != Role.SALES:
        raise PermissionDeniedError("Seuls les commerciaux peuvent créer un événement.")

    if start_date >= end_date:
        raise ValidationError("La date de début doit être antérieure à la date de fin.")
    if attendees < 0:
        raise ValidationError("Le nombre de participants ne peut pas être négatif.")
    if not location or not location.strip():
        raise ValidationError("Le lieu est requis.")

    client_repo = ClientRepository(session)
    client = client_repo.get_by_id(client_id)
    if client is None:
        raise NotFoundError("Client introuvable.")

    if client.sales_contact_id != current_employee.id:
        raise PermissionDeniedError(
            "Vous ne pouvez créer un événement que pour vos clients."
        )

    contract_repo = ContractRepository(session)
    contract = contract_repo.get_by_id(contract_id)
    if contract is None:
        raise NotFoundError("Contrat introuvable.")

    if contract.client_id != client.id:
        raise ValidationError("Le contrat ne correspond pas au client.")

    if not contract.is_signed:
        raise ValidationError("Impossible de créer un événement : contrat non signé.")

    event = Event(
        client_id=client.id,
        contract_id=contract.id,
        support_contact_id=None,  # assigné plus tard
        start_date=start_date,
        end_date=end_date,
        location=location.strip(),
        attendees=attendees,
        notes=(notes.strip() if notes else None),
    )

    repo = EventRepository(session)
    repo.add(event)
    session.commit()

    return event
