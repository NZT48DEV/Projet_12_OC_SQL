from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    """Accès aux données Employee (requêtes SQLAlchemy)."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: session SQLAlchemy utilisée pour exécuter les requêtes.
        """
        self.session = session

    def get_by_id(self, employee_id: int) -> Employee | None:
        """
        Récupère un employé par son identifiant.

        Args:
            employee_id: identifiant de l'employé.

        Returns:
            L'employé si trouvé, sinon None.
        """
        return self.session.get(Employee, employee_id)

    def get_by_email(self, email: str) -> Employee | None:
        """
        Récupère un employé par son email.

        Args:
            email: email de l'employé.

        Returns:
            L'employé si trouvé, sinon None.
        """
        return (
            self.session.query(Employee).filter(Employee.email == email).one_or_none()
        )
