from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core import jwt_service


@pytest.fixture(autouse=True)
def _set_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """Définit un secret JWT stable pour garantir des tests déterministes."""
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")


def _encode(payload: dict) -> str:
    """Encode un JWT de test avec l'algorithme et le secret utilisés dans la suite de tests."""
    return jwt.encode(payload, "test_secret__do_not_use_in_prod", algorithm="HS256")


def test_create_token_pair_creates_valid_access_and_refresh_tokens() -> None:
    """Vérifie que create_token_pair génère un access token et un refresh token valides."""
    pair = jwt_service.create_token_pair(
        employee_id=42, access_minutes=20, refresh_days=7
    )

    access_payload = jwt_service.decode_and_validate(
        pair.access_token, expected_type="access"
    )
    refresh_payload = jwt_service.decode_and_validate(
        pair.refresh_token, expected_type="refresh"
    )

    assert access_payload["sub"] == "42"
    assert refresh_payload["sub"] == "42"
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    assert "exp" in access_payload
    assert "iat" in access_payload


def test_employee_id_from_access_token_returns_int_id() -> None:
    """Vérifie que employee_id_from_access_token retourne l'identifiant employé en int."""
    pair = jwt_service.create_token_pair(
        employee_id=7, access_minutes=20, refresh_days=7
    )

    employee_id = jwt_service.employee_id_from_access_token(pair.access_token)

    assert employee_id == 7


def test_decode_and_validate_raises_if_wrong_expected_type() -> None:
    """Vérifie que decode_and_validate refuse un token si son type ne correspond pas au type attendu."""
    pair = jwt_service.create_token_pair(
        employee_id=7, access_minutes=20, refresh_days=7
    )

    with pytest.raises(jwt_service.TokenError) as excinfo:
        jwt_service.decode_and_validate(pair.refresh_token, expected_type="access")

    assert "Mauvais type de token" in str(excinfo.value)


def test_employee_id_from_access_token_raises_if_token_is_refresh() -> None:
    """Vérifie que employee_id_from_access_token refuse un refresh token."""
    pair = jwt_service.create_token_pair(
        employee_id=7, access_minutes=20, refresh_days=7
    )

    with pytest.raises(jwt_service.TokenError) as excinfo:
        jwt_service.employee_id_from_access_token(pair.refresh_token)

    assert "Mauvais type de token" in str(excinfo.value)


def test_decode_and_validate_raises_if_token_expired() -> None:
    """Vérifie que decode_and_validate lève une TokenError lorsque le token est expiré."""
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "99",
        "type": "access",
        "iat": int((now - timedelta(minutes=10)).timestamp()),
        "exp": int((now - timedelta(minutes=1)).timestamp()),
    }
    token = _encode(expired_payload)

    with pytest.raises(jwt_service.TokenError) as excinfo:
        jwt_service.decode_and_validate(token, expected_type="access")

    assert "expiré" in str(excinfo.value).lower()


def test_decode_and_validate_raises_if_token_invalid_signature() -> None:
    """Vérifie que decode_and_validate lève une TokenError si la signature du token est invalide."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=20)).timestamp()),
    }
    token_wrong_secret = jwt.encode(payload, "wrong_secret", algorithm="HS256")

    with pytest.raises(jwt_service.TokenError) as excinfo:
        jwt_service.decode_and_validate(token_wrong_secret, expected_type="access")

    assert "invalide" in str(excinfo.value).lower()


def test_refresh_access_token_without_rotation_keeps_same_refresh_token() -> None:
    """Vérifie que refresh_access_token sans rotation conserve le refresh token d'origine."""
    pair = jwt_service.create_token_pair(
        employee_id=123, access_minutes=20, refresh_days=7
    )

    new_pair = jwt_service.refresh_access_token(
        refresh_token=pair.refresh_token,
        access_minutes=20,
        rotate_refresh=False,
    )

    assert new_pair.refresh_token == pair.refresh_token
    assert jwt_service.employee_id_from_access_token(new_pair.access_token) == 123


def test_refresh_access_token_with_rotation_returns_valid_tokens() -> None:
    """Vérifie que refresh_access_token avec rotation renvoie une nouvelle paire de tokens valide."""
    pair = jwt_service.create_token_pair(
        employee_id=123, access_minutes=20, refresh_days=7
    )

    new_pair = jwt_service.refresh_access_token(
        refresh_token=pair.refresh_token,
        access_minutes=20,
        rotate_refresh=True,
    )

    access_payload = jwt_service.decode_and_validate(
        new_pair.access_token, expected_type="access"
    )
    refresh_payload = jwt_service.decode_and_validate(
        new_pair.refresh_token, expected_type="refresh"
    )

    assert access_payload["sub"] == "123"
    assert refresh_payload["sub"] == "123"
