from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event


class EventRepository:
    def __init__(self, session: Session) -> None:
        """Initialise le repository avec une session SQLAlchemy."""
        self.session = session

    def list_all(self) -> list[Event]:
        """Retourne tous les événements."""
        stmt = select(Event).order_by(Event.id)
        return list(self.session.scalars(stmt).all())

    def list_without_support(self) -> list[Event]:
        """Retourne les événements sans support assigné."""
        stmt = (
            select(Event).where(Event.support_contact_id.is_(None)).order_by(Event.id)
        )
        return list(self.session.scalars(stmt).all())

    def list_assigned_to(self, employee_id: int) -> list[Event]:
        """Retourne les événements assignés à un employé (support_contact_id = employee_id)."""
        stmt = (
            select(Event)
            .where(Event.support_contact_id == employee_id)
            .order_by(Event.id)
        )
        return list(self.session.scalars(stmt).all())

    def add(self, event: Event) -> Event:
        """Ajoute un événement en base."""
        self.session.add(event)
        self.session.flush()
        return event

    def get_by_id(self, event_id: int) -> Event | None:
        """Retourne un événement par son id."""
        stmt = select(Event).where(Event.id == event_id)
        return self.session.scalars(stmt).first()
