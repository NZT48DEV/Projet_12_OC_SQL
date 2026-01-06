from __future__ import annotations

import types

import pytest


class DummySession:
    def __init__(self) -> None:
        self.closed = False
        self.rolled_back = False

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def test_cmd_events_create_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.events as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-create-event")

    monkeypatch.setattr(cmds, "create_event", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(
        client_id=1,
        contract_id=1,
        start_date="2026-01-01",
        start_time="10:00",
        end_date="2026-01-01",
        end_time="11:00",
        location="X",
        attendees=10,
        notes=None,
    )
    cmds.cmd_events_create(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_events_update_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.events as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-update-event")

    monkeypatch.setattr(cmds, "update_event", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(
        event_id=1,
        start_date=None,
        start_time=None,
        end_date=None,
        end_time=None,
        location=None,
        attendees=None,
        notes=None,
        support_contact_id=None,
    )
    cmds.cmd_events_update(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_events_reassign_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.events as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-reassign-event")

    monkeypatch.setattr(cmds, "reassign_event", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(event_id=1, support_contact_id=2)
    cmds.cmd_events_reassign(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1
