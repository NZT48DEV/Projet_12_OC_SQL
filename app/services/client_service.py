from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.client_repository import ClientRepository


def list_clients(session: Session, current_employee: Employee):
    repo = ClientRepository(session)
    return repo.list_all()
