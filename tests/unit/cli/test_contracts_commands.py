from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.cli.commands import contracts as contracts_cmds
from tests.unit.cli.helpers.rich_table import (
    capture_table,
    get_table,
    table_all_text,
    table_headers,
)


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


def test_cmd_contracts_list_default_view_compact_headers(monkeypatch, dummy_session_rb):
    """contracts list: par défaut view=compact -> colonnes compact."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    ct = SimpleNamespace(
        id=1,
        client=None,
        sales_contact=None,
        amount_due="2000.00",
        total_amount="20000.00",
        is_signed=True,
        created_at=None,
        updated_at=None,
    )
    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [ct])

    printed = capture_table(monkeypatch, contracts_cmds)
    contracts_cmds.cmd_contracts_list(SimpleNamespace())
    table = get_table(printed)

    assert table_headers(table) == [
        "ID Contrat",
        "Client",
        "Entreprise",
        "Commercial",
        "Restant à payer",
        "Total",
        "Signé",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_contracts_list_view_contact_headers(monkeypatch, dummy_session_rb):
    """contracts list: view=contact -> colonnes contact."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    ct = SimpleNamespace(
        id=1,
        client=None,
        sales_contact=None,
        amount_due="2000.00",
        total_amount="20000.00",
        is_signed=True,
        created_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [ct])

    printed = capture_table(monkeypatch, contracts_cmds)
    contracts_cmds.cmd_contracts_list(SimpleNamespace(view="contact"))
    table = get_table(printed)

    assert table_headers(table) == [
        "ID Contrat",
        "Client",
        "Email",
        "Téléphone",
        "Entreprise",
        "Signé",
        "Créé le",
        "Modifié le",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_contracts_list_view_full_headers(monkeypatch, dummy_session_rb):
    """contracts list: view=full -> colonnes full."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    ct = SimpleNamespace(
        id=1,
        client=None,
        sales_contact=None,
        amount_due="2000.00",
        total_amount="20000.00",
        is_signed=True,
        created_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, 9, 30, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [ct])

    printed = capture_table(monkeypatch, contracts_cmds)
    contracts_cmds.cmd_contracts_list(SimpleNamespace(view="full"))
    table = get_table(printed)

    assert table_headers(table) == [
        "ID Contrat",
        "Client",
        "Email",
        "Téléphone",
        "Entreprise",
        "Commercial",
        "Restant à payer",
        "Total",
        "Signé",
        "Créé le",
        "Modifié le",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_contracts_list_unknown_view_falls_back_to_compact_headers(
    monkeypatch, dummy_session_rb
):
    """contracts list: view inconnue -> fallback compact."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    ct = SimpleNamespace(
        id=1,
        client=None,
        sales_contact=None,
        amount_due="2000.00",
        total_amount="20000.00",
        is_signed=True,
        created_at=None,
        updated_at=None,
    )
    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [ct])

    printed = capture_table(monkeypatch, contracts_cmds)
    contracts_cmds.cmd_contracts_list(SimpleNamespace(view="nope"))
    table = get_table(printed)

    assert table_headers(table) == [
        "ID Contrat",
        "Client",
        "Entreprise",
        "Commercial",
        "Restant à payer",
        "Total",
        "Signé",
    ]
    assert dummy_session_rb.closed is True


def test_cmd_contracts_list_full_shows_client_sales_and_phone_formatted(
    monkeypatch, dummy_session_rb
):
    """contracts list (full): contient email/téléphone formaté + commercial + montants + signé."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    client = SimpleNamespace(
        first_name="Alain",
        last_name="Dupont",
        email="jean.dupont@example.com",
        phone="0612345678",
        company_name="Dupont SAS",
    )
    sales = SimpleNamespace(first_name="John", last_name="Sales")

    ct = SimpleNamespace(
        id=1,
        client=client,
        sales_contact=sales,
        amount_due="2000.00",
        total_amount="20000.00",
        is_signed=True,
        created_at=datetime(2025, 12, 23, 11, 12, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 8, 11, 19, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(contracts_cmds, "list_contracts", lambda **k: [ct])

    printed = capture_table(monkeypatch, contracts_cmds)
    contracts_cmds.cmd_contracts_list(SimpleNamespace(view="full"))
    table = get_table(printed)

    text = table_all_text(table)

    assert "Alain Dupont" in text
    assert "jean.dupont@example.com" in text
    assert "+33 6 12 34 56 78" in text
    assert "Dupont SAS" in text
    assert "John Sales" in text
    assert "2000.00" in text
    assert "20000.00" in text
    assert "✅" in text

    assert dummy_session_rb.closed is True


def test_cmd_contracts_list_passes_filters_to_service(monkeypatch, dummy_session_rb):
    """contracts list: transmet unsigned/unpaid au service list_contracts()."""
    monkeypatch.setattr(contracts_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        contracts_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    captured = {}

    def fake_list_contracts(**kwargs):
        captured.update(kwargs)
        return [
            SimpleNamespace(
                id=1,
                client=None,
                sales_contact=None,
                amount_due="0.00",
                total_amount="10.00",
                is_signed=False,
                created_at=None,
                updated_at=None,
            )
        ]

    monkeypatch.setattr(contracts_cmds, "list_contracts", fake_list_contracts)

    printed = capture_table(monkeypatch, contracts_cmds)
    contracts_cmds.cmd_contracts_list(
        SimpleNamespace(unsigned=True, unpaid=True, view="compact")
    )
    _ = get_table(printed)

    assert captured["unsigned"] is True
    assert captured["unpaid"] is True
    assert "session" in captured
    assert "current_employee" in captured
    assert dummy_session_rb.closed is True
