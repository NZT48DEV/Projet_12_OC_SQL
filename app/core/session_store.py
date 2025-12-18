from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _session_path() -> Path:
    """
    Retourne le chemin du fichier de session local.

    Le fichier est stocké dans le dossier utilisateur : ~/.epiccrm/session.json
    Le dossier ~/.epiccrm est créé s'il n'existe pas.
    """
    folder = Path.home() / ".epiccrm"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "session.json"


def save_current_employee(employee_id: int) -> None:
    """
    Enregistre localement l'identifiant de l'employé authentifié.

    Args:
        employee_id: identifiant de l'employé à stocker.
    """
    _session_path().write_text(
        json.dumps({"employee_id": employee_id}), encoding="utf-8"
    )


def load_current_employee_id() -> Optional[int]:
    """
    Charge l'identifiant de l'employé courant depuis le fichier de session.

    Returns:
        L'identifiant de l'employé si présent, sinon None.
    """
    path = _session_path()
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    value = data.get("employee_id")
    return int(value) if value is not None else None


def clear_session() -> None:
    """Supprime le fichier de session local s'il existe."""
    path = _session_path()
    if path.exists():
        path.unlink()
