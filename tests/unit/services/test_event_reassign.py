from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.models.event import Event
from app.services.event_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    reassign_event,
)


def _create_employee(
    db_session, *, email: str, role: Role, is_active: bool = True
) -> Employee:
    emp = Employee(
        first_name="Test",
        last_name="User",
        email=email,
        role=role,
        password_hash=hash_password("Secret123!"),
        is_active=is_active,
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
    is_signed: bool = True,
) -> Contract:
    contract = Contract(
        client_id=client_id,
        sales_contact_id=sales_contact_id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("0.00"),
        is_signed=is_signed,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


def _create_event(
    db_session,
    *,
    client_id: int,
    contract_id: int,
    support_contact_id: int | None,
) -> Event:
    start = datetime.now() + timedelta(days=1)
    end = start + timedelta(hours=2)

    event = Event(
        client_id=client_id,
        contract_id=contract_id,
        support_contact_id=support_contact_id,
        start_date=start,
        end_date=end,
        location="Paris",
        attendees=10,
        notes=None,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def test_reassign_event_management_ok(db_session):
    manager = _create_employee(db_session, email="m@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="s@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="sup@test.com", role=Role.SUPPORT)
    support2 = _create_employee(db_session, email="sup2@test.com", role=Role.SUPPORT)

    client = _create_client(db_session, email="c@test.com", sales_contact_id=sales.id)
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales.id, is_signed=True
    )
    ev = _create_event(
        db_session,
        client_id=client.id,
        contract_id=contract.id,
        support_contact_id=support.id,
    )

    updated = reassign_event(
        session=db_session,
        current_employee=manager,
        event_id=ev.id,
        support_contact_id=support2.id,
    )
    assert updated.support_contact_id == support2.id


def test_reassign_event_sales_forbidden(db_session):
    sales = _create_employee(db_session, email="s2@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="sup3@test.com", role=Role.SUPPORT)

    with pytest.raises(PermissionDeniedError):
        reassign_event(
            session=db_session,
            current_employee=sales,
            event_id=1,
            support_contact_id=support.id,
        )


def test_reassign_event_support_forbidden(db_session):
    support = _create_employee(db_session, email="sup4@test.com", role=Role.SUPPORT)
    support2 = _create_employee(db_session, email="sup5@test.com", role=Role.SUPPORT)

    with pytest.raises(PermissionDeniedError):
        reassign_event(
            session=db_session,
            current_employee=support,
            event_id=1,
            support_contact_id=support2.id,
        )


def test_reassign_event_not_found(db_session):
    manager = _create_employee(db_session, email="m2@test.com", role=Role.MANAGEMENT)
    support = _create_employee(db_session, email="sup6@test.com", role=Role.SUPPORT)

    with pytest.raises(NotFoundError):
        reassign_event(
            session=db_session,
            current_employee=manager,
            event_id=999999,
            support_contact_id=support.id,
        )


def test_reassign_event_target_employee_not_found(db_session):
    manager = _create_employee(db_session, email="m3@test.com", role=Role.MANAGEMENT)

    # besoin d'un vrai event pour arriver au check de l'employé cible
    sales = _create_employee(db_session, email="s3@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="sup7@test.com", role=Role.SUPPORT)

    client = _create_client(db_session, email="c2@test.com", sales_contact_id=sales.id)
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales.id, is_signed=True
    )
    ev = _create_event(
        db_session,
        client_id=client.id,
        contract_id=contract.id,
        support_contact_id=support.id,
    )

    with pytest.raises(NotFoundError):
        reassign_event(
            session=db_session,
            current_employee=manager,
            event_id=ev.id,
            support_contact_id=999999,
        )


def test_reassign_event_target_employee_must_be_support(db_session):
    manager = _create_employee(db_session, email="m4@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="s4@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="sup8@test.com", role=Role.SUPPORT)

    client = _create_client(db_session, email="c3@test.com", sales_contact_id=sales.id)
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales.id, is_signed=True
    )
    ev = _create_event(
        db_session,
        client_id=client.id,
        contract_id=contract.id,
        support_contact_id=support.id,
    )

    with pytest.raises(ValidationError):
        reassign_event(
            session=db_session,
            current_employee=manager,
            event_id=ev.id,
            support_contact_id=sales.id,  # pas SUPPORT
        )


def test_reassign_event_target_employee_must_be_active(db_session):
    manager = _create_employee(db_session, email="m5@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="s5@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="sup9@test.com", role=Role.SUPPORT)
    inactive_support = _create_employee(
        db_session, email="sup10@test.com", role=Role.SUPPORT, is_active=False
    )

    client = _create_client(db_session, email="c4@test.com", sales_contact_id=sales.id)
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales.id, is_signed=True
    )
    ev = _create_event(
        db_session,
        client_id=client.id,
        contract_id=contract.id,
        support_contact_id=support.id,
    )

    with pytest.raises(ValidationError):
        reassign_event(
            session=db_session,
            current_employee=manager,
            event_id=ev.id,
            support_contact_id=inactive_support.id,
        )
