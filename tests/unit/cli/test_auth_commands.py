from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.cli.commands import auth as auth_cmds


class DummySession:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


@pytest.fixture()
def session() -> DummySession:
    return DummySession()


def test_cmd_login_success(monkeypatch, capsys, session):
    """login: authentifie, génère des tokens, les stocke et affiche un message de succès."""
    employee = SimpleNamespace(id=1, first_name="A", last_name="B", role="SALES")

    monkeypatch.setattr(auth_cmds, "get_session", lambda: session)
    monkeypatch.setattr(auth_cmds, "authenticate_employee", lambda s, e, p: employee)

    token_pair = SimpleNamespace(access_token="access", refresh_token="refresh")
    monkeypatch.setattr(auth_cmds, "create_token_pair", lambda **kwargs: token_pair)

    saved = {}
    monkeypatch.setattr(
        auth_cmds,
        "save_tokens",
        lambda a, r: saved.update({"access": a, "refresh": r}),
    )

    args = SimpleNamespace(email="x@test.com", password="pass")
    auth_cmds.cmd_login(args)

    out = capsys.readouterr().out
    assert "✅ Connecté" in out
    assert saved["access"] == "access"
    assert saved["refresh"] == "refresh"
    assert session.closed is True


def test_cmd_login_bad_credentials(monkeypatch, capsys, session):
    """login: affiche une erreur si identifiants invalides."""
    monkeypatch.setattr(auth_cmds, "get_session", lambda: session)

    class FakeAuthError(Exception):
        pass

    # Patch l'exception attendue dans le module auth_cmds
    monkeypatch.setattr(auth_cmds, "AuthenticationError", FakeAuthError)
    monkeypatch.setattr(
        auth_cmds,
        "authenticate_employee",
        lambda *a, **k: (_ for _ in ()).throw(
            FakeAuthError("Email ou mot de passe invalide.")
        ),
    )

    args = SimpleNamespace(email="x@test.com", password="bad")
    auth_cmds.cmd_login(args)

    out = capsys.readouterr().out
    assert "❌ Email ou mot de passe invalide." in out
    assert session.closed is True


def test_cmd_logout(monkeypatch, capsys):
    """logout: supprime les tokens locaux et affiche un message."""
    called = {"clear": 0}
    monkeypatch.setattr(
        auth_cmds,
        "clear_tokens",
        lambda: called.__setitem__("clear", called["clear"] + 1),
    )

    auth_cmds.cmd_logout(SimpleNamespace())
    out = capsys.readouterr().out

    assert called["clear"] == 1
    assert "✅ Déconnecté." in out


def test_cmd_refresh_token_no_token(monkeypatch, capsys):
    """refresh-token: si aucun refresh token local, affiche une erreur et stoppe."""
    monkeypatch.setattr(auth_cmds, "load_refresh_token", lambda: None)

    auth_cmds.cmd_refresh_token(SimpleNamespace())
    out = capsys.readouterr().out

    assert "❌ Aucun refresh token trouvé" in out


def test_cmd_refresh_token_success(monkeypatch, capsys):
    """refresh-token: régénère et stocke les tokens puis affiche un message de succès."""
    monkeypatch.setattr(auth_cmds, "load_refresh_token", lambda: "refresh0")
    token_pair = SimpleNamespace(access_token="a1", refresh_token="r1")
    monkeypatch.setattr(auth_cmds, "refresh_access_token", lambda **k: token_pair)

    saved = {}
    monkeypatch.setattr(
        auth_cmds, "save_tokens", lambda a, r: saved.update({"a": a, "r": r})
    )

    auth_cmds.cmd_refresh_token(SimpleNamespace())
    out = capsys.readouterr().out

    assert "✅ Token rafraîchi avec succès." in out
    assert saved["a"] == "a1"
    assert saved["r"] == "r1"


def test_cmd_whoami_success(monkeypatch, capsys, session):
    """whoami: affiche l'utilisateur courant si authentifié."""
    employee = SimpleNamespace(
        first_name="A", last_name="B", email="a@test.com", role="SALES"
    )
    monkeypatch.setattr(auth_cmds, "get_session", lambda: session)
    monkeypatch.setattr(auth_cmds, "get_current_employee", lambda s: employee)

    auth_cmds.cmd_whoami(SimpleNamespace())
    out = capsys.readouterr().out

    assert "👤" in out
    assert "email=a@test.com" in out
    assert session.closed is True
