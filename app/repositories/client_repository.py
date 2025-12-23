from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.client import Client


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Client]:
        stmt = select(Client).order_by(Client.id)
        return list(self.session.scalars(stmt).all())
