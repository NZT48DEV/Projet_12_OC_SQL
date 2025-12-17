from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    """DAL Employee : accès DB isolé de la logique métier."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> Employee | None:
        """Retourne un employé par email, ou None."""
        return (
            self.session.query(Employee).filter(Employee.email == email).one_or_none()
        )
