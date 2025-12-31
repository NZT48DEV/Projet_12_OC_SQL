from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.contract import Contract
from app.models.employee import Employee, Role
from app.services.contract_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    reassign_contract,
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


def test_reassign_contract_management_ok(db_session):
    manager = _create_employee(db_session, email="m@test.com", role=Role.MANAGEMENT)
    sales_owner = _create_employee(db_session, email="s1@test.com", role=Role.SALES)
    sales_new = _create_employee(db_session, email="s2@test.com", role=Role.SALES)

    client = _create_client(
        db_session, email="c@test.com", sales_contact_id=sales_owner.id
    )
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales_owner.id
    )

    updated = reassign_contract(
        session=db_session,
        current_employee=manager,
        contract_id=contract.id,
        new_sales_contact_id=sales_new.id,
    )
    assert updated.sales_contact_id == sales_new.id


def test_reassign_contract_sales_owner_ok(db_session):
    sales_owner = _create_employee(db_session, email="s3@test.com", role=Role.SALES)
    sales_new = _create_employee(db_session, email="s4@test.com", role=Role.SALES)

    client = _create_client(
        db_session, email="c2@test.com", sales_contact_id=sales_owner.id
    )
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales_owner.id
    )

    updated = reassign_contract(
        session=db_session,
        current_employee=sales_owner,
        contract_id=contract.id,
        new_sales_contact_id=sales_new.id,
    )
    assert updated.sales_contact_id == sales_new.id


def test_reassign_contract_sales_not_owner_forbidden(db_session):
    sales_owner = _create_employee(db_session, email="s5@test.com", role=Role.SALES)
    sales_other = _create_employee(db_session, email="s6@test.com", role=Role.SALES)
    sales_new = _create_employee(db_session, email="s7@test.com", role=Role.SALES)

    client = _create_client(
        db_session, email="c3@test.com", sales_contact_id=sales_owner.id
    )
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales_owner.id
    )

    with pytest.raises(PermissionDeniedError):
        reassign_contract(
            session=db_session,
            current_employee=sales_other,
            contract_id=contract.id,
            new_sales_contact_id=sales_new.id,
        )


def test_reassign_contract_support_forbidden(db_session):
    support = _create_employee(db_session, email="sup@test.com", role=Role.SUPPORT)
    sales_owner = _create_employee(db_session, email="s8@test.com", role=Role.SALES)
    sales_new = _create_employee(db_session, email="s9@test.com", role=Role.SALES)

    client = _create_client(
        db_session, email="c4@test.com", sales_contact_id=sales_owner.id
    )
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales_owner.id
    )

    with pytest.raises(PermissionDeniedError):
        reassign_contract(
            session=db_session,
            current_employee=support,
            contract_id=contract.id,
            new_sales_contact_id=sales_new.id,
        )


def test_reassign_contract_not_found(db_session):
    manager = _create_employee(db_session, email="m2@test.com", role=Role.MANAGEMENT)
    sales_new = _create_employee(db_session, email="s10@test.com", role=Role.SALES)

    with pytest.raises(NotFoundError):
        reassign_contract(
            session=db_session,
            current_employee=manager,
            contract_id=999999,
            new_sales_contact_id=sales_new.id,
        )


def test_reassign_contract_target_employee_not_found(db_session):
    manager = _create_employee(db_session, email="m3@test.com", role=Role.MANAGEMENT)
    sales_owner = _create_employee(db_session, email="s11@test.com", role=Role.SALES)

    client = _create_client(
        db_session, email="c5@test.com", sales_contact_id=sales_owner.id
    )
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales_owner.id
    )

    with pytest.raises(NotFoundError):
        reassign_contract(
            session=db_session,
            current_employee=manager,
            contract_id=contract.id,
            new_sales_contact_id=999999,
        )


def test_reassign_contract_target_employee_must_be_sales(db_session):
    manager = _create_employee(db_session, email="m4@test.com", role=Role.MANAGEMENT)
    sales_owner = _create_employee(db_session, email="s12@test.com", role=Role.SALES)
    support = _create_employee(db_session, email="sup2@test.com", role=Role.SUPPORT)

    client = _create_client(
        db_session, email="c6@test.com", sales_contact_id=sales_owner.id
    )
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales_owner.id
    )

    with pytest.raises(ValidationError):
        reassign_contract(
            session=db_session,
            current_employee=manager,
            contract_id=contract.id,
            new_sales_contact_id=support.id,
        )


def test_reassign_contract_target_employee_must_be_active(db_session):
    manager = _create_employee(db_session, email="m5@test.com", role=Role.MANAGEMENT)
    sales_owner = _create_employee(db_session, email="s13@test.com", role=Role.SALES)
    inactive_sales = _create_employee(
        db_session, email="s14@test.com", role=Role.SALES, is_active=False
    )

    client = _create_client(
        db_session, email="c7@test.com", sales_contact_id=sales_owner.id
    )
    contract = _create_contract(
        db_session, client_id=client.id, sales_contact_id=sales_owner.id
    )

    with pytest.raises(ValidationError):
        reassign_contract(
            session=db_session,
            current_employee=manager,
            contract_id=contract.id,
            new_sales_contact_id=inactive_sales.id,
        )
