from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from rich.console import Console

from app.cli.commands import clients as clients_cmds
from app.models.employee import Role


def test_cmd_clients_list_empty(monkeypatch, capsys, dummy_session_rb):
    """clients list: affiche 'Aucun client' si la liste est vide."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        clients_cmds,
        "get_current_employee",
        lambda s: SimpleNamespace(role=Role.SALES),
    )
    monkeypatch.setattr(clients_cmds, "list_clients", lambda **k: [])

    clients_cmds.cmd_clients_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "Aucun client trouvé." in out
    assert dummy_session_rb.closed is True


def test_cmd_clients_list_prints_for_management(monkeypatch, capsys, dummy_session_rb):
    """clients list: MANAGEMENT voit l'ID + données formatées."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        clients_cmds,
        "get_current_employee",
        lambda s: SimpleNamespace(role=Role.MANAGEMENT),
    )

    # ✅ Force une console Rich assez large pour éviter la troncature
    monkeypatch.setattr(
        clients_cmds,
        "console",
        Console(width=200, force_terminal=True, color_system=None),
    )

    created_at = datetime(2026, 1, 8, 11, 12, tzinfo=timezone.utc)

    c = SimpleNamespace(
        id=1,
        first_name="John",
        last_name="Doe",
        email="j@test.com",
        phone="0612345678",
        company_name="ACME",
        sales_contact=SimpleNamespace(first_name="Jane", last_name="Sales"),
        created_at=created_at,
        updated_at=None,
    )

    monkeypatch.setattr(clients_cmds, "list_clients", lambda **k: [c])

    clients_cmds.cmd_clients_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "Clients" in out
    assert "John" in out
    assert "Doe" in out
    assert "j@test.com" in out
    assert "ACME" in out
    assert "Jane" in out
    assert "Sales" in out
    assert "2026-01-08" in out
    assert "N/A" in out
    assert dummy_session_rb.closed is True


def test_cmd_clients_list_prints_for_sales_hides_id(
    monkeypatch, capsys, dummy_session_rb
):
    """clients list: SALES ne voit pas la colonne ID."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        clients_cmds,
        "get_current_employee",
        lambda s: SimpleNamespace(role=Role.SALES),
    )

    created_at = datetime(2026, 1, 8, 11, 12, tzinfo=timezone.utc)

    c = SimpleNamespace(
        id=99,
        first_name="John",
        last_name="Doe",
        email="j@test.com",
        phone=None,  # doit afficher N/A
        company_name=None,  # doit afficher N/A
        sales_contact=None,  # doit afficher N/A
        created_at=created_at,
        updated_at=None,
    )

    monkeypatch.setattr(clients_cmds, "list_clients", lambda **k: [c])

    clients_cmds.cmd_clients_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "Clients" in out
    assert "John" in out
    assert "Doe" in out
    assert "j@test.com" in out

    # Pas de colonne ID (non-management)
    assert "ID" not in out

    # Valeurs manquantes -> N/A
    assert "N/A" in out

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
