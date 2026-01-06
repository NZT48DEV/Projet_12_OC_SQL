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


def test_cmd_contracts_create_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.contracts as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-create-contract")

    monkeypatch.setattr(cmds, "create_contract", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(
        client_id=1, total="10.0", amount_due="5.0", signed=False
    )
    cmds.cmd_contracts_create(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_contracts_update_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.contracts as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-update-contract")

    monkeypatch.setattr(cmds, "update_contract", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(contract_id=1, total_amount=None, amount_due=None)
    cmds.cmd_contracts_update(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1


def test_cmd_contracts_reassign_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.contracts as cmds

    session = DummySession()
    monkeypatch.setattr(cmds, "get_session", lambda: session)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*args, **kwargs):
        raise RuntimeError("boom-reassign-contract")

    monkeypatch.setattr(cmds, "reassign_contract", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = types.SimpleNamespace(contract_id=1, sales_contact_id=2)
    cmds.cmd_contracts_reassign(args)

    assert session.rolled_back is True
    assert session.closed is True
    assert len(captured) == 1
