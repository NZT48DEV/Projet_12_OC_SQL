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

    def add(self, client: Client) -> Client:
        self.session.add(client)
        self.session.flush()
        return client

    def get_by_id(self, client_id: int) -> Client | None:
        stmt = select(Client).where(Client.id == client_id)
        return self.session.scalars(stmt).first()

    def get_by_email(self, email: str) -> Client | None:
        stmt = select(Client).where(Client.email == email)
        return self.session.scalars(stmt).first()
