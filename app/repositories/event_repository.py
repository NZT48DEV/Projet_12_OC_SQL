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
