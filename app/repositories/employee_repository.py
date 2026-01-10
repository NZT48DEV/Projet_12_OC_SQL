from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee, Role


class EmployeeRepository:
    """Accès aux données Employee (requêtes SQLAlchemy)."""

    def __init__(self, session: Session) -> None:
        """Initialise le repository avec une session SQLAlchemy."""
        self.session = session

    def get_by_id(self, employee_id: int) -> Employee | None:
        """Retourne un employé par son id."""
        return self.session.get(Employee, employee_id)

    def get_by_email(self, email: str) -> Employee | None:
        """Retourne un employé par son email."""
        return (
            self.session.query(Employee).filter(Employee.email == email).one_or_none()
        )

    def list_all(self) -> list[Employee]:
        """Retourne tous les employés."""
        return self.session.query(Employee).order_by(Employee.id).all()

    def list_by_role(self, role: Role) -> list[Employee]:
        """Retourne les employés filtrés par rôle."""
        return (
            self.session.query(Employee)
            .filter(Employee.role == role)
            .order_by(Employee.id)
            .all()
        )
