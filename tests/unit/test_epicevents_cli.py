from __future__ import annotations

from app.core import jwt_service, token_store
from app.core.security import hash_password
from app.epicevents import main
from app.models.employee import Employee, Role


def run_cli(monkeypatch, args: list[str]):
    """Simule sys.argv pour exécuter une commande CLI."""
    monkeypatch.setattr("sys.argv", ["epicevents"] + args)


def patch_sessionlocal(monkeypatch, db_session):
    """Force epicevents.SessionLocal() à renvoyer la session de test."""
    monkeypatch.setattr("app.epicevents.get_session", lambda: db_session)


def patch_tokens(monkeypatch, tmp_path):
    """Force le fichier tokens.json à être stocké dans un répertoire temporaire."""
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")


def seed_tokens(monkeypatch, tmp_path, employee_id: int):
    """Écrit un fichier tokens.json valide pour un employee_id donné."""
    patch_tokens(monkeypatch, tmp_path)
    pair = jwt_service.create_token_pair(
        employee_id=employee_id, access_minutes=20, refresh_days=7
    )
    token_store.save_tokens(pair.access_token, pair.refresh_token)


def test_cli_whoami_not_authenticated(monkeypatch, tmp_path, capsys, db_session):
    """whoami affiche un message si aucun token n'est présent."""
    # 1) Force le mode fallback fichier (keyring désactivé)

    monkeypatch.setattr(token_store, "keyring", None)

    # 2) Tokens fallback dans tmp_path (vide)
    patch_tokens(monkeypatch, tmp_path)

    # 3) Session DB mockée
    patch_sessionlocal(monkeypatch, db_session)

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out


def test_cli_login_success_saves_tokens(monkeypatch, tmp_path, capsys, db_session):
    """login sauvegarde des tokens locaux quand les identifiants sont valides."""
    patch_tokens(monkeypatch, tmp_path)
    patch_sessionlocal(monkeypatch, db_session)

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
    patch_tokens(monkeypatch, tmp_path)
    patch_sessionlocal(monkeypatch, db_session)

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
    patch_tokens(monkeypatch, tmp_path)
    patch_sessionlocal(monkeypatch, db_session)

    seed_tokens(monkeypatch, tmp_path, employee_id=999999999)

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out

    assert "Utilisateur introuvable" in out or "Non authentifié" in out


def test_cli_logout_clears_tokens(monkeypatch, tmp_path, capsys):
    """logout supprime les tokens locaux."""
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


def test_cli_management_only_not_authenticated(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only refuse si l'utilisateur n'est pas authentifié."""
    patch_tokens(monkeypatch, tmp_path)
    patch_sessionlocal(monkeypatch, db_session)

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out


def test_cli_management_only_allowed_for_management(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only autorise un utilisateur MANAGEMENT."""
    patch_tokens(monkeypatch, tmp_path)
    patch_sessionlocal(monkeypatch, db_session)

    emp = Employee(
        first_name="Boss",
        last_name="Manager",
        email="mgmt@example.com",
        role=Role.MANAGEMENT,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    seed_tokens(monkeypatch, tmp_path, emp.id)

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Action MANAGEMENT autorisée" in out


def test_cli_management_only_denied_for_support(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only refuse un utilisateur SUPPORT."""
    patch_tokens(monkeypatch, tmp_path)
    patch_sessionlocal(monkeypatch, db_session)

    emp = Employee(
        first_name="Bob",
        last_name="Support",
        email="support@example.com",
        role=Role.SUPPORT,
        password_hash=hash_password("Secret123!"),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)

    seed_tokens(monkeypatch, tmp_path, emp.id)

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Accès refusé" in out
    assert "MANAGEMENT" in out
