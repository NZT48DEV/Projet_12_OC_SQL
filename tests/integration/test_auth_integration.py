from __future__ import annotations

from app.core import jwt_service, token_store
from app.core.security import hash_password
from app.epicevents import main
from app.models.employee import Employee, Role


def run_cli(monkeypatch, args: list[str]):
    """Simule l'appel CLI en patchant sys.argv."""
    monkeypatch.setattr("sys.argv", ["epicevents"] + args)


def _disable_keyring(monkeypatch) -> None:
    """
    Force token_store à utiliser uniquement le fallback fichier.
    Ça évite que des tokens existent via le keyring du système (flaky en CI).
    """
    monkeypatch.setattr(token_store, "keyring", None)


def patch_cli_env(monkeypatch, db_session, tmp_path):
    """Configure la DB de test, le secret JWT et le fichier de tokens temporaire."""
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")
    monkeypatch.setattr("app.epicevents.get_session", lambda: db_session)

    # Important : on neutralise keyring pour que les tests ne dépendent pas du coffre OS
    _disable_keyring(monkeypatch)

    # On force le fichier de tokens dans un dossier temporaire
    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    # Nettoyage défensif (au cas où)
    token_store.clear_tokens()


def create_employee(db_session, *, email: str, password: str, role: Role):
    """Crée et persiste un employé de test en base."""
    emp = Employee(
        first_name="Test",
        last_name="User",
        email=email,
        role=role,
        password_hash=hash_password(password),
    )
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


def seed_tokens_for_employee(tmp_path, monkeypatch, employee_id: int):
    """Écrit un fichier tokens.json valide pour un employee_id donné."""
    monkeypatch.setenv("EPICCRM_JWT_SECRET", "test_secret__do_not_use_in_prod")

    # Important : on neutralise keyring ici aussi
    _disable_keyring(monkeypatch)

    monkeypatch.setattr(token_store, "_token_path", lambda: tmp_path / "tokens.json")

    pair = jwt_service.create_token_pair(
        employee_id=employee_id,
        access_minutes=20,
        refresh_days=7,
    )
    token_store.save_tokens(pair.access_token, pair.refresh_token)


def test_integration_login_success_creates_tokens(
    monkeypatch, tmp_path, capsys, db_session
):
    """login valide crée des tokens persistants."""
    patch_cli_env(monkeypatch, db_session, tmp_path)
    emp = create_employee(
        db_session,
        email="ok@example.com",
        password="Secret123!",
        role=Role.MANAGEMENT,
    )

    run_cli(monkeypatch, ["login", "ok@example.com", "Secret123!"])
    main()
    out = capsys.readouterr().out

    assert "✅ Connecté" in out

    access = token_store.load_access_token()
    refresh = token_store.load_refresh_token()
    assert access is not None
    assert refresh is not None
    assert jwt_service.employee_id_from_access_token(access) == emp.id


def test_integration_login_wrong_password_does_not_create_tokens(
    monkeypatch, tmp_path, capsys, db_session
):
    """login invalide ne crée aucun token."""
    patch_cli_env(monkeypatch, db_session, tmp_path)
    create_employee(
        db_session,
        email="badpass@example.com",
        password="Secret123!",
        role=Role.MANAGEMENT,
    )

    run_cli(monkeypatch, ["login", "badpass@example.com", "WRONG"])
    main()
    out = capsys.readouterr().out

    assert "❌" in out
    assert token_store.load_access_token() is None
    assert token_store.load_refresh_token() is None


def test_integration_management_only_not_authenticated(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only refuse l'accès sans authentification."""
    patch_cli_env(monkeypatch, db_session, tmp_path)

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out


def test_integration_management_only_allowed_for_management(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only autorise un utilisateur MANAGEMENT."""
    patch_cli_env(monkeypatch, db_session, tmp_path)
    emp = create_employee(
        db_session,
        email="mgmt@example.com",
        password="Secret123!",
        role=Role.MANAGEMENT,
    )

    seed_tokens_for_employee(tmp_path, monkeypatch, emp.id)

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Action MANAGEMENT autorisée" in out


def test_integration_management_only_denied_for_support(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only refuse un utilisateur SUPPORT."""
    patch_cli_env(monkeypatch, db_session, tmp_path)
    emp = create_employee(
        db_session,
        email="support@example.com",
        password="Secret123!",
        role=Role.SUPPORT,
    )

    seed_tokens_for_employee(tmp_path, monkeypatch, emp.id)

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Accès refusé" in out
    assert "MANAGEMENT" in out
