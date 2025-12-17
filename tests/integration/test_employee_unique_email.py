import pytest
from sqlalchemy.exc import IntegrityError

from app.models.employee import Employee, Role


def test_employee_email_unique_constraint(db_session):
    """Vérifie que l'email employé est unique (contrainte UNIQUE)."""
    employee1 = Employee(
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@test.com",
        role=Role.SALES,
        password_hash="hash",
    )
    employee2 = Employee(
        first_name="Jean2",
        last_name="Dupont2",
        email="jean.dupont@test.com",  # même email
        role=Role.SALES,
        password_hash="hash",
    )

    db_session.add(employee1)
    db_session.flush()

    db_session.add(employee2)
    with pytest.raises(IntegrityError):
        db_session.flush()
