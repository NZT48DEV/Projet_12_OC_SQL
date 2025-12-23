from app.models.client import Client
from app.models.employee import Employee


def test_client_created_at_is_auto_set(db_session):
    """Vérifie que created_at est renseigné lors de la persistance d'un Client."""
    employee = Employee(
        first_name="Jane",
        last_name="Darc",
        email="jane.client.created_at@test.com",
        role="SALES",
        password_hash="hash",
    )
    db_session.add(employee)
    db_session.flush()

    client = Client(
        first_name="Client",
        last_name="ABC",
        email="client.abc.created_at@test.com",
        sales_contact_id=employee.id,
    )
    db_session.add(client)
    db_session.flush()

    db_session.refresh(client)
    assert client.created_at is not None
