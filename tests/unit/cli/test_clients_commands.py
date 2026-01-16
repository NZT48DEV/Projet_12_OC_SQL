from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.cli.commands import clients as clients_cmds
from app.models.employee import Role
from tests.unit.cli.helpers.rich_table import (
    capture_table,
    get_table,
    table_all_text,
    table_headers,
)


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


def test_cmd_clients_list_prints_for_management(monkeypatch, dummy_session_rb):
    """clients list: MANAGEMENT voit l'ID + données formatées."""
    monkeypatch.setattr(clients_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        clients_cmds,
        "get_current_employee",
        lambda s: SimpleNamespace(role=Role.MANAGEMENT),
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

    printed = capture_table(monkeypatch, clients_cmds)

    clients_cmds.cmd_clients_list(SimpleNamespace())
    table = get_table(printed)

    headers = table_headers(table)
    assert any("ID" in h for h in headers)

    text = table_all_text(table)
    assert "John" in text
    assert "Doe" in text
    assert "j@test.com" in text
    assert "ACME" in text
    assert "Jane" in text
    assert "Sales" in text
    assert "+33 6 12 34 56 78" in text
    assert dummy_session_rb.closed is True


def test_cmd_clients_list_prints_for_sales_shows_id(monkeypatch, dummy_session_rb):
    """clients list: MANAGEMENT & SALES voit la colonne ID."""
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
        phone=None,
        company_name=None,
        sales_contact=None,
        created_at=created_at,
        updated_at=None,
    )

    monkeypatch.setattr(clients_cmds, "list_clients", lambda **k: [c])

    printed = capture_table(monkeypatch, clients_cmds)

    clients_cmds.cmd_clients_list(SimpleNamespace())
    table = get_table(printed)

    headers = table_headers(table)
    assert any("ID" in h for h in headers)

    text = table_all_text(table)
    assert "99" in text
    assert "John" in text
    assert "Doe" in text
    assert "j@test.com" in text
    assert "N/A" in text

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
