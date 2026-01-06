from __future__ import annotations

import types

import pytest


@pytest.mark.parametrize(
    "cmd_name,args,service_to_patch",
    [
        (
            "cmd_events_create",
            types.SimpleNamespace(
                client_id=1,
                contract_id=1,
                start_date="2026-01-01",
                start_time="10:00",
                end_date="2026-01-01",
                end_time="11:00",
                location="X",
                attendees=10,
                notes=None,
            ),
            "create_event",
        ),
        (
            "cmd_events_update",
            types.SimpleNamespace(
                event_id=1,
                start_date=None,
                start_time=None,
                end_date=None,
                end_time=None,
                location=None,
                attendees=None,
                notes=None,
                support_contact_id=None,
            ),
            "update_event",
        ),
        (
            "cmd_events_reassign",
            types.SimpleNamespace(event_id=1, support_contact_id=2),
            "reassign_event",
        ),
    ],
)
def test_events_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
    dummy_session_rb,
    cmd_name: str,
    args,
    service_to_patch: str,
) -> None:
    import app.cli.commands.events as cmds

    monkeypatch.setattr(cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(cmds, service_to_patch, boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    getattr(cmds, cmd_name)(args)

    assert dummy_session_rb.rolled_back is True
    assert dummy_session_rb.closed is True
    assert len(captured) == 1
