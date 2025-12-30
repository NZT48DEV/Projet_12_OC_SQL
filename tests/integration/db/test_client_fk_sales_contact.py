import pytest
from sqlalchemy.exc import IntegrityError

from app.models.client import Client


def test_client_sales_contact_fk_enforced(db_session):
    """Vérifie que la FK sales_contact_id rejette un employé inexistant."""
    client = Client(
        first_name="Invalid",
        last_name="client",
        email="invalid@test.com",
        sales_contact_id=99999,  # employee inexistant
    )

    db_session.add(client)

    with pytest.raises(IntegrityError):
        db_session.flush()
