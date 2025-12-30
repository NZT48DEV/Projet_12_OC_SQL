from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.employee import Employee, Role
from app.services.contract_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    create_contract,
    list_contracts,
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


def test_list_contracts_returns_list(db_session):
    mgmt = _create_employee(db_session, email="mgmt@test.com", role=Role.MANAGEMENT)
    result = list_contracts(session=db_session, current_employee=mgmt)
    assert isinstance(result, list)


def test_create_contract_denied_if_not_sales_or_management(db_session):
    support = _create_employee(db_session, email="support@test.com", role=Role.SUPPORT)

    with pytest.raises(PermissionDeniedError):
        create_contract(
            session=db_session,
            current_employee=support,
            client_id=1,
            total_amount=Decimal("1000.00"),
            amount_due=Decimal("1000.00"),
            is_signed=False,
        )


def test_create_contract_client_not_found(db_session):
    mgmt = _create_employee(db_session, email="mgmt2@test.com", role=Role.MANAGEMENT)

    with pytest.raises(NotFoundError):
        create_contract(
            session=db_session,
            current_employee=mgmt,
            client_id=999999,
            total_amount=Decimal("1000.00"),
            amount_due=Decimal("1000.00"),
            is_signed=False,
        )


def test_create_contract_validation_amounts(db_session):
    mgmt = _create_employee(db_session, email="mgmt3@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="sales2@test.com", role=Role.SALES)
    client = _create_client(db_session, email="c@test.com", sales_contact_id=sales.id)

    with pytest.raises(ValidationError):
        create_contract(
            session=db_session,
            current_employee=mgmt,
            client_id=client.id,
            total_amount=Decimal("0"),
            amount_due=Decimal("0"),
            is_signed=False,
        )

    with pytest.raises(ValidationError):
        create_contract(
            session=db_session,
            current_employee=mgmt,
            client_id=client.id,
            total_amount=Decimal("100"),
            amount_due=Decimal("200"),
            is_signed=False,
        )


def test_create_contract_success_sets_sales_contact_id_from_client(db_session):
    mgmt = _create_employee(db_session, email="mgmt4@test.com", role=Role.MANAGEMENT)
    sales = _create_employee(db_session, email="sales3@test.com", role=Role.SALES)
    client = _create_client(db_session, email="c2@test.com", sales_contact_id=sales.id)

    contract = create_contract(
        session=db_session,
        current_employee=mgmt,
        client_id=client.id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("250.00"),
        is_signed=True,
    )

    assert contract.id is not None
    assert contract.client_id == client.id
    assert contract.sales_contact_id == client.sales_contact_id
    assert contract.is_signed is True
