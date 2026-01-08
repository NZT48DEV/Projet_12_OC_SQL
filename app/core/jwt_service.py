from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt


class TokenError(Exception):
    """Token invalide/expiré."""


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


def _secret() -> str:
    secret = os.getenv("EPICCRM_JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "EPICCRM_JWT_SECRET manquant. Définis-le dans tes variables d'environnement."
        )
    return secret


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"{name} doit être un entier (valeur actuelle: {raw!r})."
        ) from exc


def _get_bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _alg() -> str:
    # Lu dynamiquement pour respecter les changements d'env
    return os.getenv("EPICCRM_JWT_ALG", "HS256")


def _default_access_minutes() -> int:
    return _get_int_env("EPICCRM_JWT_ACCESS_MINUTES", 20)


def _default_refresh_days() -> int:
    return _get_int_env("EPICCRM_JWT_REFRESH_DAYS", 7)


def _default_rotate_refresh() -> bool:
    return _get_bool_env("EPICCRM_JWT_ROTATE_REFRESH", True)


def create_token_pair(
    employee_id: int,
    access_minutes: int | None = None,
    refresh_days: int | None = None,
) -> TokenPair:
    # IMPORTANT: valeurs calculées au moment de l'appel (pas à l'import)
    access_minutes = (
        _default_access_minutes() if access_minutes is None else access_minutes
    )
    refresh_days = _default_refresh_days() if refresh_days is None else refresh_days

    now = datetime.now(timezone.utc)

    access_payload: Dict[str, Any] = {
        "sub": str(employee_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=access_minutes)).timestamp()),
    }
    refresh_payload: Dict[str, Any] = {
        "sub": str(employee_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=refresh_days)).timestamp()),
    }

    algorithm = _alg()
    access_token = jwt.encode(access_payload, _secret(), algorithm=algorithm)
    refresh_token = jwt.encode(refresh_payload, _secret(), algorithm=algorithm)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def decode_and_validate(token: str, expected_type: str) -> Dict[str, Any]:
    """
    Décode + valide signature + exp.
    Vérifie aussi le champ "type" (access/refresh).
    """
    try:
        payload = jwt.decode(token, _secret(), algorithms=[_alg()])
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("Token expiré.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("Token invalide.") from exc

    token_type = payload.get("type")
    if token_type != expected_type:
        raise TokenError(f"Mauvais type de token (attendu {expected_type}).")

    return payload


def employee_id_from_access_token(token: str) -> int:
    payload = decode_and_validate(token, expected_type="access")
    return int(payload["sub"])


def refresh_access_token(
    refresh_token: str,
    access_minutes: int | None = None,
    rotate_refresh: bool | None = None,
) -> TokenPair:
    # IMPORTANT: valeurs calculées au moment de l'appel (pas à l'import)
    access_minutes = (
        _default_access_minutes() if access_minutes is None else access_minutes
    )
    rotate_refresh = (
        _default_rotate_refresh() if rotate_refresh is None else rotate_refresh
    )

    payload = decode_and_validate(refresh_token, expected_type="refresh")
    employee_id = int(payload["sub"])

    # Recommandé : rotation du refresh token
    if rotate_refresh:
        # refresh_days=None -> prendra la valeur de .env au moment de l'appel
        return create_token_pair(employee_id, access_minutes=access_minutes)

    # Sinon : on ne régénère que l'access token
    now = datetime.now(timezone.utc)
    access_payload: Dict[str, Any] = {
        "sub": str(employee_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=access_minutes)).timestamp()),
    }

    new_access = jwt.encode(access_payload, _secret(), algorithm=_alg())
    return TokenPair(access_token=new_access, refresh_token=refresh_token)
