"""Tests CLI (intégration légère) pour epicevents via main()."""

import json

from app.core import session_store
from app.core.security import hash_password
from app.epicevents import main
from app.models.employee import Employee, Role


def run_cli(monkeypatch, args: list[str]):
    """Simule sys.argv pour exécuter une commande CLI."""
    monkeypatch.setattr("sys.argv", ["epicevents"] + args)


def patch_sessionlocal(monkeypatch, db_session):
    """Force epicevents.SessionLocal() à renvoyer la session de test."""
    monkeypatch.setattr("app.epicevents.SessionLocal", lambda: db_session)


def test_cli_whoami_not_authenticated(monkeypatch, tmp_path, capsys):
    """whoami affiche un message si aucune session n'est présente."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out
    assert "Non authentifié" in out


def test_cli_login_success_saves_session(monkeypatch, tmp_path, capsys, db_session):
    """login sauvegarde la session locale quand les identifiants sont valides."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )
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

    assert "Session sauvegardée" in out
    assert session_store.load_current_employee_id() == emp.id


def test_cli_whoami_with_valid_session(monkeypatch, tmp_path, capsys, db_session):
    """whoami affiche l'utilisateur si la session locale est valide."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )
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

    (tmp_path / "session.json").write_text(
        json.dumps({"employee_id": emp.id}), encoding="utf-8"
    )

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out

    assert "Session active" in out
    assert "SUPPORT" in out


def test_cli_whoami_invalid_session_clears_file(
    monkeypatch, tmp_path, capsys, db_session
):
    """whoami nettoie la session si l'employé n'existe pas en base."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )
    patch_sessionlocal(monkeypatch, db_session)

    path = tmp_path / "session.json"
    path.write_text(json.dumps({"employee_id": 999999999}), encoding="utf-8")

    run_cli(monkeypatch, ["whoami"])
    main()
    out = capsys.readouterr().out

    assert "Session invalide" in out
    assert not path.exists()


def test_cli_logout_clears_session(monkeypatch, tmp_path, capsys):
    """logout supprime la session locale."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )

    session_store.save_current_employee(1)
    assert session_store.load_current_employee_id() == 1

    run_cli(monkeypatch, ["logout"])
    main()
    out = capsys.readouterr().out

    assert "Déconnecté" in out
    assert session_store.load_current_employee_id() is None


def test_cli_management_only_not_authenticated(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only refuse si l'utilisateur n'est pas authentifié."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )
    patch_sessionlocal(monkeypatch, db_session)

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Non authentifié" in out


def test_cli_management_only_allowed_for_management(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only autorise un utilisateur MANAGEMENT."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )
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

    (tmp_path / "session.json").write_text(
        json.dumps({"employee_id": emp.id}), encoding="utf-8"
    )

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Action autorisée" in out


def test_cli_management_only_denied_for_support(
    monkeypatch, tmp_path, capsys, db_session
):
    """management-only refuse un utilisateur SUPPORT."""
    monkeypatch.setattr(
        session_store, "_session_path", lambda: tmp_path / "session.json"
    )
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

    (tmp_path / "session.json").write_text(
        json.dumps({"employee_id": emp.id}), encoding="utf-8"
    )

    run_cli(monkeypatch, ["management-only"])
    main()
    out = capsys.readouterr().out

    assert "Accès refusé" in out
    assert "MANAGEMENT" in out
