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


def test_cmd_clients_create_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.clients as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-create-client")

    monkeypatch.setattr(cmds, "create_client", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(
        first_name="A",
        last_name="B",
        email="a@b.com",
        phone="0",
        company_name="X",
    )
    cmds.cmd_clients_create(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_clients_update_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.clients as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-update-client")

    monkeypatch.setattr(cmds, "update_client", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(
        client_id=1,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        company_name=None,
    )
    cmds.cmd_clients_update(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_clients_reassign_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.clients as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-reassign-client")

    monkeypatch.setattr(cmds, "reassign_client", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(client_id=1, sales_contact_id=2)
    cmds.cmd_clients_reassign(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1
