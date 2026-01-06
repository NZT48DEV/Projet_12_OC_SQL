from __future__ import annotations

import types

import pytest


@pytest.mark.parametrize(
    "func_name,args,service_to_patch",
    [
        (
            "cmd_contracts_create",
            types.SimpleNamespace(
                client_id=1, total="10.0", amount_due="5.0", signed=False
            ),
            "create_contract",
        ),
        (
            "cmd_contracts_update",
            types.SimpleNamespace(contract_id=1, total_amount=None, amount_due=None),
            "update_contract",
        ),
        (
            "cmd_contracts_reassign",
            types.SimpleNamespace(contract_id=1, sales_contact_id=2),
            "reassign_contract",
        ),
    ],
)
def test_contracts_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
    dummy_session_rb,
    func_name: str,
    args,
    service_to_patch: str,
) -> None:
    import app.cli.commands.contracts as cmds

    monkeypatch.setattr(cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    def boom(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(cmds, service_to_patch, boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    getattr(cmds, func_name)(args)

    assert dummy_session_rb.rolled_back is True
    assert dummy_session_rb.closed is True
    assert len(captured) == 1
