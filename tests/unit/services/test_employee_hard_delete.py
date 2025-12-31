from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.models.event import Event
from app.services.employee_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    hard_delete_employee,
)


def _create_employee(db_session, *, email: str, role: Role) -> Employee:
    emp = Employee(
        first_name="Test",
        last_name="User",
        email=email,
        role=role,
        password_hash=hash_password("Secret123!"),
        is_active=True,
        deactivated_at=None,
        reactivated_at=None,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def _create_client(
    db_session, *, sales_id: int, email: str = "client@test.com"
) -> Client:
    client = Client(
        first_name="Client",
        last_name="Test",
        email=email,
        phone="0600000000",
        company_name="ACME",
        sales_contact_id=sales_id,
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


def _create_contract(db_session, *, client_id: int, sales_id: int) -> Contract:
    contract = Contract(
        client_id=client_id,
        sales_contact_id=sales_id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("500.00"),
        is_signed=False,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


def _create_event(
    db_session, *, client_id: int, contract_id: int, support_id: int | None
) -> Event:
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = start + timedelta(hours=2)

    event = Event(
        client_id=client_id,
        contract_id=contract_id,
        support_contact_id=support_id,
        start_date=start,
        end_date=end,
        location="Paris",
        attendees=10,
        notes="test",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def test_hard_delete_employee_forbidden_for_sales(db_session):
    """SALES ne peut pas supprimer définitivement un employé."""
    sales = _create_employee(db_session, email="sales@test.com", role=Role.SALES)
    target = _create_employee(db_session, email="target@test.com", role=Role.SUPPORT)

    with pytest.raises(PermissionDeniedError):
        hard_delete_employee(
            session=db_session,
            current_employee=sales,
            employee_id=target.id,
            confirm_employee_id=target.id,
        )


def test_hard_delete_employee_confirm_mismatch(db_session):
    """Hard delete refuse si confirm_employee_id ne correspond pas à employee_id."""
    manager = _create_employee(db_session, email="m@test.com", role=Role.MANAGEMENT)
    target = _create_employee(db_session, email="t@test.com", role=Role.SUPPORT)

    with pytest.raises(ValidationError):
        hard_delete_employee(
            session=db_session,
            current_employee=manager,
            employee_id=target.id,
            confirm_employee_id=999999,
        )


def test_hard_delete_employee_cannot_self_delete(db_session):
    """Hard delete interdit de se supprimer soi-même."""
    manager = _create_employee(db_session, email="m2@test.com", role=Role.MANAGEMENT)

    with pytest.raises(ValidationError):
        hard_delete_employee(
            session=db_session,
            current_employee=manager,
            employee_id=manager.id,
            confirm_employee_id=manager.id,
        )


def test_hard_delete_employee_not_found(db_session):
    """Hard delete échoue si employé introuvable."""
    manager = _create_employee(db_session, email="m3@test.com", role=Role.MANAGEMENT)

    with pytest.raises(NotFoundError):
        hard_delete_employee(
            session=db_session,
            current_employee=manager,
            employee_id=999999999,
            confirm_employee_id=999999999,
        )


def test_hard_delete_employee_blocked_if_referenced_by_client(db_session):
    """Hard delete refusé si l'employé est référencé par un client."""
    manager = _create_employee(db_session, email="m4@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="sales2@test.com", role=Role.SALES)

    client = _create_client(db_session, sales_id=sales.id, email="client@test.com")
    assert client.sales_contact_id == sales.id  # sanity check

    with pytest.raises(ValidationError):
        hard_delete_employee(
            session=db_session,
            current_employee=manager,
            employee_id=sales.id,
            confirm_employee_id=sales.id,
        )


def test_hard_delete_employee_blocked_if_referenced_by_contract(db_session):
    """Hard delete refusé si l'employé est référencé par un contrat."""
    manager = _create_employee(db_session, email="m5@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="sales3@test.com", role=Role.SALES)

    client = _create_client(
        db_session, sales_id=sales.id, email="client_contract@test.com"
    )
    contract = _create_contract(db_session, client_id=client.id, sales_id=sales.id)
    assert contract.sales_contact_id == sales.id  # sanity check

    with pytest.raises(ValidationError):
        hard_delete_employee(
            session=db_session,
            current_employee=manager,
            employee_id=sales.id,
            confirm_employee_id=sales.id,
        )


def test_hard_delete_employee_blocked_if_referenced_by_event(db_session):
    """Hard delete refusé si l'employé est référencé par un événement (support_contact_id)."""
    manager = _create_employee(db_session, email="m6@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="sales4@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="support@test.com", role=Role.SUPPORT)

    client = _create_client(
        db_session, sales_id=sales.id, email="client_event@test.com"
    )
    contract = _create_contract(db_session, client_id=client.id, sales_id=sales.id)
    event = _create_event(
        db_session, client_id=client.id, contract_id=contract.id, support_id=support.id
    )
    assert event.support_contact_id == support.id  # sanity check

    with pytest.raises(ValidationError):
        hard_delete_employee(
            session=db_session,
            current_employee=manager,
            employee_id=support.id,
            confirm_employee_id=support.id,
        )


def test_hard_delete_employee_ok_when_not_referenced(db_session):
    """Hard delete OK si aucune référence n'existe."""
    manager = _create_employee(db_session, email="m7@test.com", role=Role.MANAGEMENT)
    target = _create_employee(db_session, email="target2@test.com", role=Role.SUPPORT)

    hard_delete_employee(
        session=db_session,
        current_employee=manager,
        employee_id=target.id,
        confirm_employee_id=target.id,
    )

    assert db_session.get(Employee, target.id) is None
