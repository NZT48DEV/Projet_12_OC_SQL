from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.cli.commands import contracts as contracts_cmds


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


def test_cmd_contracts_list_empty(monkeypatch, capsys, session):
    """contracts list: affiche 'Aucun contrat' si vide."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )
    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [])

    contracts_cmds.cmd_contracts_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "ℹ️  Aucun contrat trouvé." in out


def test_cmd_contracts_create_success(monkeypatch, capsys, session):
    """contracts create: parse Decimal et affiche la confirmation."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    created = SimpleNamespace(
        id=1,
        client_id=2,
        sales_contact_id=3,
        total_amount="100.00",
        amount_due="10.00",
        is_signed=False,
    )
    monkeypatch.setattr(contracts_cmds, "create_contract", lambda **k: created)

    args = SimpleNamespace(
        client_id=2, total="100.00", amount_due="10.00", signed=False
    )
    contracts_cmds.cmd_contracts_create(args)

    out = capsys.readouterr().out
    assert "✅ Contrat créé" in out
    assert "id=1" in out


def test_cmd_contracts_sign_authorization_error(monkeypatch, capsys, session):
    """contracts sign: affiche ⛔ si require_role refuse."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace(role="SALES")
    )

    class FakeAuthzError(Exception):
        pass

    monkeypatch.setattr(contracts_cmds, "AuthorizationError", FakeAuthzError)
    monkeypatch.setattr(
        contracts_cmds,
        "require_role",
        lambda *a, **k: (_ for _ in ()).throw(FakeAuthzError("Interdit")),
    )

    args = SimpleNamespace(contract_id=1)
    contracts_cmds.cmd_contracts_sign(args)

    out = capsys.readouterr().out
    assert "⛔" in out


def test_cmd_contracts_update_unexpected_error_rollbacks(monkeypatch, capsys, session):
    """contracts update: rollback + message générique si exception inattendue."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )
    monkeypatch.setattr(
        contracts_cmds,
        "update_contract",
        lambda **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    args = SimpleNamespace(contract_id=1, total_amount="100.00", amount_due="10.00")
    contracts_cmds.cmd_contracts_update(args)

    out = capsys.readouterr().out
    assert "Erreur lors de la mise à jour du contrat" in out
    assert session.rolled_back is True
