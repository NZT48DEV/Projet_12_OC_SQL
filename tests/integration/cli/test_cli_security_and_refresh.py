from __future__ import annotations

import time
from decimal import Decimal

from app.core import jwt_service, token_store
from app.core.security import hash_password
from app.epicevents import main
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role


def run_cli(monkeypatch, args: list[str]) -> None:
    monkeypatch.setattr("sys.argv", ["epicevents"] + args)


def patch_cli_env(monkeypatch, db_session, tmp_path) -> None:
    # JWT + stockage tokens local dans un tmp
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")
    monkeypatch.setattr(token_store, "keyring", None)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    # Désactive init_db() (sinon side effects hors fixtures)
    monkeypatch.setattr("app.epicevents.init_db", lambda: None)

    # Patch get_session dans tous les modules CLI
    monkeypatch.setattr("app.cli.commands.auth.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.employees.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.clients.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.contracts.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.events.get_session", lambda: db_session)

    # Nettoyage défensif
    token_store.clear_tokens()


def seed_tokens(monkeypatch, tmp_path, employee_id: int) -> None:
    pair = jwt_service.create_token_pair(
        employee_id=employee_id,
        access_minutes=20,
        refresh_days=7,
    )
    token_store.save_tokens(pair.access_token, pair.refresh_token)


def create_employee(db_session, *, email: str, role: Role) -> Employee:
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


# -------------------------------------------------------------------
# AUTH REQUIRED (garde-fous)
# -------------------------------------------------------------------


def test_cli_clients_list_requires_auth(monkeypatch, tmp_path, capsys, db_session):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    # Pas de tokens -> doit refuser
    run_cli(monkeypatch, ["clients", "list"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out or "❌" in out


def test_cli_contracts_list_requires_auth(monkeypatch, tmp_path, capsys, db_session):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    run_cli(monkeypatch, ["contracts", "list"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out or "❌" in out


def test_cli_events_list_requires_auth(monkeypatch, tmp_path, capsys, db_session):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    run_cli(monkeypatch, ["events", "list"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out or "❌" in out


# -------------------------------------------------------------------
# REFRESH TOKEN (intégration CLI)
# -------------------------------------------------------------------


def test_cli_refresh_token_success_updates_tokens(
    monkeypatch, tmp_path, capsys, db_session
):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    emp = create_employee(db_session, email="refresh-ok@test.com", role=Role.MANAGEMENT)
    seed_tokens(monkeypatch, tmp_path, emp.id)

    access_before = token_store.load_access_token()
    refresh_before = token_store.load_refresh_token()
    assert access_before is not None
    assert refresh_before is not None

    time.sleep(2)

    run_cli(monkeypatch, ["refresh-token"])
    main()
    out = capsys.readouterr().out

    assert "✅ Token rafraîchi avec succès." in out

    access_after = token_store.load_access_token()
    refresh_after = token_store.load_refresh_token()

    assert access_after is not None
    assert refresh_after is not None

    assert access_after != access_before


def test_cli_refresh_token_invalid_refresh_token_shows_error(
    monkeypatch, tmp_path, capsys, db_session
):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    # On écrit un refresh token invalide
    token_store.save_tokens("access-does-not-matter", "invalid-refresh-token")

    run_cli(monkeypatch, ["refresh-token"])
    main()
    out = capsys.readouterr().out

    assert "❌ Impossible de rafraîchir le token" in out
    assert "Faites `login`" in out


# -------------------------------------------------------------------
# RBAC (autorisation par rôle) - scénarios de refus
# -------------------------------------------------------------------


def test_cli_contracts_sign_requires_management(
    monkeypatch, tmp_path, capsys, db_session
):
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

    # Tentative de signature par SALES -> refus (require_role MANAGEMENT)
    seed_tokens(monkeypatch, tmp_path, sales.id)

    run_cli(monkeypatch, ["contracts", "sign", str(contract.id)])
    main()
    out = capsys.readouterr().out

    assert (
        "⛔" in out
    )  # cmd_contracts_sign affiche ⛔ en cas de refus :contentReference[oaicite:1]{index=1}


def test_cli_employees_hard_delete_requires_management(
    monkeypatch, tmp_path, capsys, db_session
):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    # Un SALES connecté qui tente un hard delete
    sales = create_employee(db_session, email="sales-del@test.com", role=Role.SALES)

    # Une "cible" existante en base
    target = create_employee(db_session, email="target-del@test.com", role=Role.SUPPORT)

    seed_tokens(monkeypatch, tmp_path, sales.id)

    run_cli(
        monkeypatch,
        ["employees", "delete", str(target.id), "--hard", "--confirm", str(target.id)],
    )
    main()
    out = capsys.readouterr().out

    # Selon la règle métier (service), on attend un refus
    assert "⛔" in out or "Accès refusé" in out
