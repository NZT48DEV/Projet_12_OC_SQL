from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.sql.schema import Table

from app.models.event import Event


def test_events_table_exists(tables: Mapping[str, Table]):
    """Vérifie que la table 'events' est bien déclarée dans la metadata."""
    assert "events" in tables


def test_events_columns(events_table: Table):
    """Vérifie colonnes, NULL/NOT NULL et types principaux de la table events."""
    cols = events_table.c

    assert set(cols.keys()) >= {
        "id",
        "contract_id",
        "client_id",
        "support_contact_id",
        "start_date",
        "end_date",
        "location",
        "attendees",
        "notes",
        "created_at",
    }

    assert cols.contract_id.nullable is False
    assert cols.client_id.nullable is False
    assert cols.support_contact_id.nullable is True
    assert cols.start_date.nullable is False
    assert cols.end_date.nullable is False
    assert cols.location.nullable is False
    assert cols.attendees.nullable is False
    assert cols.notes.nullable is True
    assert cols.created_at.nullable is False

    assert isinstance(cols.start_date.type, DateTime)
    assert isinstance(cols.end_date.type, DateTime)
    assert isinstance(cols.location.type, String)
    assert isinstance(cols.created_at.type, DateTime)


def test_events_contract_fk(events_table: Table):
    """Vérifie la FK events.contract_id -> contracts.id."""
    fks = list(events_table.foreign_key_constraints)
    assert any(
        fk.referred_table.name == "contracts"
        and [col.name for col in fk.columns] == ["contract_id"]
        for fk in fks
    )


def test_events_client_fk(events_table: Table):
    """Vérifie la FK events.client_id -> clients.id."""
    fks = list(events_table.foreign_key_constraints)
    assert any(
        fk.referred_table.name == "clients"
        and [col.name for col in fk.columns] == ["client_id"]
        for fk in fks
    )


def test_events_support_contact_fk(events_table: Table):
    """Vérifie la FK events.support_contact_id -> employees.id (nullable)."""
    fks = list(events_table.foreign_key_constraints)
    assert any(
        fk.referred_table.name == "employees"
        and [col.name for col in fk.columns] == ["support_contact_id"]
        for fk in fks
    )


def test_event_instance_creation():
    """Vérifie qu'une instance Event se crée avec les champs attendus."""
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)

    event = Event(
        contract_id=1,
        client_id=1,
        support_contact_id=None,
        start_date=start,
        end_date=end,
        location="Strasbourg",
        attendees=10,
        notes="Notes de test",
        created_at=datetime.now(timezone.utc),
    )

    assert event.contract_id == 1
    assert event.client_id == 1
    assert event.support_contact_id is None
    assert event.start_date == start
    assert event.end_date == end
    assert event.location == "Strasbourg"
    assert event.attendees == 10
    assert event.notes == "Notes de test"
    assert event.created_at.tzinfo is not None
