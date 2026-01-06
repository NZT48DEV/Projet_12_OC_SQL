from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from app.cli.commands import employees as employees_cmds
from app.models.employee import Role


class BootstrapSession:
    """
    Session minimale pour tester cmd_create_employee :
    - query(Employee).count()
    - add/commit/refresh/rollback/close
    """

    def __init__(self, employees_count: int) -> None:
        self.closed = False
        self.rolled_back = False
        self.added = []
        self.committed = False
        self.refreshed = False
        self._employees_count = employees_count

    def close(self) -> None:
        self.closed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def add(self, obj) -> None:
        self.added.append(obj)

    def commit(self) -> None:
        self.committed = True

    def refresh(self, _obj) -> None:
        self.refreshed = True

    # cmd_create_employee : session.query(Employee).count()
    def query(self, _model):
        return self

    def count(self) -> int:
        return self._employees_count


# -------------------------
# cmd_create_employee
# -------------------------


def test_cmd_create_employee_bootstrap_requires_management(monkeypatch, capsys):
    """DB vide: seul MANAGEMENT est autorisé."""
    session = BootstrapSession(employees_count=0)
    monkeypatch.setattr(employees_cmds, "get_session", lambda: session)

    args = SimpleNamespace(
        first_name="A",
        last_name="B",
        email="a@test.com",
        password="x",
        role="SALES",
    )
    employees_cmds.cmd_create_employee(args)

    out = capsys.readouterr().out
    assert "❌ Le premier compte doit être MANAGEMENT." in out
    assert session.committed is False
    assert session.closed is True


def test_cmd_create_employee_bootstrap_management_success(monkeypatch, capsys):
    """DB vide: MANAGEMENT => création OK (commit + refresh + print)."""
    session = BootstrapSession(employees_count=0)
    monkeypatch.setattr(employees_cmds, "get_session", lambda: session)

    # Utilise le vrai Enum Role
    monkeypatch.setattr(employees_cmds, "Role", Role)

    # Evite dépendre de SQLAlchemy : on stub Employee
    created = SimpleNamespace(
        first_name="A", last_name="B", email="a@test.com", role=Role.MANAGEMENT
    )
    monkeypatch.setattr(employees_cmds, "hash_password", lambda _p: "hashed")
    monkeypatch.setattr(employees_cmds, "Employee", lambda **_kw: created)

    args = SimpleNamespace(
        first_name="A",
        last_name="B",
        email="a@test.com",
        password="x",
        role=Role.MANAGEMENT.name,  # "MANAGEMENT"
    )
    employees_cmds.cmd_create_employee(args)

    out = capsys.readouterr().out
    assert "✅ Employé créé" in out
    assert session.committed is True
    assert session.refreshed is True
    assert session.closed is True


def test_cmd_create_employee_non_bootstrap_authorization_error(monkeypatch, capsys):
    """DB non vide: require_role refuse => ⛔."""
    session = BootstrapSession(employees_count=1)
    monkeypatch.setattr(employees_cmds, "get_session", lambda: session)
    monkeypatch.setattr(employees_cmds, "Role", Role)

    monkeypatch.setattr(
        employees_cmds,
        "get_current_employee",
        lambda _s: SimpleNamespace(role=Role.SALES),
    )

    class FakeAuthzError(Exception):
        pass

    monkeypatch.setattr(employees_cmds, "AuthorizationError", FakeAuthzError)
    monkeypatch.setattr(
        employees_cmds,
        "require_role",
        lambda *_a, **_k: (_ for _ in ()).throw(FakeAuthzError("Interdit")),
    )

    args = SimpleNamespace(
        first_name="A",
        last_name="B",
        email="a@test.com",
        password="x",
        role=Role.SALES.name,
    )
    employees_cmds.cmd_create_employee(args)

    out = capsys.readouterr().out
    assert "⛔ Accès refusé" in out
    assert session.closed is True


