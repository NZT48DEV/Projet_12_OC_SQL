from __future__ import annotations

import pytest


def test_init_sentry_no_dsn_does_not_init(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Si SENTRY_DSN est absent/vide, init_sentry() ne doit rien initialiser.
    Note : conftest.py charge .env, donc on force ici le comportement attendu.
    """
    import app.core.observability as obs

    monkeypatch.delenv("SENTRY_DSN", raising=False)

    calls: list[dict] = []

    def fake_init(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(obs.sentry_sdk, "init", fake_init)

    obs.init_sentry()

    assert calls == []


def test_init_sentry_with_dsn_calls_sentry_init(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Avec un DSN présent, init_sentry() doit appeler sentry_sdk.init avec
    les bons paramètres (environment/release, send_default_pii, etc.).
    """
    import app.core.observability as obs

    monkeypatch.setenv("SENTRY_DSN", "https://example@sentry.io/1")
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "ci")
    monkeypatch.setenv("SENTRY_RELEASE", "epic-events@1.2.3")

    calls: list[dict] = []

    def fake_init(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(obs.sentry_sdk, "init", fake_init)

    obs.init_sentry()

    assert len(calls) == 1
    kwargs = calls[0]

    assert kwargs["dsn"] == "https://example@sentry.io/1"
    assert kwargs["environment"] == "ci"
    assert kwargs["release"] == "epic-events@1.2.3"
    assert kwargs["send_default_pii"] is False
    assert kwargs["server_name"] is None
    assert kwargs["before_send"] == obs.before_send


def test_before_send_scrubs_user_ip_and_server_name() -> None:
    import app.core.observability as obs

    event = {
        "user": {"geo": {"city": "X"}, "email": "a@b.com"},
        "server_name": "PC",
        "extra": {"x": 1},
    }

    cleaned = obs.before_send(event, hint=None)

    assert cleaned["user"] == {"ip_address": None}
    assert "server_name" not in cleaned
    assert cleaned["extra"] == {"x": 1}
