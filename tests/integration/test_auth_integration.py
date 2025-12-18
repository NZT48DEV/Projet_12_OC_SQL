"""Tests d'intégration AuthN/AuthZ via la CLI epicevents."""

import json

from app.core import session_store
from app.core.security import hash_password
from app.epicevents import main
from app.models.employee import Employee, Role


def run_cli(monkeypatch, args: list[str]):
    """Simule l'appel CLI en patchant sys.argv."""
    monkeypatch.setattr("sys.argv", ["epicevents"] + args)


def patch_cli_env(monkeypatch, db_session, tmp_path):
    """Configure la DB de test et le fichier de session temporaire."""
    monkeypatch.setattr("app.epicevents.SessionLocal", lambda: db_session)
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )


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


def test_integration_login_success_creates_session(
    monkeypatch, tmp_path, capsys, db_session
):
    """login valide crée une session persistante."""
    patch_cli_env(monkeypatch, db_session, tmp_path)
    emp = create_employee(
        db_session, email="ok@example.com", password="Secret123!", role=Role.MANAGEMENT
    )

    run_cli(monkeypatch, ["login", "ok@example.com", "Secret123!"])
    main()
    out = capsys.readouterr().out

    assert "Session sauvegardée" in out
    assert session_store.load_current_employee_id() == emp.id


def test_integration_login_wrong_password_does_not_create_session(
    monkeypatch, tmp_path, capsys, db_session
):
    """login invalide ne crée aucune session."""
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

    assert "Email ou mot de passe invalide" in out
    assert session_store.load_current_employee_id() is None


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

    (tmp_path / "session.json").write_text(
        json.dumps({"employee_id": emp.id}), encoding="utf-8"
    )

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Action autorisée" in out


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

    (tmp_path / "session.json").write_text(
        json.dumps({"employee_id": emp.id}), encoding="utf-8"
    )

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Accès refusé" in out
