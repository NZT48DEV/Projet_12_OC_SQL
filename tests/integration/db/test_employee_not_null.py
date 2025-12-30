import pytest
from sqlalchemy.exc import IntegrityError

from app.models.employee import Employee, Role


@pytest.mark.parametrize(
    "field",
    ["first_name", "last_name", "email", "role", "password_hash"],
)
def test_employee_required_fields_not_null(db_session, field):
    """Vérifie que les champs essentiels d'Employee sont NOT NULL."""
    data = dict(
        first_name="Jane",
        last_name="Darc",
        email="jane.darc@test.com",
        role=Role.SALES,
        password_hash="hash",
    )
    data[field] = None

    employee = Employee(**data)
    db_session.add(employee)

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_employee_created_at_is_auto_set(db_session):
    """Vérifie que created_at est automatiquement renseigné par défaut."""
    employee = Employee(
        first_name="Jane",
        last_name="Darc",
        email="jane.created_at@test.com",
        role=Role.SALES,
        password_hash="hash",
    )

    db_session.add(employee)
    db_session.flush()

    assert employee.created_at is not None
    assert employee.created_at.tzinfo is not None
