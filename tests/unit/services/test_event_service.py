from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.services.event_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    create_event,
    list_events,
)


def _create_employee(db_session, *, email: str, role: Role) -> Employee:
    emp = Employee(
        first_name="Test",
        last_name="User",
        email=email,
        role=role,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def _create_client(db_session, *, email: str, sales_contact_id: int) -> Client:
    client = Client(
        first_name="Client",
        last_name="Test",
        email=email,
        sales_contact_id=sales_contact_id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


def _create_contract(
    db_session,
    *,
    client_id: int,
    sales_contact_id: int,
    is_signed: bool,
) -> Contract:
    contract = Contract(
        client_id=client_id,
        sales_contact_id=sales_contact_id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("1000.00"),
        is_signed=is_signed,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


def test_list_events_returns_list(db_session):
    sales = _create_employee(db_session, email="sales@test.com", role=Role.SALES)
    result = list_events(session=db_session, current_employee=sales)
    assert isinstance(result, list)


def test_create_event_denied_if_not_sales(db_session):
    mgmt = _create_employee(db_session, email="mgmt@test.com", role=Role.MANAGEMENT)

    now = datetime.now(timezone.utc)
    with pytest.raises(PermissionDeniedError):
        create_event(
            session=db_session,
            current_employee=mgmt,
            client_id=1,
            contract_id=1,
            start_date=now,
            end_date=now + timedelta(hours=1),
            location="Paris",
            attendees=10,
            notes=None,
        )


def test_create_event_client_not_found(db_session):
    sales = _create_employee(db_session, email="sales2@test.com", role=Role.SALES)
    now = datetime.now(timezone.utc)

    with pytest.raises(NotFoundError):
        create_event(
            session=db_session,
            current_employee=sales,
            client_id=999999,
            contract_id=1,
            start_date=now,
            end_date=now + timedelta(hours=1),
            location="Paris",
            attendees=10,
            notes=None,
        )


def test_create_event_denied_if_client_not_owned(db_session):
    sales = _create_employee(db_session, email="sales3@test.com", role=Role.SALES)
    other_sales = _create_employee(db_session, email="sales4@test.com", role=Role.SALES)

    client = _create_client(
        db_session, email="c@test.com", sales_contact_id=other_sales.id
    )
    contract = _create_contract(
        db_session,
        client_id=client.id,
        sales_contact_id=client.sales_contact_id,
        is_signed=True,
    )

    now = datetime.now(timezone.utc)
    with pytest.raises(PermissionDeniedError):
        create_event(
            session=db_session,
            current_employee=sales,
            client_id=client.id,
            contract_id=contract.id,
            start_date=now,
            end_date=now + timedelta(hours=1),
            location="Paris",
            attendees=10,
            notes=None,
        )


def test_create_event_rejects_unsigned_contract(db_session):
    sales = _create_employee(db_session, email="sales5@test.com", role=Role.SALES)
    client = _create_client(db_session, email="c2@test.com", sales_contact_id=sales.id)
    contract = _create_contract(
        db_session,
        client_id=client.id,
        sales_contact_id=client.sales_contact_id,
        is_signed=False,
    )

    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        create_event(
            session=db_session,
            current_employee=sales,
            client_id=client.id,
            contract_id=contract.id,
            start_date=now,
            end_date=now + timedelta(hours=1),
            location="Paris",
            attendees=10,
            notes=None,
        )


def test_create_event_success(db_session):
    sales = _create_employee(db_session, email="sales6@test.com", role=Role.SALES)
    client = _create_client(db_session, email="c3@test.com", sales_contact_id=sales.id)
    contract = _create_contract(
        db_session,
        client_id=client.id,
        sales_contact_id=client.sales_contact_id,
        is_signed=True,
    )

    now = datetime.now(timezone.utc)
    event = create_event(
        session=db_session,
        current_employee=sales,
        client_id=client.id,
        contract_id=contract.id,
        start_date=now,
        end_date=now + timedelta(hours=2),
        location="Paris",
        attendees=120,
        notes="Conf",
    )

    assert event.id is not None
    assert event.client_id == client.id
    assert event.contract_id == contract.id
    assert event.location == "Paris"
