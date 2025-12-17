from collections.abc import Mapping
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric
from sqlalchemy.sql.schema import Table

from app.models.contract import Contract


def test_contracts_table_exists(tables: Mapping[str, Table]):
    """Vérifie que la table 'contracts' est bien déclarée dans la metadata."""
    assert "contracts" in tables


def test_contracts_columns(contracts_table: Table):
    """Vérifie colonnes, NULL/NOT NULL et types principaux de la table contracts."""
    cols = contracts_table.c

    assert set(cols.keys()) >= {
        "id",
        "client_id",
        "sales_contact_id",
        "total_amount",
        "amount_due",
        "is_signed",
        "created_at",
    }

    assert cols.client_id.nullable is False
    assert cols.sales_contact_id.nullable is False
    assert cols.total_amount.nullable is False
    assert cols.amount_due.nullable is False
    assert cols.is_signed.nullable is False
    assert cols.created_at.nullable is False

    assert isinstance(cols.total_amount.type, Numeric)
    assert isinstance(cols.amount_due.type, Numeric)
    assert isinstance(cols.is_signed.type, Boolean)
    assert isinstance(cols.created_at.type, DateTime)


def test_contracts_client_fk(contracts_table: Table):
    """Vérifie la FK contracts.client_id -> clients.id."""
    fks = list(contracts_table.foreign_key_constraints)
    assert any(
        fk.referred_table.name == "clients"
        and [col.name for col in fk.columns] == ["client_id"]
        for fk in fks
    )


def test_contracts_sales_contact_fk(contracts_table: Table):
    """Vérifie la FK contracts.sales_contact_id -> employees.id."""
    fks = list(contracts_table.foreign_key_constraints)
    assert any(
        fk.referred_table.name == "employees"
        and [col.name for col in fk.columns] == ["sales_contact_id"]
        for fk in fks
    )


def test_contract_instance_creation():
    """Vérifie qu'une instance Contract se crée avec les champs attendus."""
    contract = Contract(
        client_id=1,
        sales_contact_id=1,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("250.00"),
        is_signed=False,
        created_at=datetime.now(timezone.utc),
    )

    assert contract.client_id == 1
    assert contract.sales_contact_id == 1
    assert contract.total_amount == Decimal("1000.00")
    assert contract.amount_due == Decimal("250.00")
    assert contract.is_signed is False
    assert contract.created_at.tzinfo is not None
