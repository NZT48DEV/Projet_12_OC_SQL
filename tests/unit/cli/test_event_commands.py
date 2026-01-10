from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from app.cli.commands import events as events_cmds
from tests.unit.cli.helpers.rich_table import (
    capture_table,
    get_table,
    table_headers,
)


def test_cmd_events_create_bad_datetime_format(monkeypatch, capsys, dummy_session_rb):
    """events create: refuse si format date/heure invalide."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    args = SimpleNamespace(
        client_id=1,
        contract_id=2,
        start_date="2025-99-99",
        start_time="10:00",
        end_date="2025-12-31",
        end_time="11:00",
        location="Paris",
        attendees=10,
        notes=None,
    )

    events_cmds.cmd_events_create(args)
    out = capsys.readouterr().out

    assert "Format de date/heure invalide" in out
    assert dummy_session_rb.closed is True


def test_cmd_events_update_requires_both_start_fields(
    monkeypatch, capsys, dummy_session_rb
):
    """events update: start-date doit être fourni avec start-time."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    args = SimpleNamespace(
        event_id=1,
        start_date="2025-12-30",
        start_time=None,
        end_date=None,
        end_time=None,
        location=None,
        attendees=None,
        notes=None,
        support_contact_id=None,
    )

    events_cmds.cmd_events_update(args)
    out = capsys.readouterr().out

    assert "Pour modifier le début" in out
    assert dummy_session_rb.closed is True


