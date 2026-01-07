from __future__ import annotations

from app.core import jwt_service, token_store
from app.core.security import hash_password
from app.models.employee import Employee, Role
from tests.integration.cli._click_runner import invoke_cli


def patch_sessions(monkeypatch, db_session) -> None:
    """Force les modules de commandes CLI à utiliser la session de test."""
    monkeypatch.setattr("app.cli.commands.auth.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.employees.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.clients.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.contracts.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.events.get_session", lambda: db_session)


def patch_init_db(monkeypatch) -> None:
    """Désactive init_db() pendant les tests CLI."""
    monkeypatch.setattr("app.epicevents.init_db", lambda: None)


def patch_tokens(monkeypatch, tmp_path) -> None:
    """Force le fichier tokens.json à être stocké dans un répertoire temporaire."""
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")


def seed_tokens(monkeypatch, tmp_path, employee_id: int) -> None:
    """Écrit un fichier tokens.json valide pour un employee_id donné."""
    patch_tokens(monkeypatch, tmp_path)
    pair = jwt_service.create_token_pair(
        employee_id=employee_id,
        access_minutes=20,
        refresh_days=7,
    )
    token_store.save_tokens(pair.access_token, pair.refresh_token)


def test_cli_whoami_not_authenticated(monkeypatch, tmp_path, capsys, db_session):
    """whoami affiche un message si aucun token n'est présent."""
    patch_init_db(monkeypatch)

    monkeypatch.setattr(token_store, "keyring", None)
    patch_tokens(monkeypatch, tmp_path)
    patch_sessions(monkeypatch, db_session)

    result = invoke_cli(["whoami"])

    assert "Non authentifié" in result.output


def test_cli_login_success_saves_tokens(monkeypatch, tmp_path, capsys, db_session):
    """login sauvegarde des tokens locaux quand les identifiants sont valides."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)
    patch_sessions(monkeypatch, db_session)
    monkeypatch.setattr(token_store, "keyring", None)

    emp = Employee(
        first_name="Anthony",
        last_name="Test",
        email="cli-login@example.com",
        role=Role.MANAGEMENT,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    result = invoke_cli(["login", "cli-login@example.com", "Secret123!"])

    assert "✅ Connecté" in result.output
    assert token_store.load_access_token() is not None
    assert token_store.load_refresh_token() is not None


def test_cli_whoami_with_valid_tokens(monkeypatch, tmp_path, capsys, db_session):
    """whoami affiche l'utilisateur si les tokens sont valides."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)
    patch_sessions(monkeypatch, db_session)
    monkeypatch.setattr(token_store, "keyring", None)

    emp = Employee(
        first_name="Anthony",
        last_name="Test",
        email="cli-whoami@example.com",
        role=Role.SUPPORT,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    seed_tokens(monkeypatch, tmp_path, emp.id)

    result = invoke_cli(["whoami"])

    assert emp.email in result.output
    assert "SUPPORT" in result.output


def test_cli_whoami_employee_missing(monkeypatch, tmp_path, capsys, db_session):
    """whoami échoue si le token est valide mais l'employé est absent en base."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)
    patch_sessions(monkeypatch, db_session)
    monkeypatch.setattr(token_store, "keyring", None)

    seed_tokens(monkeypatch, tmp_path, employee_id=999999999)

    result = invoke_cli(["whoami"])

    assert (
        "Utilisateur introuvable" in result.output or "Non authentifié" in result.output
    )


def test_cli_logout_clears_tokens(monkeypatch, tmp_path, capsys):
    """logout supprime les tokens locaux."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)
    monkeypatch.setattr(token_store, "keyring", None)

    seed_tokens(monkeypatch, tmp_path, employee_id=1)
    assert token_store.load_access_token() is not None

    result = invoke_cli(["logout"])

    assert "Déconnecté" in result.output
    assert token_store.load_access_token() is None
    assert token_store.load_refresh_token() is None
