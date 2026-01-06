from __future__ import annotations

import types

import pytest


@pytest.mark.parametrize(
    "cmd_name,args,service_to_patch",
    [
        (
            "cmd_employees_deactivate",
            types.SimpleNamespace(employee_id=1),
            "deactivate_employee",
        ),
        (
            "cmd_employees_delete",
            types.SimpleNamespace(employee_id=1, hard=False, confirm=None),
            "deactivate_employee",
        ),
        (
            "cmd_employees_delete",
            types.SimpleNamespace(employee_id=1, hard=True, confirm=1),
            "hard_delete_employee",
        ),
    ],
)
def test_employees_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
    dummy_session_rb,
    cmd_name: str,
    args,
    service_to_patch: str,
) -> None:
    import app.cli.commands.employees as cmds

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
