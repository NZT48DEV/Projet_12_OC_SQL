from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.cli.commands import employees as employees_cmds


class DummySession:
    def __init__(self) -> None:
        self.closed = False
        self.added = []
        self.committed = False

    def close(self) -> None:
        self.closed = True

    def add(self, obj) -> None:
        self.added.append(obj)

    def commit(self) -> None:
        self.committed = True

    def refresh(self, _obj) -> None:
        pass

    def rollback(self) -> None:
        pass

    # pour cmd_create_employee : session.query(Employee).count()
    def query(self, _model):
        return self

    def count(self) -> int:
        return 0  # “bootstrap” : aucun employé


@pytest.fixture()
def session() -> DummySession:
    return DummySession()


def test_cmd_create_employee_bootstrap_requires_management(
    monkeypatch, capsys, session
):
    """create-employee: si DB vide, seul un MANAGEMENT est autorisé."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: session)

    # role != MANAGEMENT => doit refuser et ne rien créer
    args = SimpleNamespace(
        first_name="A", last_name="B", email="a@test.com", password="x", role="SALES"
    )
    employees_cmds.cmd_create_employee(args)

    out = capsys.readouterr().out
    assert "❌ Le premier compte doit être MANAGEMENT." in out
    assert session.committed is False


def test_cmd_employees_list_no_filter(monkeypatch, capsys, session):
    """employees list: affiche la liste des employés sans filtre."""
    monkeypatch.setattr(employees_cmds, "get_session", lambda: session)
    monkeypatch.setattr(
        employees_cmds, "get_current_employee", lambda s: SimpleNamespace()
    )

    repo = SimpleNamespace(
        list_all=lambda: [
            SimpleNamespace(
                id=1, email="a@test.com", role=SimpleNamespace(value="SALES")
            )
        ]
    )
    monkeypatch.setattr(employees_cmds, "EmployeeRepository", lambda s: repo)

    args = SimpleNamespace(role=None)
    employees_cmds.cmd_employees_list(args)

    out = capsys.readouterr().out
    assert "Employés :" in out
    assert "email=a@test.com" in out
