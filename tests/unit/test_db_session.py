from tests.conftest import reload_module


def test_sessionmaker_called_with_expected_args(monkeypatch):
    """Vérifie que SessionLocal est créé avec les bons paramètres."""
    fake_engine = object()
    monkeypatch.setattr("app.db.engine.get_engine", lambda: fake_engine)

    calls = {}

    def fake_sessionmaker(**kwargs):
        calls.update(kwargs)
        return "SESSIONMAKER_RETURN"

    monkeypatch.setattr("sqlalchemy.orm.sessionmaker", fake_sessionmaker)

    mod = reload_module("app.db.session")

    assert mod.SessionLocal == "SESSIONMAKER_RETURN"
    assert calls["bind"] is fake_engine
    assert calls["autoflush"] is False
    assert calls["autocommit"] is False
