from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

try:
    import keyring  # type: ignore
except Exception:  # pragma: no cover
    keyring = None


# Nom "service" dans le coffre OS (Keychain / Credential Manager / Secret Service)
_KEYRING_SERVICE = "epiccrm-cli"
_KEYRING_ACCESS = "access_token"
_KEYRING_REFRESH = "refresh_token"


def _token_folder() -> Path:
    """
    Dossier local pour fallback fichier.
    Stockage : ~/.epiccrm/
    """
    folder = Path.home() / ".epiccrm"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _token_path() -> Path:
    """
    Chemin du fichier local contenant les tokens (fallback).
    Stockage : ~/.epiccrm/tokens.json
    """
    return _token_folder() / "tokens.json"


def _best_effort_secure_file(path: Path) -> None:
    """
    Tente de restreindre les permissions du fichier (best effort).
    - Unix: chmod 600
    - Windows: chmod n'applique pas les ACL NTFS; on fait au mieux sans dépendances.
    """
    try:
        os.chmod(path, 0o600)
    except Exception:
        # Sur certains environnements (Windows / FS particuliers), chmod peut échouer.
        pass


def _keyring_available() -> bool:
    return keyring is not None


def _keyring_set(access_token: str, refresh_token: str) -> None:
    keyring.set_password(_KEYRING_SERVICE, _KEYRING_ACCESS, access_token)
    keyring.set_password(_KEYRING_SERVICE, _KEYRING_REFRESH, refresh_token)


def _keyring_get(name: str) -> Optional[str]:
    return keyring.get_password(_KEYRING_SERVICE, name)


def _keyring_delete(name: str) -> None:
    # keyring peut lever si l'entrée n'existe pas selon les backends
    try:
        keyring.delete_password(_KEYRING_SERVICE, name)
    except Exception:
        pass


def save_tokens(access_token: str, refresh_token: str) -> None:
    """
    Sauvegarde les tokens.
    Stratégie:
    1) Coffre sécurisé OS via keyring (si dispo)
    2) Fallback fichier local (tokens.json) avec permissions restreintes (best effort)
    """
    if _keyring_available():
        print("KEYRING available =", _keyring_available())
        try:
            _keyring_set(access_token, refresh_token)
            print("Tokens saved in keyring")
            return
        except Exception:
            # Backend keyring absent/mal configuré -> fallback fichier
            pass

    path = _token_path()
    path.write_text(
        json.dumps({"access_token": access_token, "refresh_token": refresh_token}),
        encoding="utf-8",
    )
    _best_effort_secure_file(path)


def load_access_token() -> Optional[str]:
    """Charge l'access_token, ou None."""
    if _keyring_available():
        try:
            token = _keyring_get(_KEYRING_ACCESS)
            if token:
                return token
        except Exception:
            pass

    path = _token_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("access_token")


def load_refresh_token() -> Optional[str]:
    """Charge le refresh_token, ou None."""
    if _keyring_available():
        try:
            token = _keyring_get(_KEYRING_REFRESH)
            if token:
                return token
        except Exception:
            pass

    path = _token_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
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
        except Exception:
            pass

    path = _token_path()
    if path.exists():
        path.unlink()
