from collections.abc import Mapping
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.sql.schema import Table

from app.models.client import Client


def test_clients_table_exists(tables: Mapping[str, Table]):
    """Vérifie que la table 'clients' est bien déclarée dans la metadata."""
    assert "clients" in tables


def test_clients_columns(clients_table: Table):
    """Vérifie colonnes, NULL/NOT NULL et types principaux de la table clients."""
    cols = clients_table.c

    assert set(cols.keys()) >= {
        "id",
        "full_name",
        "email",
        "phone",
        "company_name",
        "sales_contact_id",
        "created_at",
    }

    assert cols.full_name.nullable is False
    assert cols.email.nullable is False
    assert cols.sales_contact_id.nullable is False
    assert cols.created_at.nullable is False

    assert isinstance(cols.full_name.type, String)
    assert isinstance(cols.email.type, String)
    assert isinstance(cols.created_at.type, DateTime)


def test_clients_email_unique_constraint_named(clients_table: Table):
    """Vérifie la présence de la contrainte UNIQUE nommée uq_clients_email."""
    assert "uq_clients_email" in {c.name for c in clients_table.constraints}


def test_clients_sales_contact_fk(clients_table: Table):
    """Vérifie la FK clients.sales_contact_id -> employees.id."""
    fks = list(clients_table.foreign_key_constraints)
    assert any(
        fk.referred_table.name == "employees"
        and [col.name for col in fk.columns] == ["sales_contact_id"]
        for fk in fks
    )


def test_client_instance_creation():
    """Vérifie qu'une instance Client se crée avec les champs attendus."""
    client = Client(
        full_name="ABC Corp",
        email="contact@abc.test",
        phone="0600000000",
        company_name="ABC",
        sales_contact_id=1,
        created_at=datetime.now(timezone.utc),
    )

    assert client.full_name == "ABC Corp"
    assert client.email == "contact@abc.test"
    assert client.phone == "0600000000"
    assert client.company_name == "ABC"
    assert client.sales_contact_id == 1