def test_cmd_create_employee_invalid_role_keyerror(monkeypatch, capsys):
    """DB non vide: Role[args.role] lève KeyError => message 'Rôle invalide'."""
    session = BootstrapSession(employees_count=1)
    monkeypatch.setattr(employees_cmds, "get_session", lambda: session)

    # Utilise le vrai Enum Role (hashable, fidèle)
    monkeypatch.setattr(employees_cmds, "Role", Role)

    # Passe la barrière require_role (on ne veut pas tester l'auth ici)
    monkeypatch.setattr(
        employees_cmds,
        "get_current_employee",
        lambda _s: SimpleNamespace(role=Role.MANAGEMENT),
    )
    monkeypatch.setattr(employees_cmds, "require_role", lambda *_a, **_k: None)

    args = SimpleNamespace(
        first_name="A",
        last_name="B",
        email="a@test.com",
        password="x",
        role="NOPE",  # => KeyError sur Role["NOPE"]
    )
    employees_cmds.cmd_create_employee(args)

    out = capsys.readouterr().out
    assert "❌ Rôle invalide" in out
    assert session.closed is True


def test_cmd_create_employee_unexpected_exception_rollbacks(monkeypatch, capsys):
    """Exception inattendue => rollback + capture + message."""
    session = BootstrapSession(employees_count=0)
    monkeypatch.setattr(employees_cmds, "get_session", lambda: session)
    monkeypatch.setattr(employees_cmds, "Role", Role)

    monkeypatch.setattr(employees_cmds, "hash_password", lambda _p: "hashed")

    def boom_employee(**_kw):
        raise RuntimeError("boom")

    monkeypatch.setattr(employees_cmds, "Employee", boom_employee)

    captured: list[Exception] = []
    monkeypatch.setattr(
        employees_cmds.sentry_sdk, "capture_exception", lambda e: captured.append(e)
    )

    args = SimpleNamespace(
        first_name="A",
        last_name="B",
        email="a@test.com",
        password="x",
        role=Role.MANAGEMENT.name,
    )
    employees_cmds.cmd_create_employee(args)

    out = capsys.readouterr().out
    assert "❌ Erreur lors de la création de l'employé" in out
    assert session.rolled_back is True
    assert len(captured) == 1
    assert session.closed is True


# -------------------------
# cmd_employees_list
# -------------------------


def test_cmd_employees_list_empty(monkeypatch, capsys, dummy_session_rb):
    """employees list: affiche 'Aucun employé trouvé.' si vide."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        employees_cmds, "get_current_employee", lambda _s: SimpleNamespace()
    )

    repo = SimpleNamespace(list_all=lambda: [])
    monkeypatch.setattr(employees_cmds, "EmployeeRepository", lambda _s: repo)

    employees_cmds.cmd_employees_list(SimpleNamespace(role=None))
    out = capsys.readouterr().out

    assert "Aucun employé trouvé." in out
    assert dummy_session_rb.closed is True


def test_cmd_employees_list_prints(monkeypatch, capsys, dummy_session_rb):
    """employees list: affiche la liste des employés."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        employees_cmds, "get_current_employee", lambda _s: SimpleNamespace()
    )

    repo = SimpleNamespace(
        list_all=lambda: [
            SimpleNamespace(
                id=1, email="a@test.com", role=SimpleNamespace(value="SALES")
            )
        ]
    )
    monkeypatch.setattr(employees_cmds, "EmployeeRepository", lambda _s: repo)

    employees_cmds.cmd_employees_list(SimpleNamespace(role=None))
    out = capsys.readouterr().out

    assert "Employés :" in out
    assert "email=a@test.com" in out
    assert dummy_session_rb.closed is True


