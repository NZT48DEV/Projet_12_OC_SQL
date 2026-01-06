from __future__ import annotations

import argparse

import sentry_sdk

from app.core.jwt_service import TokenError, create_token_pair, refresh_access_token
from app.core.token_store import clear_tokens, load_refresh_token, save_tokens
from app.db.session import get_session
from app.services.auth_service import AuthenticationError, authenticate_employee
from app.services.current_employee import NotAuthenticatedError, get_current_employee


def cmd_login(args: argparse.Namespace) -> None:
    """Authentifie un employé et stocke les tokens JWT localement."""
    session = get_session()
    try:
        employee = authenticate_employee(session, args.email, args.password)

        token_pair = create_token_pair(
            employee_id=employee.id,
            access_minutes=20,
            refresh_days=7,
        )
        save_tokens(token_pair.access_token, token_pair.refresh_token)

        print(
            f"✅ Connecté : {employee.first_name} {employee.last_name} "
            f"(role={employee.role})"
        )
        print("ℹ️  Access token valide 20 minutes.")
        print("ℹ️  Utilise `refresh-token` si le token expire.")
    except AuthenticationError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        print(f"❌ Erreur inattendue lors du login : {exc}")
    finally:
        session.close()


def cmd_logout(_: argparse.Namespace) -> None:
    """Supprime les tokens locaux (déconnexion)."""
    clear_tokens()
    print("✅ Déconnecté.")


def cmd_refresh_token(_: argparse.Namespace) -> None:
    """Régénère un access token via le refresh token local."""
    refresh_token = load_refresh_token()
    if not refresh_token:
        print("❌ Aucun refresh token trouvé. Faites `login`.")
        return

    try:
        token_pair = refresh_access_token(
            refresh_token=refresh_token,
            access_minutes=20,
            rotate_refresh=True,
        )
        save_tokens(token_pair.access_token, token_pair.refresh_token)
        print("✅ Token rafraîchi avec succès.")
    except TokenError as exc:
        print(f"❌ Impossible de rafraîchir le token : {exc}")
        print("➡️ Faites `login`.")
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        print(f"❌ Erreur inattendue lors du refresh token : {exc}")


def cmd_whoami(_: argparse.Namespace) -> None:
    """Affiche l'utilisateur actuellement authentifié (via access token)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        print(
            f"👤 {employee.first_name} {employee.last_name} "
            f"(email={employee.email}, role={employee.role})"
        )
    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()
