from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.employee import Employee, Role
from app.models.event import Event
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.event_repository import EventRepository


class PermissionDeniedError(Exception):
    """Accès interdit (règle métier)."""


class ValidationError(Exception):
    """Données invalides."""


class NotFoundError(Exception):
    """Entité introuvable."""


def list_events(
    session: Session,
    current_employee: Employee,
    *,
    without_support: bool = False,
    assigned_to_me: bool = False,
) -> list[Event]:
    """
    Liste les événements accessibles à l'utilisateur courant.

    :param without_support: si True, retourne uniquement les événements sans support assigné.
    :param assigned_to_me: si True, retourne uniquement les événements assignés à l'utilisateur courant.
    """
    repo = EventRepository(session)

    # Combinaison impossible (un event ne peut pas être "sans support" ET "assigné à moi")
    if without_support and assigned_to_me:
        return []

    if assigned_to_me:
        return repo.list_assigned_to(current_employee.id)

    if without_support:
        return repo.list_without_support()

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


def reassign_event(
    session: Session,
    current_employee: Employee,
    *,
    event_id: int,
    support_contact_id: int,
) -> Event:
    """
    Réassigne le support d'un événement.

    Règles métier :
    - MANAGEMENT uniquement
    - l'événement doit exister
    - l'employé support doit exister, être ROLE.SUPPORT, et être actif
    """
    if current_employee.role != Role.MANAGEMENT:
        raise PermissionDeniedError("Seul le management peut réassigner un événement.")

    repo = EventRepository(session)
    event = repo.get_by_id(event_id)
    if event is None:
        raise NotFoundError("Événement introuvable.")

    emp_repo = EmployeeRepository(session)
    support = emp_repo.get_by_id(support_contact_id)
    if support is None:
        raise NotFoundError("Employé introuvable.")

    if support.role != Role.SUPPORT:
        raise ValidationError("L'employé assigné doit avoir le rôle SUPPORT.")

    if not support.is_active:
        raise ValidationError("Impossible d'assigner un employé désactivé.")

    event.support_contact_id = support_contact_id
    session.commit()
    return event


def unassign_event_support(
    session: Session,
    current_employee: Employee,
    *,
    event_id: int,
) -> Event:
    """Retire le support assigné à un événement."""
    if current_employee.role != Role.MANAGEMENT:
        raise PermissionDeniedError("Seul le management peut retirer un support.")

    repo = EventRepository(session)
    event = repo.get_by_id(event_id)
    if event is None:
        raise NotFoundError("Événement introuvable.")

    event.support_contact_id = None
    session.commit()
    return event


def update_event(
    session: Session,
    current_employee: Employee,
    *,
    event_id: int,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    location: str | None = None,
    attendees: int | None = None,
    notes: str | None = None,
    support_contact_id: int | None = None,
) -> Event:
    """
    UPDATE Event

    Règles métier :
    - MANAGEMENT : peut modifier tous les événements
    - SUPPORT : peut modifier uniquement les événements qui lui sont assignés
    - SALES : interdit
    - start_date < end_date
    - attendees >= 0
    - location non vide si fourni
    - assignation support : MANAGEMENT uniquement (via reassign_event)
    """
    if current_employee.role == Role.SALES:
        raise PermissionDeniedError(
            "Les commerciaux ne peuvent pas modifier un événement."
        )

    repo = EventRepository(session)
    event = repo.get_by_id(event_id)
    if event is None:
        raise NotFoundError("Événement introuvable.")

    if current_employee.role == Role.SUPPORT:
        if event.support_contact_id != current_employee.id:
            raise PermissionDeniedError(
                "Vous ne pouvez modifier que les événements qui vous sont assignés."
            )

    # Si on veut assigner/réassigner un support depuis update_event :
    # on délègue à reassign_event pour éviter la duplication des règles.
    if support_contact_id is not None:
        return reassign_event(
            session=session,
            current_employee=current_employee,
            event_id=event_id,
            support_contact_id=support_contact_id,
        )

    # Validations + valeurs finales
    final_start = start_date if start_date is not None else event.start_date
    final_end = end_date if end_date is not None else event.end_date

    if final_start >= final_end:
        raise ValidationError("La date de début doit être antérieure à la date de fin.")

    if attendees is not None and attendees < 0:
        raise ValidationError("Le nombre de participants ne peut pas être négatif.")

    if location is not None and not location.strip():
        raise ValidationError("Le lieu est requis.")

    # Application des modifications
    if start_date is not None:
        event.start_date = start_date
    if end_date is not None:
        event.end_date = end_date
    if location is not None:
        event.location = location.strip()
    if attendees is not None:
        event.attendees = attendees
    if notes is not None:
        event.notes = notes.strip() or None

    session.commit()
    return event
