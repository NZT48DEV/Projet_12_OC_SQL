from __future__ import annotations

import pytest

from app.core.security import hash_password
from app.models.employee import Employee, Role
from app.services.employee_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    reactivate_employee,
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
        deactivated_at=None,
        reactivated_at=None,
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def test_reactivate_employee_management_ok_sets_reactivated_at_and_clears_deactivated_at(
    db_session,
):
    """MANAGEMENT peut réactiver un employé désactivé et met à jour les timestamps."""
    manager = _create_employee(db_session, email="m@test.com", role=Role.MANAGEMENT)

    target = _create_employee(
        db_session,
        email="t@test.com",
        role=Role.SUPPORT,
        is_active=False,
    )
    # simuler une désactivation préalable (valeur non nulle)
    target.deactivated_at = (
        target.deactivated_at or None
    )  # explicite pour la lisibilité
    db_session.commit()
    db_session.refresh(target)

    updated = reactivate_employee(
        session=db_session,
        current_employee=manager,
        employee_id=target.id,
    )

    assert updated.is_active is True
    assert updated.deactivated_at is None
    assert updated.reactivated_at is not None


def test_reactivate_employee_forbidden_for_sales(db_session):
    """SALES ne peut pas réactiver un employé."""
    sales = _create_employee(db_session, email="s@test.com", role=Role.SALES)
    target = _create_employee(
        db_session, email="t2@test.com", role=Role.SUPPORT, is_active=False
    )

    with pytest.raises(PermissionDeniedError):
        reactivate_employee(
            session=db_session,
            current_employee=sales,
            employee_id=target.id,
        )


def test_reactivate_employee_not_found(db_session):
    """Réactivation échoue si l'employé n'existe pas."""
    manager = _create_employee(db_session, email="m2@test.com", role=Role.MANAGEMENT)

    with pytest.raises(NotFoundError):
        reactivate_employee(
            session=db_session,
            current_employee=manager,
            employee_id=999999999,
        )


def test_reactivate_employee_already_active(db_session):
    """Réactivation échoue si l'employé est déjà actif."""
    manager = _create_employee(db_session, email="m3@test.com", role=Role.MANAGEMENT)
    target = _create_employee(
        db_session, email="t3@test.com", role=Role.SUPPORT, is_active=True
    )

    with pytest.raises(ValidationError):
        reactivate_employee(
            session=db_session,
            current_employee=manager,
            employee_id=target.id,
        )
