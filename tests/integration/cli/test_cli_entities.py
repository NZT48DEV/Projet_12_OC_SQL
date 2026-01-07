from __future__ import annotations

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
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")
    monkeypatch.setattr(token_store, "keyring", None)
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")
    monkeypatch.setattr("app.epicevents.init_db", lambda: None)

    # patch get_session dans tous les modules commands
    monkeypatch.setattr("app.cli.commands.auth.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.employees.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.clients.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.contracts.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.events.get_session", lambda: db_session)

    token_store.clear_tokens()


def seed_tokens(monkeypatch, tmp_path, employee_id: int) -> None:
    pair = jwt_service.create_token_pair(employee_id=employee_id)
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


def test_cli_clients_create_and_list(monkeypatch, tmp_path, capsys, db_session):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    sales = create_employee(db_session, email="sales@test.com", role=Role.SALES)
    seed_tokens(monkeypatch, tmp_path, sales.id)

    run_cli(monkeypatch, ["clients", "create", "Jean", "Dupont", "jean@test.com"])
    main()
    out = capsys.readouterr().out
    assert "✅ Client créé" in out

    run_cli(monkeypatch, ["clients", "list"])
    main()
    out = capsys.readouterr().out
    assert "Clients" in out
    assert "jean@test.com" in out


def test_cli_contracts_create_and_list(monkeypatch, tmp_path, capsys, db_session):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    mgmt = create_employee(db_session, email="mgmt@test.com", role=Role.MANAGEMENT)
    sales = create_employee(db_session, email="sales2@test.com", role=Role.SALES)

    client = Client(
        first_name="Client",
        last_name="A",
        email="client@test.com",
        sales_contact_id=sales.id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    client_id = client.id

    seed_tokens(monkeypatch, tmp_path, mgmt.id)

    run_cli(
        monkeypatch,
        ["contracts", "create", str(client_id), "1000", "250", "--signed"],
    )
    main()
    out = capsys.readouterr().out
    assert "✅ Contrat créé" in out

    run_cli(monkeypatch, ["contracts", "list"])
    main()
    out = capsys.readouterr().out
    assert "Contrats" in out
    assert str(client_id) in out


def test_cli_events_create_and_list(monkeypatch, tmp_path, capsys, db_session):
    patch_cli_env(monkeypatch, db_session, tmp_path)

    sales = create_employee(db_session, email="sales3@test.com", role=Role.SALES)
    seed_tokens(monkeypatch, tmp_path, sales.id)

    client = Client(
        first_name="Client",
        last_name="B",
        email="client2@test.com",
        sales_contact_id=sales.id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    client_id = client.id

    contract = Contract(
        client_id=client_id,
        sales_contact_id=client.sales_contact_id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("1000.00"),
        is_signed=True,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    contract_id = contract.id

    run_cli(
        monkeypatch,
        [
            "events",
            "create",
            str(client_id),
            str(contract_id),
            "2025-07-01",
            "09:00",
            "2025-07-01",
            "18:00",
            "Paris",
            "120",
            "--notes",
            "Conf",
        ],
    )
    main()
    out = capsys.readouterr().out
    assert "✅ Événement créé" in out

    run_cli(monkeypatch, ["events", "list"])
    main()
    out = capsys.readouterr().out
    assert "Événements" in out
    assert str(contract_id) in out
