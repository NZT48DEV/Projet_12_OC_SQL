from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.models.event import Event
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository


def test_client_repository_add_and_get_by_id(db_session):
    emp = Employee(
        first_name="Sales",
        last_name="Guy",
        email="repo-sales@test.com",
        role=Role.SALES,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    repo = ClientRepository(db_session)
    client = Client(
        first_name="A",
        last_name="B",
        email="repo-client@test.com",
        sales_contact_id=emp.id,
    )

    repo.add(client)
    db_session.commit()
    assert client.id is not None

    loaded = repo.get_by_id(client.id)
    assert loaded is not None
    assert loaded.email == "repo-client@test.com"


def test_contract_repository_add_and_get_by_id(db_session):
    emp = Employee(
        first_name="Mgmt",
        last_name="Boss",
        email="repo-mgmt@test.com",
        role=Role.MANAGEMENT,
        password_hash=hash_password("Secret123!"),
    )
    sales = Employee(
        first_name="Sales",
        last_name="Guy",
        email="repo-sales2@test.com",
        role=Role.SALES,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add_all([emp, sales])
    db_session.commit()
    db_session.refresh(sales)

    client = Client(
        first_name="C",
        last_name="D",
        email="repo-client2@test.com",
        sales_contact_id=sales.id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)

    repo = ContractRepository(db_session)
    contract = Contract(
        client_id=client.id,
        sales_contact_id=client.sales_contact_id,
        total_amount=Decimal("100.00"),
        amount_due=Decimal("50.00"),
        is_signed=True,
    )

    repo.add(contract)
    db_session.commit()
    assert contract.id is not None

    loaded = repo.get_by_id(contract.id)
    assert loaded is not None
    assert loaded.client_id == client.id


def test_event_repository_add_and_get_by_id(db_session):
    sales = Employee(
        first_name="Sales",
        last_name="Guy",
        email="repo-sales3@test.com",
        role=Role.SALES,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(sales)
    db_session.commit()
    db_session.refresh(sales)

    client = Client(
        first_name="E",
        last_name="F",
        email="repo-client3@test.com",
        sales_contact_id=sales.id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)

    contract = Contract(
        client_id=client.id,
        sales_contact_id=client.sales_contact_id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("1000.00"),
        is_signed=True,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)

    repo = EventRepository(db_session)
    event = Event(
        contract_id=contract.id,
        client_id=client.id,
        support_contact_id=None,
        start_date=start,
        end_date=end,
        location="Paris",
        attendees=10,
        notes=None,
    )

    repo.add(event)
    db_session.commit()
    assert event.id is not None

    loaded = repo.get_by_id(event.id)
    assert loaded is not None
    assert loaded.location == "Paris"
