from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event


class EventRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Event]:
        stmt = select(Event).order_by(Event.id)
        return list(self.session.scalars(stmt).all())

    def add(self, event: Event) -> Event:
        self.session.add(event)
        self.session.flush()
        return event

    def get_by_id(self, event_id: int) -> Event | None:
        stmt = select(Event).where(Event.id == event_id)
        return self.session.scalars(stmt).first()
