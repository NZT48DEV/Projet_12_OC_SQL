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


def test_cmd_employees_deactivate_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.employees as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-deactivate")

    monkeypatch.setattr(cmds, "deactivate_employee", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(employee_id=1)
    cmds.cmd_employees_deactivate(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_employees_delete_soft_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.employees as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-delete-soft")

    monkeypatch.setattr(cmds, "deactivate_employee", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(employee_id=1, hard=False, confirm=None)
    cmds.cmd_employees_delete(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_employees_delete_hard_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.employees as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-delete-hard")

    monkeypatch.setattr(cmds, "hard_delete_employee", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(employee_id=1, hard=True, confirm=1)
    cmds.cmd_employees_delete(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1
