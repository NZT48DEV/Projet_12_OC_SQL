from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.models.event import Event
from app.services.event_service import (
    PermissionDeniedError,
    ValidationError,
    update_event,
)


@pytest.fixture()
def sales(db_session) -> Employee:
    e = Employee(
        first_name="Sales",
        last_name="One",
        email="sales@test.com",
        role=Role.SALES,
        password_hash=hash_password("Password123!"),
    )
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e


@pytest.fixture()
def manager(db_session) -> Employee:
    e = Employee(
        first_name="Manager",
        last_name="Boss",
        email="manager@test.com",
        role=Role.MANAGEMENT,
        password_hash=hash_password("Password123!"),
    )
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e


@pytest.fixture()
def support(db_session) -> Employee:
    e = Employee(
        first_name="Support",
        last_name="User",
        email="support@test.com",
        role=Role.SUPPORT,
        password_hash=hash_password("Password123!"),
    )
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e


@pytest.fixture()
def support2(db_session) -> Employee:
    e = Employee(
        first_name="Support",
        last_name="Two",
        email="support2@test.com",
        role=Role.SUPPORT,
        password_hash=hash_password("Password123!"),
    )
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e


@pytest.fixture()
def client(db_session, sales) -> Client:
    c = Client(
        first_name="John",
        last_name="Doe",
        email="john@test.com",
        phone=None,
        company_name="ACME",
        sales_contact_id=sales.id,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture()
def signed_contract(db_session, client, sales) -> Contract:
    ct = Contract(
        client_id=client.id,
        sales_contact_id=sales.id,
        total_amount=1000,
        amount_due=0,
        is_signed=True,
    )
    db_session.add(ct)
    db_session.commit()
    db_session.refresh(ct)
    return ct


@pytest.fixture()
def event_assigned_to_support(db_session, client, signed_contract, support) -> Event:
    start = datetime.now() + timedelta(days=2)
    end = start + timedelta(hours=2)

    ev = Event(
        client_id=client.id,
        contract_id=signed_contract.id,
        support_contact_id=support.id,
        start_date=start,
        end_date=end,
        location="Paris",
        attendees=10,
        notes=None,
    )
    db_session.add(ev)
    db_session.commit()
    db_session.refresh(ev)
    return ev


def test_update_event_sales_forbidden(db_session, sales, event_assigned_to_support):
    """Un SALES ne peut jamais modifier un événement."""
    with pytest.raises(PermissionDeniedError):
        update_event(
            session=db_session,
            current_employee=sales,
            event_id=event_assigned_to_support.id,
            location="Lyon",
        )


def test_update_event_support_can_update_only_assigned(
    db_session, support, support2, event_assigned_to_support
):
    """Un SUPPORT ne peut modifier que les événements qui lui sont assignés."""
    # support2 n'est pas assigné => interdit
    with pytest.raises(PermissionDeniedError):
        update_event(
            session=db_session,
            current_employee=support2,
            event_id=event_assigned_to_support.id,
            location="Lyon",
        )

    # support assigné => OK
    updated = update_event(
        session=db_session,
        current_employee=support,
        event_id=event_assigned_to_support.id,
        location="Lyon",
        notes="  note  ",
    )
    assert updated.location == "Lyon"
    assert updated.notes == "note"


def test_update_event_management_can_update_any(
    db_session, manager, event_assigned_to_support
):
    """Un MANAGEMENT peut modifier n'importe quel événement."""
    updated = update_event(
        session=db_session,
        current_employee=manager,
        event_id=event_assigned_to_support.id,
        attendees=0,
    )
    assert updated.attendees == 0


def test_update_event_start_must_be_before_end(
    db_session, manager, event_assigned_to_support
):
    """La date de début d'un événement doit être antérieure à la date de fin."""
    bad_end = event_assigned_to_support.start_date - timedelta(hours=1)
    with pytest.raises(ValidationError):
        update_event(
            session=db_session,
            current_employee=manager,
            event_id=event_assigned_to_support.id,
            end_date=bad_end,
        )


def test_update_event_location_cannot_be_empty(
    db_session, manager, event_assigned_to_support
):
    """Le lieu d'un événement ne peut pas être vide."""
    with pytest.raises(ValidationError):
        update_event(
            session=db_session,
            current_employee=manager,
            event_id=event_assigned_to_support.id,
            location="   ",
        )


def test_update_event_attendees_cannot_be_negative(
    db_session, manager, event_assigned_to_support
):
    """Le nombre de participants ne peut pas être négatif."""
    with pytest.raises(ValidationError):
        update_event(
            session=db_session,
            current_employee=manager,
            event_id=event_assigned_to_support.id,
            attendees=-1,
        )


def test_update_event_support_assignment_management_only(
    db_session, manager, support2, support, event_assigned_to_support
):
    """Seul le MANAGEMENT peut assigner ou modifier le support d'un événement."""
    # support ne peut pas assigner
    with pytest.raises(PermissionDeniedError):
        update_event(
            session=db_session,
            current_employee=support,
            event_id=event_assigned_to_support.id,
            support_contact_id=support2.id,
        )

    # management peut assigner à un SUPPORT
    updated = update_event(
        session=db_session,
        current_employee=manager,
        event_id=event_assigned_to_support.id,
        support_contact_id=support2.id,
    )
    assert updated.support_contact_id == support2.id
