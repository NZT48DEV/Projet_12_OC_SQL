from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

try:
    import keyring  # type: ignore
except Exception:  # pragma: no cover
    keyring = None


logger = logging.getLogger(__name__)

# Nom "service" dans le coffre OS (Keychain / Credential Manager / Secret Service)
_KEYRING_SERVICE = "epiccrm-cli"
_KEYRING_ACCESS = "access_token"
_KEYRING_REFRESH = "refresh_token"


def _token_folder() -> Path:
    """Dossier local pour fallback fichier (~/.epiccrm/)."""
    folder = Path.home() / ".epiccrm"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _token_path() -> Path:
    """Chemin du fichier local contenant les tokens (~/.epiccrm/tokens.json)."""
    return _token_folder() / "tokens.json"


def _best_effort_secure_file(path: Path) -> None:
    """Tente de restreindre les permissions du fichier (best effort)."""
    try:
        os.chmod(path, 0o600)
    except Exception:
        logger.debug("Impossible d'appliquer chmod 600 sur %s", path)


def _keyring_available() -> bool:
    return keyring is not None


def _keyring_set(access_token: str, refresh_token: str) -> None:
    keyring.set_password(_KEYRING_SERVICE, _KEYRING_ACCESS, access_token)
    keyring.set_password(_KEYRING_SERVICE, _KEYRING_REFRESH, refresh_token)


def _keyring_get(name: str) -> Optional[str]:
    return keyring.get_password(_KEYRING_SERVICE, name)


def _keyring_delete(name: str) -> None:
    try:
        keyring.delete_password(_KEYRING_SERVICE, name)
    except Exception:
        logger.debug("Suppression keyring ignorée pour %s", name)


def save_tokens(access_token: str, refresh_token: str) -> None:
    """
    Sauvegarde les tokens.
    Stratégie:
    1) Coffre sécurisé OS via keyring (si dispo)
    2) Fallback fichier local
    """
    if _keyring_available():
        try:
            _keyring_set(access_token, refresh_token)
            logger.info("Tokens sauvegardés via keyring (backend OS)")
            return
        except Exception as exc:
            logger.warning(
                "Keyring disponible mais échec d'écriture (%s) → fallback fichier",
                exc,
            )

    path = _token_path()
    path.write_text(
        json.dumps({"access_token": access_token, "refresh_token": refresh_token}),
        encoding="utf-8",
    )
    _best_effort_secure_file(path)
    logger.info("Tokens sauvegardés via fichier local (%s)", path)


def load_access_token() -> Optional[str]:
    """Charge l'access_token, ou None."""
    if _keyring_available():
        try:
            token = _keyring_get(_KEYRING_ACCESS)
            if token:
                logger.debug("Access token chargé depuis keyring")
                return token
        except Exception as exc:
            logger.warning("Erreur lecture access token depuis keyring (%s)", exc)

    path = _token_path()
    if not path.exists():
        logger.debug("Aucun access token trouvé (ni keyring, ni fichier)")
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    logger.debug("Access token chargé depuis fichier (%s)", path)
    return data.get("access_token")


def load_refresh_token() -> Optional[str]:
    """Charge le refresh_token, ou None."""
    if _keyring_available():
        try:
            token = _keyring_get(_KEYRING_REFRESH)
            if token:
                logger.debug("Refresh token chargé depuis keyring")
                return token
        except Exception as exc:
            logger.warning("Erreur lecture refresh token depuis keyring (%s)", exc)

    path = _token_path()
    if not path.exists():
        logger.debug("Aucun refresh token trouvé (ni keyring, ni fichier)")
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    logger.debug("Refresh token chargé depuis fichier (%s)", path)
    return data.get("refresh_token")


def clear_tokens() -> None:
    """
    Supprime les tokens.
    - Efface le coffre OS si possible
    - Efface le fichier fallback si présent
    """
    if _keyring_available():
        try:
            _keyring_delete(_KEYRING_ACCESS)
            _keyring_delete(_KEYRING_REFRESH)
            logger.info("Tokens supprimés du keyring")
        except Exception as exc:
            logger.warning("Erreur suppression keyring (%s)", exc)

    path = _token_path()
    if path.exists():
        path.unlink()
        logger.info("Fichier de tokens supprimé (%s)", path)
