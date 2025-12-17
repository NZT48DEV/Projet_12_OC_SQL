from tests.conftest import reload_module


def test_engine_create_engine_called_with_database_url(monkeypatch):
    # Mock DATABASE_URL
    monkeypatch.setattr(
        "app.db.config.DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/epic_crm"
    )

    calls = {}

    def fake_create_engine(url, **kwargs):
        calls["url"] = url
        calls["kwargs"] = kwargs
        return object()

    # Patch create_engine importé dans app.db.engine
    monkeypatch.setattr("sqlalchemy.create_engine", fake_create_engine)

    mod = reload_module("app.db.engine")

    assert calls["url"] == "postgresql+psycopg://u:p@localhost:5432/epic_crm"
    assert calls["kwargs"]["pool_pre_ping"] is True
    assert hasattr(mod, "engine")
