from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from rich.console import Console

from app.cli.commands import contracts as contracts_cmds
from app.models.employee import Role


def test_cmd_contracts_list_empty(monkeypatch, capsys, dummy_session_rb):
    """contracts list: affiche 'Aucun contrat' si vide."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )
    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [])

    contracts_cmds.cmd_contracts_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "Aucun contrat trouvé." in out
    assert dummy_session_rb.closed is True


def test_cmd_contracts_list_prints_for_management(
    monkeypatch, capsys, dummy_session_rb
):
    """contracts list: MANAGEMENT voit la colonne ID + données enrichies (client, sales, téléphone formaté)."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds,
        "get_current_employee",
        lambda s: SimpleNamespace(role=Role.MANAGEMENT),
    )

    # Console large pour éviter les ellipsis/troncatures
    monkeypatch.setattr(
        contracts_cmds,
        "console",
        Console(width=220, force_terminal=True, color_system=None),
    )

    client = SimpleNamespace(
        first_name="Alain",
        last_name="Dupont",
        email="jean.dupont@example.com",
        phone="0612345678",
        company_name="Dupont SAS",
        created_at=datetime(2025, 12, 23, 11, 12, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 8, 11, 19, tzinfo=timezone.utc),
    )
    sales = SimpleNamespace(first_name="John", last_name="Sales")

    ct = SimpleNamespace(
        id=1,
        client=client,
        sales_contact=sales,
        amount_due="2000.00",
        total_amount="20000.00",
        is_signed=True,
    )

    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [ct])

    contracts_cmds.cmd_contracts_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "Contrats" in out

    # Colonne ID visible pour MANAGEMENT
    assert "ID" in out
    assert "1" in out

    # Client
    assert "Alain" in out
    assert "Dupont" in out
    assert "jean.dupont@example.com" in out
    # Téléphone format corrigé
    assert "+33 6 12 34 56 78" in out
    assert "Dupont SAS" in out

    # Commercial
    assert "John" in out
    assert "Sales" in out

    # Montants + signé
    assert "20000.00" in out
    assert "2000.00" in out
    assert "✅" in out

    # Dates (celles du client, comme dans ta commande)
    assert "2025-12-23 11:12" in out
    assert "2026-01-08 11:19" in out

    assert dummy_session_rb.closed is True


def test_cmd_contracts_list_prints_for_sales_hides_id(
    monkeypatch, capsys, dummy_session_rb
):
    """contracts list: SALES ne voit pas la colonne ID."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds,
        "get_current_employee",
        lambda s: SimpleNamespace(role=Role.SALES),
    )

    monkeypatch.setattr(
        contracts_cmds,
        "console",
        Console(width=220, force_terminal=True, color_system=None),
    )

    client = SimpleNamespace(
        first_name="Anthony",
        last_name="Test",
        email="anthony.test@example.com",
        phone=None,  # -> N/A
        company_name=None,  # -> N/A
        created_at=datetime(2025, 12, 29, 12, 21, tzinfo=timezone.utc),
        updated_at=None,  # -> N/A
    )
    sales = SimpleNamespace(first_name="John", last_name="Sales")

    ct = SimpleNamespace(
        id=999,  # ne doit pas “fuir” via colonne ID (elle n’existe pas)
        client=client,
        sales_contact=sales,
        amount_due="2500.00",
        total_amount="10000.00",
        is_signed=True,
    )

    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [ct])

    contracts_cmds.cmd_contracts_list(SimpleNamespace())
    out = capsys.readouterr().out

    assert "Contrats" in out
    assert "ID" not in out  # colonne masquée
    assert "Anthony" in out
    assert "Test" in out
    assert "anthony.test@example.com" in out
    assert "N/A" in out  # téléphone/entreprise/updated_at

    assert dummy_session_rb.closed is True


def test_cmd_contracts_create_success(monkeypatch, capsys, dummy_session_rb):
    """contracts create: parse Decimal et affiche la confirmation."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
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
    assert dummy_session_rb.closed is True


def test_cmd_contracts_sign_authorization_error(monkeypatch, capsys, dummy_session_rb):
    """contracts sign: affiche ⛔ si require_role refuse."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
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
    assert dummy_session_rb.closed is True


def test_cmd_contracts_update_unexpected_error_rollbacks(
    monkeypatch, capsys, dummy_session_rb
):
    """contracts update: rollback + message générique si exception inattendue."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
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
    assert dummy_session_rb.rolled_back is True
    assert dummy_session_rb.closed is True