def test_cmd_employees_list_with_role_filter(monkeypatch, capsys, dummy_session_rb):
    """employees list --role: appelle list_by_role."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(
        employees_cmds, "get_current_employee", lambda _s: SimpleNamespace()
    )
    monkeypatch.setattr(employees_cmds, "Role", Role)

    repo = SimpleNamespace(
        list_by_role=lambda _role: [
            SimpleNamespace(
                id=2, email="b@test.com", role=SimpleNamespace(value="SUPPORT")
            )
        ]
    )
    monkeypatch.setattr(employees_cmds, "EmployeeRepository", lambda _s: repo)

    employees_cmds.cmd_employees_list(SimpleNamespace(role=Role.SUPPORT.name))
    out = capsys.readouterr().out

    assert "email=b@test.com" in out
    assert dummy_session_rb.closed is True


# -------------------------
# deactivate / reactivate / delete
# -------------------------


def test_cmd_employees_deactivate_success(monkeypatch, capsys, dummy_session_rb):
    """deactivate: affiche ✅ + date formatée."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(employees_cmds, "get_current_employee", lambda _s: object())

    emp = SimpleNamespace(
        id=1,
        email="x@test.com",
        deactivated_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    monkeypatch.setattr(employees_cmds, "deactivate_employee", lambda **_k: emp)

    employees_cmds.cmd_employees_deactivate(SimpleNamespace(employee_id=1))
    out = capsys.readouterr().out

    assert "✅ Employé désactivé" in out
    assert "désactivé_le=" in out
    assert dummy_session_rb.closed is True


def test_cmd_employees_reactivate_success(monkeypatch, capsys, dummy_session_rb):
    """reactivate: affiche ✅ + date formatée."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(employees_cmds, "get_current_employee", lambda _s: object())

    emp = SimpleNamespace(
        id=1,
        email="x@test.com",
        reactivated_at=datetime(2026, 1, 2, 10, 0, 0),
    )
    monkeypatch.setattr(employees_cmds, "reactivate_employee", lambda **_k: emp)

    employees_cmds.cmd_employees_reactivate(SimpleNamespace(employee_id=1))
    out = capsys.readouterr().out

    assert "✅ Employé réactivé" in out
    assert "réactivé_le=" in out
    assert dummy_session_rb.closed is True


def test_cmd_employees_delete_hard_requires_confirm(
    monkeypatch, capsys, dummy_session_rb
):
    """delete --hard sans confirm => ⚠️."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(employees_cmds, "get_current_employee", lambda _s: object())

    args = SimpleNamespace(employee_id=1, hard=True, confirm=None)
    employees_cmds.cmd_employees_delete(args)

    out = capsys.readouterr().out
    assert "⚠️" in out
    assert dummy_session_rb.closed is True


def test_cmd_employees_delete_hard_success(monkeypatch, capsys, dummy_session_rb):
    """delete --hard => appelle hard_delete_employee + print ✅."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(employees_cmds, "get_current_employee", lambda _s: object())

    called = {"n": 0}

    def hard_delete_employee(**_k):
        called["n"] += 1

    monkeypatch.setattr(employees_cmds, "hard_delete_employee", hard_delete_employee)

    args = SimpleNamespace(employee_id=1, hard=True, confirm=1)
    employees_cmds.cmd_employees_delete(args)

    out = capsys.readouterr().out
    assert "✅ Employé supprimé définitivement" in out
    assert called["n"] == 1
    assert dummy_session_rb.closed is True


def test_cmd_employees_delete_soft_success(monkeypatch, capsys, dummy_session_rb):
    """delete sans --hard => deactivate_employee + print ✅."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: dummy_session_rb)
    monkeypatch.setattr(employees_cmds, "get_current_employee", lambda _s: object())

    emp = SimpleNamespace(
        id=1,
        email="x@test.com",
        deactivated_at=datetime(2026, 1, 1, 10, 0, 0),
    )
    monkeypatch.setattr(employees_cmds, "deactivate_employee", lambda **_k: emp)

    args = SimpleNamespace(employee_id=1, hard=False, confirm=None)
    employees_cmds.cmd_employees_delete(args)

    out = capsys.readouterr().out
    assert "✅ Employé désactivé" in out
    assert dummy_session_rb.closed is True
