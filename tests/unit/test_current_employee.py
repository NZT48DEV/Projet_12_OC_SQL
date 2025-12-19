from __future__ import annotations

import pytest

from app.core import jwt_service, token_store
from app.core.security import hash_password
from app.models.employee import Employee, Role
from app.services.current_employee import NotAuthenticatedError, get_current_employee


def _patch_token_path(monkeypatch, tmp_path):
    """Patch le chemin du fichier tokens.json (fichier temporaire)"""
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")


def _set_jwt_secret(monkeypatch):
    """Définit un secret JWT stable pour les tests."""
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")


def _seed_tokens(monkeypatch, tmp_path, employee_id: int):
    """Crée et sauvegarde une paire de tokens JWT pour un employee_id donné."""
    _set_jwt_secret(monkeypatch)
    _patch_token_path(monkeypatch, tmp_path)
    pair = jwt_service.create_token_pair(
        employee_id=employee_id, access_minutes=20, refresh_days=7
    )
    token_store.save_tokens(pair.access_token, pair.refresh_token)


def test_get_current_employee_not_authenticated(db_session, monkeypatch, tmp_path):
    """Lève NotAuthenticatedError si aucun access token n'est stocké."""
    _set_jwt_secret(monkeypatch)
    _patch_token_path(monkeypatch, tmp_path)

    with pytest.raises(NotAuthenticatedError):
        get_current_employee(db_session)


def test_get_current_employee_ok(db_session, monkeypatch, tmp_path):
    """Retourne l'employé si l'access token est valide et l'employé existe en base."""
    _set_jwt_secret(monkeypatch)
    _patch_token_path(monkeypatch, tmp_path)

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

    _seed_tokens(monkeypatch, tmp_path, emp.id)

    current = get_current_employee(db_session)
    assert current.id == emp.id
    assert current.email == emp.email


def test_get_current_employee_employee_not_found_raises(
    db_session, monkeypatch, tmp_path
):
    """Lève une erreur si le token est valide mais l'employé n'existe pas en base."""
    _seed_tokens(monkeypatch, tmp_path, employee_id=999999999)

    with pytest.raises(NotAuthenticatedError):
        get_current_employee(db_session)

    # Remarque: on ne teste pas la suppression du fichier, car le code ne le fait pas.
    assert token_store.load_access_token() is not None
