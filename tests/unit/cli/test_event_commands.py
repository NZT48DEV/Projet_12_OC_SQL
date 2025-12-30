from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import pytest

from app.cli.commands import events as events_cmds


class DummySession:
    def __init__(self) -> None:
        self.rolled_back = False
        self.closed = False

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


@pytest.fixture()
def session() -> DummySession:
    return DummySession()


def test_cmd_events_create_bad_datetime_format(monkeypatch, capsys, session):
    """events create: refuse si format date/heure invalide."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: session)
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

    assert "❌ Format de date/heure invalide" in out


def test_cmd_events_update_requires_both_start_fields(monkeypatch, capsys, session):
    """events update: start-date doit être fourni avec start-time."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: session)
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

    assert "❌ Pour modifier le début" in out


def test_cmd_events_update_success(monkeypatch, capsys, session):
    """events update: parse les dates optionnelles et affiche la confirmation."""
    monkeypatch.setattr(events_cmds, "get_session", lambda: session)
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
