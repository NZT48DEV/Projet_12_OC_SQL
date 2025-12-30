import pytest

from tests.conftest import reload_module


def test_config_raises_when_database_url_missing(monkeypatch: pytest.MonkeyPatch):
    """Vérifie qu'on lève une erreur si DATABASE_URL est absent à l'import."""
    # Empêche dotenv de recharger le .env et de "ré-injecter" DATABASE_URL
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)

    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="DATABASE_URL manquant"):
        reload_module("app.db.config")


def test_config_reads_database_url(monkeypatch: pytest.MonkeyPatch):
    """Vérifie que DATABASE_URL est lu depuis l'environnement."""
    monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)

    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/db"
    )

    cfg = reload_module("app.db.config")
    assert cfg.DATABASE_URL == "postgresql+psycopg://user:pass@localhost:5432/db"
