from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _token_path() -> Path:
    """
    Chemin du fichier local contenant les tokens.
    Stockage : ~/.epiccrm/tokens.json
    """
    folder = Path.home() / ".epiccrm"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "tokens.json"


def save_tokens(access_token: str, refresh_token: str) -> None:
    """Sauvegarde les tokens localement."""
    _token_path().write_text(
        json.dumps({"access_token": access_token, "refresh_token": refresh_token}),
        encoding="utf-8",
    )


def load_access_token() -> Optional[str]:
    """Charge l'access_token local, ou None."""
    path = _token_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("access_token")


def load_refresh_token() -> Optional[str]:
    """Charge le refresh_token local, ou None."""
    path = _token_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("refresh_token")


def clear_tokens() -> None:
    """Supprime le fichier local de tokens s'il existe."""
    path = _token_path()
    if path.exists():
        path.unlink()
