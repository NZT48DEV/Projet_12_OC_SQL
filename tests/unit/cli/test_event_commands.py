from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from app.cli.commands import events as events_cmds


# -----------------------------
# Helpers de test (Rich Table)
# -----------------------------
def _get_table_columns(table) -> list[str]:
    """Retourne les en-têtes de colonnes Rich (texte)."""
    # Rich 13+: table.columns -> Column objects, .header is str
    return [c.header for c in table.columns]


# -----------------------------
# events create
# -----------------------------
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


# -----------------------------
# events update
# -----------------------------
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
        start_time=None,  # incohérent
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


# -----------------------------
# events list (nouveau: --view)
# -----------------------------
def test_cmd_events_list_default_view_compact(monkeypatch, dummy_session_rb):
    """events list: par défaut view=compact -> colonnes compact."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        events_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    # 1 event minimal
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

    printed = {}

    def fake_print(obj):
        printed["obj"] = obj

    monkeypatch.setattr(events_cmds.console, "print", fake_print)

    # args sans view -> default "compact" dans cmd_events_list
    args = SimpleNamespace()
    events_cmds.cmd_events_list(args)

    table = printed.get("obj")
    assert table is not None

    headers = _get_table_columns(table)
    # compact: event_id, contract_id, client_name, start, end, location, attendees
    assert headers == [
        "Event ID",
        "Contrat ID",
        "Client",
        "Début",
        "Fin",
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
        first_name="A",
        last_name="B",
        email="a@b.com",
        phone="0600000000",
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

    printed = {}

    def fake_print(obj):
        printed["obj"] = obj

    monkeypatch.setattr(events_cmds.console, "print", fake_print)

    args = SimpleNamespace(view="contact")
    events_cmds.cmd_events_list(args)

    table = printed.get("obj")
    assert table is not None

    headers = _get_table_columns(table)
    assert headers == [
        "Event ID",
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
        first_name="A",
        last_name="B",
        email="a@b.com",
        phone="0600000000",
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

    printed = {}

    def fake_print(obj):
        printed["obj"] = obj

    monkeypatch.setattr(events_cmds.console, "print", fake_print)

    args = SimpleNamespace(view="full")
    events_cmds.cmd_events_list(args)

    table = printed.get("obj")
    assert table is not None

    headers = _get_table_columns(table)
    assert headers == [
        "Event ID",
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

    printed = {}

    def fake_print(obj):
        printed["obj"] = obj

    monkeypatch.setattr(events_cmds.console, "print", fake_print)

    args = SimpleNamespace(view="nope")
    events_cmds.cmd_events_list(args)

    table = printed.get("obj")
    assert table is not None

    headers = _get_table_columns(table)
    assert headers == [
        "Event ID",
        "Contrat ID",
        "Client",
        "Début",
        "Fin",
        "Lieu",
        "Participants",
    ]
    assert dummy_session_rb.closed is True
