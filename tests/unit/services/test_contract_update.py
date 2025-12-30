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
    update_contract,
)


@pytest.fixture()
def sales(db_session) -> Employee:
    e = Employee(
        first_name="Sales",
        last_name="One",
        email="sales1@test.com",
        role=Role.SALES,
        password_hash=hash_password("Password123!"),
    )
    db_session.add(e)
    db_session.commit()
    db_session.refresh(e)
    return e


@pytest.fixture()
def sales2(db_session) -> Employee:
    e = Employee(
        first_name="Sales",
        last_name="Two",
        email="sales2@test.com",
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
def contract(db_session, client, sales) -> Contract:
    ct = Contract(
        client_id=client.id,
        sales_contact_id=sales.id,
        total_amount=Decimal("1000.00"),
        amount_due=Decimal("200.00"),
        is_signed=False,
    )
    db_session.add(ct)
    db_session.commit()
    db_session.refresh(ct)
    return ct


def test_update_contract_not_found(db_session, manager):
    """La mise à jour d'un contrat inexistant doit échouer."""
    with pytest.raises(NotFoundError):
        update_contract(
            session=db_session,
            current_employee=manager,
            contract_id=999999,
            total_amount=Decimal("10.00"),
        )


def test_update_contract_sales_can_update_own(db_session, sales, contract):
    """Un SALES peut modifier un contrat dont il est responsable."""
    updated = update_contract(
        session=db_session,
        current_employee=sales,
        contract_id=contract.id,
        amount_due=Decimal("150.00"),
    )
    assert updated.amount_due == Decimal("150.00")


def test_update_contract_sales_cannot_update_others(db_session, sales2, contract):
    """Un SALES ne peut pas modifier le contrat d'un autre commercial."""
    with pytest.raises(PermissionDeniedError):
        update_contract(
            session=db_session,
            current_employee=sales2,
            contract_id=contract.id,
            total_amount=Decimal("2000.00"),
        )


def test_update_contract_total_must_be_positive(db_session, manager, contract):
    """Le montant total d'un contrat doit être strictement positif."""
    with pytest.raises(ValidationError):
        update_contract(
            session=db_session,
            current_employee=manager,
            contract_id=contract.id,
            total_amount=Decimal("0"),
        )


def test_update_contract_amount_due_cannot_be_negative(db_session, manager, contract):
    """Le montant restant dû ne peut pas être négatif."""
    with pytest.raises(ValidationError):
        update_contract(
            session=db_session,
            current_employee=manager,
            contract_id=contract.id,
            amount_due=Decimal("-1"),
        )


def test_update_contract_due_cannot_exceed_total_final_values(
    db_session, manager, contract
):
    """Le montant dû ne peut pas dépasser le montant total final."""
    with pytest.raises(ValidationError):
        update_contract(
            session=db_session,
            current_employee=manager,
            contract_id=contract.id,
            amount_due=Decimal("1200.00"),
        )


def test_update_contract_due_ok_if_total_updated_too(db_session, manager, contract):
    """La mise à jour est valide si le montant total couvre le montant dû."""
    updated = update_contract(
        session=db_session,
        current_employee=manager,
        contract_id=contract.id,
        total_amount=Decimal("1500.00"),
        amount_due=Decimal("1200.00"),
    )
    assert updated.total_amount == Decimal("1500.00")
    assert updated.amount_due == Decimal("1200.00")
