from __future__ import annotations

from app.core import jwt_service, token_store
from app.core.security import hash_password
from app.epicevents import main
from app.models.employee import Employee, Role


def run_cli(monkeypatch, args: list[str]) -> None:
    """Simule sys.argv pour exécuter une commande CLI."""
    monkeypatch.setattr("sys.argv", ["epicevents"] + args)


def patch_sessions(monkeypatch, db_session) -> None:
    """
    Force les modules de commandes CLI à utiliser la session de test.
    IMPORTANT: après refactor, get_session est importé directement dans chaque module
    (from app.db.session import get_session), donc il faut patcher ces modules-là.
    """
    monkeypatch.setattr("app.cli.commands.auth.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.employees.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.clients.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.contracts.get_session", lambda: db_session)
    monkeypatch.setattr("app.cli.commands.events.get_session", lambda: db_session)


def patch_init_db(monkeypatch) -> None:
    """Désactive init_db() pendant les tests CLI pour éviter les effets de bord."""
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

    # 1) Force le mode fallback fichier (keyring désactivé)
    monkeypatch.setattr(token_store, "keyring", None)

    # 2) Tokens fallback dans tmp_path (vide)
    patch_tokens(monkeypatch, tmp_path)

    # 3) Session DB mockée
    patch_sessions(monkeypatch, db_session)

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out


def test_cli_login_success_saves_tokens(monkeypatch, tmp_path, capsys, db_session):
    """login sauvegarde des tokens locaux quand les identifiants sont valides."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)
    patch_sessions(monkeypatch, db_session)

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

    run_cli(monkeypatch, ["login", "cli-login@example.com", "Secret123!"])
    main()
    out = capsys.readouterr().out

    assert "✅ Connecté" in out
    assert token_store.load_access_token() is not None
    assert token_store.load_refresh_token() is not None


def test_cli_whoami_with_valid_tokens(monkeypatch, tmp_path, capsys, db_session):
    """whoami affiche l'utilisateur si les tokens sont valides."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)
    patch_sessions(monkeypatch, db_session)

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

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out

    assert emp.email in out
    assert "SUPPORT" in out


def test_cli_whoami_employee_missing(monkeypatch, tmp_path, capsys, db_session):
    """whoami échoue si le token est valide mais l'employé est absent en base."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)
    patch_sessions(monkeypatch, db_session)

    seed_tokens(monkeypatch, tmp_path, employee_id=999999999)

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out

    assert "Utilisateur introuvable" in out or "Non authentifié" in out


def test_cli_logout_clears_tokens(monkeypatch, tmp_path, capsys):
    """logout supprime les tokens locaux."""
    patch_init_db(monkeypatch)
    patch_tokens(monkeypatch, tmp_path)

    # On seed un fichier tokens.json
    seed_tokens(monkeypatch, tmp_path, employee_id=1)
    assert token_store.load_access_token() is not None

    run_cli(monkeypatch, ["logout"])
    main()
    out = capsys.readouterr().out

    assert "Déconnecté" in out
    assert token_store.load_access_token() is None
    assert token_store.load_refresh_token() is None
