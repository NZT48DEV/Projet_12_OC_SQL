from __future__ import annotations

import pytest

from app.core.security import hash_password
from app.models.employee import Employee, Role
from app.services.client_service import (
    ClientAlreadyExistsError,
    PermissionDeniedError,
    ValidationError,
    create_client,
    list_clients,
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


def test_list_clients_returns_list(db_session):
    sales = _create_employee(db_session, email="sales@test.com", role=Role.SALES)
    result = list_clients(session=db_session, current_employee=sales)
    assert isinstance(result, list)


def test_create_client_denied_if_not_sales(db_session):
    mgmt = _create_employee(db_session, email="mgmt@test.com", role=Role.MANAGEMENT)

    with pytest.raises(PermissionDeniedError):
        create_client(
            session=db_session,
            current_employee=mgmt,
            first_name="A",
            last_name="B",
            email="client@test.com",
            phone=None,
            company_name=None,
        )


def test_create_client_validates_required_fields(db_session):
    sales = _create_employee(db_session, email="sales2@test.com", role=Role.SALES)

    with pytest.raises(ValidationError):
        create_client(
            session=db_session,
            current_employee=sales,
            first_name="",
            last_name="B",
            email="client@test.com",
            phone=None,
            company_name=None,
        )


def test_create_client_success_sets_sales_contact_id(db_session):
    sales = _create_employee(db_session, email="sales3@test.com", role=Role.SALES)

    client = create_client(
        session=db_session,
        current_employee=sales,
        first_name="Jean",
        last_name="Dupont",
        email="jean.dupont@client.test",
        phone="0612345678",
        company_name="Dupont SAS",
    )

    assert client.id is not None
    assert client.sales_contact_id == sales.id
    assert client.email == "jean.dupont@client.test"


def test_create_client_duplicate_email_raises(db_session):
    sales = _create_employee(db_session, email="sales4@test.com", role=Role.SALES)

    create_client(
        session=db_session,
        current_employee=sales,
        first_name="Jean",
        last_name="Dupont",
        email="dup@test.com",
        phone=None,
        company_name=None,
    )

    with pytest.raises(ClientAlreadyExistsError):
        create_client(
            session=db_session,
            current_employee=sales,
            first_name="Jean2",
            last_name="Dupont2",
            email="dup@test.com",
            phone=None,
            company_name=None,
        )
