from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.services.client_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    reassign_client,
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
) -> Contract:
    contract = Contract(
        client_id=client_id,
        sales_contact_id=sales_contact_id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("1000.00"),
        is_signed=False,
    )
    db_session.add(contract)
    db_session.commit()
    db_session.refresh(contract)
    return contract


def test_reassign_client_management_ok_updates_client_and_contracts(db_session):
    manager = _create_employee(db_session, email="m@test.com", role=Role.MANAGEMENT)
    old_sales = _create_employee(db_session, email="s1@test.com", role=Role.SALES)
    new_sales = _create_employee(db_session, email="s2@test.com", role=Role.SALES)

    client = _create_client(
        db_session, email="c@test.com", sales_contact_id=old_sales.id
    )

    c1 = _create_contract(
        db_session, client_id=client.id, sales_contact_id=old_sales.id
    )
    c2 = _create_contract(
        db_session, client_id=client.id, sales_contact_id=old_sales.id
    )

    updated = reassign_client(
        session=db_session,
        current_employee=manager,
        client_id=client.id,
        new_sales_contact_id=new_sales.id,
    )

    assert updated.sales_contact_id == new_sales.id

    # reload contracts and check cascade update
    db_session.refresh(c1)
    db_session.refresh(c2)
    assert c1.sales_contact_id == new_sales.id
    assert c2.sales_contact_id == new_sales.id


def test_reassign_client_forbidden_if_not_management(db_session):
    sales = _create_employee(db_session, email="s@test.com", role=Role.SALES)
    target_sales = _create_employee(db_session, email="s2@test.com", role=Role.SALES)
    client = _create_client(db_session, email="c2@test.com", sales_contact_id=sales.id)

    with pytest.raises(PermissionDeniedError):
        reassign_client(
            session=db_session,
            current_employee=sales,
            client_id=client.id,
            new_sales_contact_id=target_sales.id,
        )


def test_reassign_client_client_not_found(db_session):
    manager = _create_employee(db_session, email="m2@test.com", role=Role.MANAGEMENT)
    new_sales = _create_employee(db_session, email="s3@test.com", role=Role.SALES)

    with pytest.raises(NotFoundError):
        reassign_client(
            session=db_session,
            current_employee=manager,
            client_id=999999,
            new_sales_contact_id=new_sales.id,
        )


def test_reassign_client_target_employee_not_found(db_session):
    manager = _create_employee(db_session, email="m3@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="s4@test.com", role=Role.SALES)
    client = _create_client(db_session, email="c3@test.com", sales_contact_id=sales.id)

    with pytest.raises(NotFoundError):
        reassign_client(
            session=db_session,
            current_employee=manager,
            client_id=client.id,
            new_sales_contact_id=999999,
        )


def test_reassign_client_target_employee_must_be_sales(db_session):
    manager = _create_employee(db_session, email="m4@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="s5@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="sup@test.com", role=Role.SUPPORT)
    client = _create_client(db_session, email="c4@test.com", sales_contact_id=sales.id)

    with pytest.raises(ValidationError):
        reassign_client(
            session=db_session,
            current_employee=manager,
            client_id=client.id,
            new_sales_contact_id=support.id,
        )


def test_reassign_client_target_employee_must_be_active(db_session):
    manager = _create_employee(db_session, email="m5@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="s6@test.com", role=Role.SALES)
    inactive_sales = _create_employee(
        db_session, email="s7@test.com", role=Role.SALES, is_active=False
    )
    client = _create_client(db_session, email="c5@test.com", sales_contact_id=sales.id)

    with pytest.raises(ValidationError):
        reassign_client(
            session=db_session,
            current_employee=manager,
            client_id=client.id,
            new_sales_contact_id=inactive_sales.id,
        )
