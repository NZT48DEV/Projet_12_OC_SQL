from __future__ import annotations

import types

import pytest


class DummySessionClose:
    """Local fallback si tu veux garder ce fichier autonome, mais normalement on passe par la fixture."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_cmd_login_unexpected_exception_is_captured(
    monkeypatch: pytest.MonkeyPatch, dummy_session_close_only
) -> None:
    import app.cli.commands.auth as auth_cmds

    monkeypatch.setattr(auth_cmds, "get_session", lambda: dummy_session_close_only)

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(auth_cmds, "authenticate_employee", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        auth_cmds.sentry_sdk, "capture_exception", lambda exc: captured.append(exc)
    )

    args = types.SimpleNamespace(email="x@test.com", password="bad")
    auth_cmds.cmd_login(args)

    assert dummy_session_close_only.closed is True
    assert len(captured) == 1
    assert isinstance(captured[0], RuntimeError)


def test_cmd_refresh_token_unexpected_exception_is_captured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.cli.commands.auth as auth_cmds

    monkeypatch.setattr(auth_cmds, "load_refresh_token", lambda: "dummy-refresh")

    def boom(*args, **kwargs):
        raise RuntimeError("boom-refresh")

    monkeypatch.setattr(auth_cmds, "refresh_access_token", boom)

    captured: list[Exception] = []
    monkeypatch.setattr(
        auth_cmds.sentry_sdk, "capture_exception", lambda exc: captured.append(exc)
    )

    auth_cmds.cmd_refresh_token(types.SimpleNamespace())

    assert len(captured) == 1
    assert isinstance(captured[0], RuntimeError)
