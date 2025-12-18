"""Tests unitaires pour la récupération de l'employé courant (session + DB)."""

import json

import pytest

from app.core import session_store
from app.core.security import hash_password
from app.models.employee import Employee, Role
from app.services.current_employee import NotAuthenticatedError, get_current_employee


def test_get_current_employee_not_authenticated(db_session, monkeypatch, tmp_path):
    """Lève NotAuthenticatedError si aucun employee_id n'est stocké."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )

    with pytest.raises(NotAuthenticatedError):
        get_current_employee(db_session)


def test_get_current_employee_ok(db_session, monkeypatch, tmp_path):
    """Retourne l'employé si la session locale et la DB sont cohérentes."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )

    emp = Employee(
        first_name="Test",
        last_name="User",
        email="test-current@example.com",
        role=Role.MANAGEMENT,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    (tmp_path / "session.json").write_text(
        json.dumps({"employee_id": emp.id}),
        encoding="utf-8",
    )

    current = get_current_employee(db_session)
    assert current.id == emp.id
    assert current.email == emp.email


def test_get_current_employee_invalid_session_clears_file(
    db_session, monkeypatch, tmp_path
):
    """Supprime la session locale si l'employee_id ne correspond à aucun employé."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )

    path = tmp_path / "session.json"
    path.write_text(json.dumps({"employee_id": 999999999}), encoding="utf-8")

    with pytest.raises(NotAuthenticatedError):
        get_current_employee(db_session)

    assert not path.exists()
