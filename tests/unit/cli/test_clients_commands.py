from __future__ import annotations

from types import SimpleNamespace

from app.cli.commands import clients as clients_cmds


def test_cmd_clients_list_empty(monkeypatch, capsys, dummy_session_rb):
    """clients list: affiche 'Aucun client' si la liste est vide."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        clients_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )
    monkeypatch.setattr(clients_cmds, "list_clients", lambda **k: [])

    clients_cmds.cmd_clients_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "Aucun client trouvé." in out
    assert dummy_session_rb.closed is True


def test_cmd_clients_list_prints(monkeypatch, capsys, dummy_session_rb):
    """clients list: affiche chaque client formaté."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
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

    assert "Clients" in out
    assert "John" in out
    assert "Doe" in out
    assert "j@test.com" in out
    assert "ACME" in out
    assert "10" in out
    assert dummy_session_rb.closed is True


def test_cmd_clients_create_success(monkeypatch, capsys, dummy_session_rb):
    """clients create: crée un client et affiche la confirmation."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
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
    assert dummy_session_rb.closed is True


def test_cmd_clients_create_unexpected_error_rollbacks(
    monkeypatch, capsys, dummy_session_rb
):
    """clients create: rollback + message générique si exception inattendue."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
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
    assert dummy_session_rb.rolled_back is True
    assert dummy_session_rb.closed is True
