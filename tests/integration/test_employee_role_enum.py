import pytest
from sqlalchemy.exc import DataError, IntegrityError, StatementError

from app.models.employee import Employee


def test_employee_role_enum_rejects_invalid_value(db_session):
    """Vérifie que role rejette une valeur hors Enum."""
    employee = Employee(
        first_name="Bad",
        last_name="Role",
        email="bad.role@test.com",
        role="INVALID_ROLE",
        password_hash="hash",
    )

    db_session.add(employee)

    with pytest.raises((StatementError, DataError, IntegrityError)):
        db_session.flush()
