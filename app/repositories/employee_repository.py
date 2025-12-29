from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    """Accès aux données Employee (requêtes SQLAlchemy)."""

    def __init__(self, session: Session):
        """
        Initialise le repository.
        """
        self.session = session

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.session.get(Employee, employee_id)

    def get_by_email(self, email: str) -> Employee | None:
        return (
            self.session.query(Employee).filter(Employee.email == email).one_or_none()
        )
