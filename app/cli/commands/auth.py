from __future__ import annotations

import argparse
import os

import jwt
import sentry_sdk

from app.cli.console import error, info, success
from app.core.jwt_service import TokenError, create_token_pair, refresh_access_token
from app.core.token_store import clear_tokens, load_refresh_token, save_tokens
from app.db.session import get_session
from app.services.auth_service import AuthenticationError, authenticate_employee
from app.services.current_employee import NotAuthenticatedError, get_current_employee


def _access_ttl_minutes(access_token: str) -> int:
    """
    Calcule la durée de validité (en minutes) à partir du JWT (exp - iat).
    On redécode avec la même clé/algorithme que l'app.
    """
    secret = os.getenv("EPICCRM_JWT_SECRET")
    if not secret:
        return 0

    alg = os.getenv("EPICCRM_JWT_ALG", "HS256")

    try:
        payload = jwt.decode(access_token, secret, algorithms=[alg])
        exp = int(payload.get("exp", 0))
        iat = int(payload.get("iat", 0))
        ttl_seconds = max(0, exp - iat)
        return ttl_seconds // 60
    except Exception:
        # Si jamais le decode échoue (cas rare), on ne bloque pas l'UX
        return 0


def cmd_login(args: argparse.Namespace) -> None:
    """Authentifie un employé et stocke les tokens JWT localement."""
    session = get_session()
    try:
        employee = authenticate_employee(session, args.email, args.password)

        # IMPORTANT: ne pas passer 20/7 en dur -> laisse jwt_service lire le .env
        token_pair = create_token_pair(employee_id=employee.id)

        save_tokens(token_pair.access_token, token_pair.refresh_token)

        success(
            f"Connecté : {employee.first_name} {employee.last_name} "
            f"(role={employee.role})"
        )

        ttl_min = _access_ttl_minutes(token_pair.access_token)
        if ttl_min > 0:
            info(f"Access token valide {ttl_min} minutes.")
        else:
            # fallback si decode impossible
            info("Access token généré.")
        info("Utilise `refresh-token` si le token expire.")
    except AuthenticationError as exc:
        error(str(exc))
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        error(f"Erreur inattendue lors du login : {exc}")
    finally:
        session.close()


def cmd_logout(_: argparse.Namespace) -> None:
    """Supprime les tokens locaux (déconnexion)."""
    clear_tokens()
    success("Déconnecté.")


def cmd_refresh_token(_: argparse.Namespace) -> None:
    """Régénère un access token via le refresh token local."""
    refresh_token = load_refresh_token()
    if not refresh_token:
        error("Aucun refresh token trouvé. Faites `login`.")
        return

    try:
        # IMPORTANT: ne pas passer 20 en dur -> laisse jwt_service lire le .env
        token_pair = refresh_access_token(
            refresh_token=refresh_token,
            rotate_refresh=True,
        )

        save_tokens(token_pair.access_token, token_pair.refresh_token)

        ttl_min = _access_ttl_minutes(token_pair.access_token)
        if ttl_min > 0:
            success(f"Token rafraîchi avec succès ({ttl_min} min).")
        else:
            success("Token rafraîchi avec succès.")
    except TokenError as exc:
        error(f"Impossible de rafraîchir le token : {exc}")
        info("Faites `login`.")
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        error(f"Erreur inattendue lors du refresh token : {exc}")


def cmd_whoami(_: argparse.Namespace) -> None:
    """Affiche l'utilisateur actuellement authentifié (via access token)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        info(
            f"👤 {employee.first_name} {employee.last_name} "
            f"(email={employee.email}, role={employee.role})"
        )
    except NotAuthenticatedError as exc:
        error(f"❌ {exc}")
    finally:
        session.close()