def test_cmd_events_update_success(monkeypatch, capsys, dummy_session_rb):
    """events update: parse les dates optionnelles et affiche la confirmation."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    updated = SimpleNamespace(
        id=1,
        client_id=2,
        contract_id=3,
        support_contact_id=None,
        start_date=datetime(2026, 1, 1, 10, 0),
        end_date=datetime(2026, 1, 1, 12, 0),
        location="Paris",
        attendees=10,
    )
    monkeypatch.setattr(events_cmds, "update_event", lambda **k: updated)

    args = SimpleNamespace(
        event_id=1,
        start_date="2026-01-01",
        start_time="10:00",
        end_date="2026-01-01",
        end_time="12:00",
        location="Paris",
        attendees=10,
        notes=None,
        support_contact_id=None,
    )

    events_cmds.cmd_events_update(args)
    out = capsys.readouterr().out

    assert "Événement mis à jour" in out
    assert "id=1" in out
    assert dummy_session_rb.closed is True


def test_cmd_events_list_default_view_compact(monkeypatch, dummy_session_rb):
    """events list: par défaut view=compact -> colonnes compact."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    ev = SimpleNamespace(
        id=1,
        contract_id=10,
        start_date=datetime(2026, 1, 1, 10, 0),
        end_date=datetime(2026, 1, 1, 12, 0),
        location="Paris",
        attendees=50,
        notes=None,
        created_at=datetime(2026, 1, 1, 9, 0),
        updated_at=datetime(2026, 1, 1, 9, 30),
        client=None,
        support_contact=None,
    )
    monkeypatch.setattr(events_cmds, "list_events", lambda **k: [ev])

    printed = capture_table(monkeypatch, events_cmds)

    events_cmds.cmd_events_list(SimpleNamespace())
    table = get_table(printed)

    headers = table_headers(table)
    assert headers == [
        "ID Event",
        "Contrat ID",
        "Client",
        "Début",
        "Fin",
        "Support",
        "Lieu",
        "Participants",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_events_list_view_contact(monkeypatch, dummy_session_rb):
    """events list: view=contact -> ajoute Contact client + Support."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    client = SimpleNamespace(
        first_name="A", last_name="B", email="a@b.com", phone="0600000000"
    )
    support = SimpleNamespace(first_name="S", last_name="UP")

    ev = SimpleNamespace(
        id=1,
        contract_id=10,
        start_date=datetime(2026, 1, 1, 10, 0),
        end_date=datetime(2026, 1, 1, 12, 0),
        location="Paris",
        attendees=50,
        notes=None,
        created_at=datetime(2026, 1, 1, 9, 0),
        updated_at=datetime(2026, 1, 1, 9, 30),
        client=client,
        support_contact=support,
    )
    monkeypatch.setattr(events_cmds, "list_events", lambda **k: [ev])

    printed = capture_table(monkeypatch, events_cmds)

    events_cmds.cmd_events_list(SimpleNamespace(view="contact"))
    table = get_table(printed)

    headers = table_headers(table)
    assert headers == [
        "ID Event",
        "Contrat ID",
        "Client",
        "Contact client",
        "Début",
        "Fin",
        "Support",
        "Lieu",
        "Participants",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_events_list_view_full(monkeypatch, dummy_session_rb):
    """events list: view=full -> ajoute Notes + Créé le + Modifié le."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    client = SimpleNamespace(
        first_name="A", last_name="B", email="a@b.com", phone="0600000000"
    )
    support = SimpleNamespace(first_name="S", last_name="UP")

    ev = SimpleNamespace(
        id=1,
        contract_id=10,
        start_date=datetime(2026, 1, 1, 10, 0),
        end_date=datetime(2026, 1, 1, 12, 0),
        location="Paris",
        attendees=50,
        notes="Some notes",
        created_at=datetime(2026, 1, 1, 9, 0),
        updated_at=datetime(2026, 1, 1, 9, 30),
        client=client,
        support_contact=support,
    )
    monkeypatch.setattr(events_cmds, "list_events", lambda **k: [ev])

    printed = capture_table(monkeypatch, events_cmds)

    events_cmds.cmd_events_list(SimpleNamespace(view="full"))
    table = get_table(printed)

    headers = table_headers(table)
    assert headers == [
        "ID Event",
        "Contrat ID",
        "Client",
        "Contact client",
        "Début",
        "Fin",
        "Support",
        "Lieu",
        "Participants",
        "Notes",
        "Créé le",
        "Modifié le",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_events_list_unknown_view_falls_back_to_compact(
    monkeypatch, dummy_session_rb
):
    """events list: view inconnue -> fallback sur compact."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    ev = SimpleNamespace(
        id=1,
        contract_id=10,
        start_date=datetime(2026, 1, 1, 10, 0),
        end_date=datetime(2026, 1, 1, 12, 0),
        location="Paris",
        attendees=50,
        notes=None,
        created_at=datetime(2026, 1, 1, 9, 0),
        updated_at=datetime(2026, 1, 1, 9, 30),
        client=None,
        support_contact=None,
    )
    monkeypatch.setattr(events_cmds, "list_events", lambda **k: [ev])

    printed = capture_table(monkeypatch, events_cmds)

    events_cmds.cmd_events_list(SimpleNamespace(view="nope"))
    table = get_table(printed)

    headers = table_headers(table)
    assert headers == [
        "ID Event",
        "Contrat ID",
        "Client",
        "Début",
        "Fin",
        "Support",
        "Lieu",
        "Participants",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_events_reassign_unassign_support(monkeypatch, capsys, dummy_session_rb):
    """events reassign: --unassign-support retire le support assigné."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    ev = SimpleNamespace(id=1, support_contact_id=None)
    called = {}

    def fake_unassign_event_support(**kwargs):
        called.update(kwargs)
        return ev

    monkeypatch.setattr(
        events_cmds, "unassign_event_support", fake_unassign_event_support
    )

    args = SimpleNamespace(
        event_id=1,
        unassign_support=True,
        support_contact_id=None,
    )

    events_cmds.cmd_events_reassign(args)
    out = capsys.readouterr().out

    assert "Support retiré" in out
    assert "id=1" in out
    assert called["event_id"] == 1
    assert "current_employee" in called
    assert "session" in called
    assert dummy_session_rb.closed is True


def test_cmd_events_list_passes_assigned_to_me_filter(monkeypatch, dummy_session_rb):
    """events list: transmet assigned_to_me au service list_events()."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    captured = {}

    def fake_list_events(**kwargs):
        captured.update(kwargs)
        # Retourne 1 event minimal pour éviter "Aucun événement"
        return [
            SimpleNamespace(
                id=1,
                contract_id=10,
                start_date=datetime(2026, 1, 1, 10, 0),
                end_date=datetime(2026, 1, 1, 12, 0),
                location="Paris",
                attendees=50,
                notes=None,
                created_at=datetime(2026, 1, 1, 9, 0),
                updated_at=datetime(2026, 1, 1, 9, 30),
                client=None,
                support_contact=None,
            )
        ]

    monkeypatch.setattr(events_cmds, "list_events", fake_list_events)

    printed = capture_table(monkeypatch, events_cmds)

    args = SimpleNamespace(view="compact", assigned_to_me=True, without_support=False)
    events_cmds.cmd_events_list(args)

    table = get_table(printed)
    assert table is not None

    assert captured["assigned_to_me"] is True
    assert captured["without_support"] is False
    assert "session" in captured
    assert "current_employee" in captured
    assert dummy_session_rb.closed is True
