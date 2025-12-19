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


_ALG = "HS256"


def create_token_pair(
    employee_id: int, access_minutes: int = 20, refresh_days: int = 7
) -> TokenPair:
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

    access_token = jwt.encode(access_payload, _secret(), algorithm=_ALG)
    refresh_token = jwt.encode(refresh_payload, _secret(), algorithm=_ALG)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def decode_and_validate(token: str, expected_type: str) -> Dict[str, Any]:
    """
    Décode + valide signature + exp.
    Vérifie aussi le champ "type" (access/refresh).
    """
    try:
        payload = jwt.decode(token, _secret(), algorithms=[_ALG])
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
    refresh_token: str, access_minutes: int = 20, rotate_refresh: bool = True
) -> TokenPair:
    payload = decode_and_validate(refresh_token, expected_type="refresh")
    employee_id = int(payload["sub"])

    # Recommandé : rotation du refresh token
    if rotate_refresh:
        return create_token_pair(employee_id, access_minutes=access_minutes)

    # Sinon : on ne régénère que l'access token
    now = datetime.now(timezone.utc)
    access_payload: Dict[str, Any] = {
        "sub": str(employee_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=access_minutes)).timestamp()),
    }
    new_access = jwt.encode(access_payload, _secret(), algorithm=_ALG)
    return TokenPair(access_token=new_access, refresh_token=refresh_token)
