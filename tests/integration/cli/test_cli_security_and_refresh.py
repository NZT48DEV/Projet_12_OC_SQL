from __future__ import annotations

import re
import time
from decimal import Decimal

from app.core import jwt_service, token_store
from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from tests.integration.cli._click_runner import invoke_cli


def patch_cli_env(monkeypatch, db_session, tmp_path) -> None:
    """Configure l’environnement CLI (JWT, sessions patchées, tokens dans tmp)."""
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")
    monkeypatch.setattr(token_store, "keyring", None)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")
    monkeypatch.setattr("app.epicevents.init_db", lambda: None)

    monkeypatch.setattr("app.cli.commands.auth.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.employees.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.clients.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.contracts.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.events.get_session", lambda: db_session)

    token_store.clear_tokens()


def seed_tokens(monkeypatch, tmp_path, employee_id: int) -> None:
    """Seed des tokens valides pour employee_id."""
    pair = jwt_service.create_token_pair(
        employee_id=employee_id,
        access_minutes=20,
        refresh_days=7,
    )
    token_store.save_tokens(pair.access_token, pair.refresh_token)


def create_employee(db_session, *, email: str, role: Role) -> Employee:
    """Crée et persiste un employé de test."""
    emp = Employee(
        first_name="T",
        last_name="U",
        email=email,
        role=role,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def test_cli_clients_list_requires_auth(monkeypatch, tmp_path, capsys, db_session):
    """clients list sans token doit refuser."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    result = invoke_cli(["clients", "list"])

    assert "Non authentifié" in result.output or "❌" in result.output


def test_cli_contracts_list_requires_auth(monkeypatch, tmp_path, capsys, db_session):
    """contracts list sans token doit refuser."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    result = invoke_cli(["contracts", "list"])

    assert "Non authentifié" in result.output or "❌" in result.output


def test_cli_events_list_requires_auth(monkeypatch, tmp_path, capsys, db_session):
    """events list sans token doit refuser."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    result = invoke_cli(["events", "list"])

    assert "Non authentifié" in result.output or "❌" in result.output


def test_cli_refresh_token_success_updates_tokens(
    monkeypatch, tmp_path, capsys, db_session
):
    """refresh-token valide met à jour les tokens."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    emp = create_employee(db_session, email="refresh-ok@test.com", role=Role.MANAGEMENT)
    seed_tokens(monkeypatch, tmp_path, emp.id)

    access_before = token_store.load_access_token()
    refresh_before = token_store.load_refresh_token()
    assert access_before is not None
    assert refresh_before is not None

    time.sleep(2)

    result = invoke_cli(["refresh-token"])

    assert re.search(
        r"✅ Token rafraîchi avec succès(\s+\(\d+\s+min\))?\.", result.output
    )

    access_after = token_store.load_access_token()
    refresh_after = token_store.load_refresh_token()
    assert access_after is not None
    assert refresh_after is not None
    assert access_after != access_before


def test_cli_refresh_token_invalid_refresh_token_shows_error(
    monkeypatch, tmp_path, capsys, db_session
):
    """refresh-token invalide affiche une erreur."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    token_store.save_tokens("access-does-not-matter", "invalid-refresh-token")

    result = invoke_cli(["refresh-token"])

    assert "❌ Impossible de rafraîchir le token" in result.output
    assert "Faites `login`" in result.output


def test_cli_contracts_sign_requires_management(
    monkeypatch, tmp_path, capsys, db_session
):
    """contracts sign par SALES doit refuser."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    sales = create_employee(db_session, email="sales-sign@test.com", role=Role.SALES)

    client = Client(
        first_name="C",
        last_name="L",
        email="c-sign@test.com",
        sales_contact_id=sales.id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)

    contract = Contract(
        client_id=client.id,
        sales_contact_id=sales.id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("1000.00"),
        is_signed=False,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    seed_tokens(monkeypatch, tmp_path, sales.id)

    result = invoke_cli(["contracts", "sign", str(contract.id)])

    assert "⛔" in result.output


def test_cli_employees_hard_delete_requires_management(
    monkeypatch, tmp_path, capsys, db_session
):
    """employees delete --hard par SALES doit refuser."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    sales = create_employee(db_session, email="sales-del@test.com", role=Role.SALES)
    target = create_employee(db_session, email="target-del@test.com", role=Role.SUPPORT)

    seed_tokens(monkeypatch, tmp_path, sales.id)

    result = invoke_cli(
        ["employees", "delete", str(target.id), "--hard", "--confirm", str(target.id)]
    )

    assert "⛔" in result.output or "Accès refusé" in result.output
