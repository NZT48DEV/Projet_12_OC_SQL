from __future__ import annotations

import types

import pytest


@pytest.mark.parametrize(
    "func_name,args",
    [
        (
            "cmd_clients_create",
            types.SimpleNamespace(
                first_name="A",
                last_name="B",
                email="a@b.com",
                phone="0",
                company_name="X",
            ),
        ),
        (
            "cmd_clients_update",
            types.SimpleNamespace(
                client_id=1,
                first_name=None,
                last_name=None,
                email=None,
                phone=None,
                company_name=None,
            ),
        ),
        (
            "cmd_clients_reassign",
            types.SimpleNamespace(client_id=1, sales_contact_id=2),
        ),
    ],
)
def test_clients_unexpected_exception_rolls_back_and_is_captured(
    monkeypatch: pytest.MonkeyPatch,
    dummy_session_rb,
    func_name: str,
    args,
) -> None:
    import app.cli.commands.clients as cmds

    monkeypatch.setattr(cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(cmds, "get_current_employee", lambda s: object())

    # Patch le service appelé selon la commande
    service_to_patch = {
        "cmd_clients_create": "create_client",
        "cmd_clients_update": "update_client",
        "cmd_clients_reassign": "reassign_client",
    }[func_name]

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
