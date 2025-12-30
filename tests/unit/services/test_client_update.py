from __future__ import annotations

import pytest

from app.core.security import hash_password
from app.models.client import Client
from app.models.employee import Employee, Role
from app.services.client_service import (
    ClientAlreadyExistsError,
    PermissionDeniedError,
    ValidationError,
    update_client,
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
def client_owned_by_sales(db_session, sales) -> Client:
    c = Client(
        first_name="John",
        last_name="Doe",
        email="john.doe@test.com",
        phone=None,
        company_name="ACME",
        sales_contact_id=sales.id,
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


def test_update_client_support_forbidden(db_session, support, client_owned_by_sales):
    """Un utilisateur SUPPORT ne peut jamais modifier un client."""
    with pytest.raises(PermissionDeniedError):
        update_client(
            session=db_session,
            current_employee=support,
            client_id=client_owned_by_sales.id,
            first_name="NewName",
        )


def test_update_client_sales_can_update_own_client(
    db_session, sales, client_owned_by_sales
):
    """Un SALES peut modifier un client dont il est le contact commercial."""
    updated = update_client(
        session=db_session,
        current_employee=sales,
        client_id=client_owned_by_sales.id,
        phone="  0600000000  ",
        company_name="  NewCo  ",
    )
    assert updated.phone == "0600000000"
    assert updated.company_name == "NewCo"


def test_update_client_sales_cannot_update_other_sales_client(
    db_session, sales2, client_owned_by_sales
):
    """Un SALES ne peut pas modifier un client appartenant à un autre commercial."""
    with pytest.raises(PermissionDeniedError):
        update_client(
            session=db_session,
            current_employee=sales2,
            client_id=client_owned_by_sales.id,
            last_name="Hack",
        )


def test_update_client_management_can_update_any(
    db_session, manager, client_owned_by_sales
):
    """Un MANAGEMENT peut modifier n'importe quel client."""
    updated = update_client(
        session=db_session,
        current_employee=manager,
        client_id=client_owned_by_sales.id,
        last_name="Changed",
    )
    assert updated.last_name == "Changed"


def test_update_client_email_must_be_unique(db_session, manager, sales):
    """L'email d'un client doit rester unique lors d'une mise à jour."""
    # client A
    c1 = Client(
        first_name="A",
        last_name="A",
        email="a@test.com",
        phone=None,
        company_name=None,
        sales_contact_id=sales.id,
    )
    # client B
    c2 = Client(
        first_name="B",
        last_name="B",
        email="b@test.com",
        phone=None,
        company_name=None,
        sales_contact_id=sales.id,
    )
    db_session.add_all([c1, c2])
    db_session.commit()
    db_session.refresh(c2)

    with pytest.raises(ClientAlreadyExistsError):
        update_client(
            session=db_session,
            current_employee=manager,
            client_id=c2.id,
            email="a@test.com",
        )


def test_update_client_first_name_cannot_be_empty(
    db_session, manager, client_owned_by_sales
):
    """Le prénom ne peut pas être vide lors d'une mise à jour."""
    with pytest.raises(ValidationError):
        update_client(
            session=db_session,
            current_employee=manager,
            client_id=client_owned_by_sales.id,
            first_name="   ",
        )
