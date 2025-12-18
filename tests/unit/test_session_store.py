"""Tests unitaires pour le stockage local de session."""

from pathlib import Path

from app.core import session_store


def test_save_and_load_current_employee_id(monkeypatch, tmp_path):
    """Sauvegarde puis relit l'employee_id depuis le fichier de session."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )

    session_store.save_current_employee(123)
    assert session_store.load_current_employee_id() == 123


def test_clear_session(monkeypatch, tmp_path):
    """Supprime la session et retourne None au chargement."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )

    session_store.save_current_employee(1)
    session_store.clear_session()

    assert session_store.load_current_employee_id() is None


def test__session_path_creates_folder_and_returns_file(monkeypatch, tmp_path):
    """Crée le dossier ~/.epiccrm et retourne le chemin session.json."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    path = session_store._session_path()

    assert path == tmp_path / ".epiccrm" / "session.json"
    assert (tmp_path / ".epiccrm").exists()
    assert (tmp_path / ".epiccrm").is_dir()
