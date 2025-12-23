import pytest
from sqlalchemy.exc import IntegrityError

from app.models.client import Client
from app.models.employee import Employee


def test_client_email_unique_constraint(db_session):
    """Vérifie que l'email client est unique (contrainte UNIQUE)."""
    employee = Employee(
        first_name="Jean",
        last_name="Louis",
        email="jean.louis@test.com",
        role="SALES",
        password_hash="hash",
    )
    db_session.add(employee)
    db_session.flush()

    client1 = Client(
        first_name="Client",
        last_name="ABC",
        email="contact@abc.test",
        sales_contact_id=employee.id,
    )

    client2 = Client(
        first_name="Client",
        last_name="ABC 2",
        email="contact@abc.test",
        sales_contact_id=employee.id,
    )

    db_session.add(client1)
    db_session.flush()

    db_session.add(client2)

    with pytest.raises(IntegrityError):
        db_session.flush()
