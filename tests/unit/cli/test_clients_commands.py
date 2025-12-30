from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.cli.commands import clients as clients_cmds


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


def test_cmd_clients_list_empty(monkeypatch, capsys, session):
    """clients list: affiche 'Aucun client' si la liste est vide."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        clients_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )
    monkeypatch.setattr(clients_cmds, "list_clients", lambda **k: [])

    clients_cmds.cmd_clients_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "ℹ️  Aucun client trouvé." in out
    assert session.closed is True


def test_cmd_clients_list_prints(monkeypatch, capsys, session):
    """clients list: affiche chaque client formaté."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        clients_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    c = SimpleNamespace(
        id=1,
        first_name="John",
        last_name="Doe",
        email="j@test.com",
        company_name="ACME",
        sales_contact_id=10,
    )
    monkeypatch.setattr(clients_cmds, "list_clients", lambda **k: [c])

    clients_cmds.cmd_clients_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "📋 Clients" in out
    assert "id=1" in out
    assert "sales_contact_id=10" in out


def test_cmd_clients_create_success(monkeypatch, capsys, session):
    """clients create: crée un client et affiche la confirmation."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        clients_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    created = SimpleNamespace(
        id=1,
        first_name="John",
        last_name="Doe",
        email="j@test.com",
        company_name=None,
        sales_contact_id=3,
    )
    monkeypatch.setattr(clients_cmds, "create_client", lambda **k: created)

    args = SimpleNamespace(
        first_name="John",
        last_name="Doe",
        email="j@test.com",
        phone=None,
        company_name=None,
    )
    clients_cmds.cmd_clients_create(args)

    out = capsys.readouterr().out
    assert "✅ Client créé" in out
    assert "id=1" in out


def test_cmd_clients_create_unexpected_error_rollbacks(monkeypatch, capsys, session):
    """clients create: rollback + message générique si exception inattendue."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        clients_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )
    monkeypatch.setattr(
        clients_cmds,
        "create_client",
        lambda **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    args = SimpleNamespace(
        first_name="John",
        last_name="Doe",
        email="j@test.com",
        phone=None,
        company_name=None,
    )
    clients_cmds.cmd_clients_create(args)

    out = capsys.readouterr().out
    assert "❌ Erreur lors de la création du client" in out
    assert session.rolled_back is True
