from __future__ import annotations

from app.core.security import hash_password
from app.models.employee import Employee, Role
from app.services.employee_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    deactivate_employee,
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
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def test_deactivate_employee_management_ok(db_session):
    """MANAGEMENT peut désactiver un employé actif."""
    manager = _create_employee(db_session, email="m@test.com", role=Role.MANAGEMENT)
    target = _create_employee(db_session, email="t@test.com", role=Role.SUPPORT)

    updated = deactivate_employee(
        session=db_session,
        current_employee=manager,
        employee_id=target.id,
    )

    assert updated.is_active is False
    assert updated.deactivated_at is not None


def test_deactivate_employee_forbidden_for_sales(db_session):
    """SALES ne peut pas désactiver un employé."""
    sales = _create_employee(db_session, email="s@test.com", role=Role.SALES)
    target = _create_employee(db_session, email="t2@test.com", role=Role.SUPPORT)

    try:
        deactivate_employee(db_session, sales, target.id)
        assert False, "PermissionDeniedError attendu"
    except PermissionDeniedError:
        assert True


def test_deactivate_employee_cannot_self_delete(db_session):
    """Un MANAGEMENT ne peut pas se désactiver lui-même."""
    manager = _create_employee(db_session, email="m2@test.com", role=Role.MANAGEMENT)

    try:
        deactivate_employee(db_session, manager, manager.id)
        assert False, "ValidationError attendu"
    except ValidationError:
        assert True


def test_deactivate_employee_not_found(db_session):
    """Désactivation échoue si l'employé n'existe pas."""
    manager = _create_employee(db_session, email="m3@test.com", role=Role.MANAGEMENT)

    try:
        deactivate_employee(db_session, manager, employee_id=999999)
        assert False, "NotFoundError attendu"
    except NotFoundError:
        assert True


def test_deactivate_employee_already_disabled(db_session):
    """Désactivation échoue si l'employé est déjà désactivé."""
    manager = _create_employee(db_session, email="m4@test.com", role=Role.MANAGEMENT)
    target = _create_employee(db_session, email="t3@test.com", role=Role.SUPPORT)

    # 1ère désactivation OK
    deactivate_employee(db_session, manager, target.id)

    # 2ème désactivation => ValidationError
    try:
        deactivate_employee(db_session, manager, target.id)
        assert False, "ValidationError attendu"
    except ValidationError:
        assert True
