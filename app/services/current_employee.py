from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.session_store import clear_session, load_current_employee_id
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository


class NotAuthenticatedError(Exception):
    """Utilisateur non authentifié."""


def get_current_employee(session: Session) -> Employee:
    employee_id = load_current_employee_id()
    if employee_id is None:
        raise NotAuthenticatedError("Non authentifié.")

    repo = EmployeeRepository(session)
    employee = repo.get_by_id(employee_id)

    if employee is None:
        clear_session()
        raise NotAuthenticatedError("Session invalide.")

    return employee
