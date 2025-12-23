from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.event_repository import EventRepository


def list_events(session: Session, current_employee: Employee) -> list:
    """
    Liste tous les événements.
    Authentification requise (gérée côté CLI).
    """
    repo = EventRepository(session)
    return repo.list_all()
