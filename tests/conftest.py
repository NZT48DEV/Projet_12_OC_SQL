from __future__ import annotations

import importlib
import os
import sys

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.config as db_config
import app.models  # noqa: F401
from app.db.base import Base

load_dotenv()


def _test_database_url() -> str:
    """Retourne l'URL de la base de test."""
    return os.getenv(
        "DATABASE_URL_TEST",
        "postgresql+psycopg://epic_crm_app:epic_crm_password@localhost:5432/epic_crm_test",
    )


@pytest.fixture(scope="session", autouse=True)
def force_test_database_url() -> None:
    """Force DATABASE_URL à pointer vers la base de test."""
    url = _test_database_url()
    os.environ["DATABASE_URL"] = url
    db_config.DATABASE_URL = url


@pytest.fixture(scope="session")
def metadata():
    """Expose Base.metadata pour les tests de schéma."""
    return Base.metadata


@pytest.fixture(scope="session")
def tables(metadata):
    """Expose le mapping nom_de_table -> Table via metadata.tables."""
    return metadata.tables


@pytest.fixture()
def clients_table(tables):
    """Retourne la table SQLAlchemy 'clients' depuis la metadata."""
    return tables["clients"]


@pytest.fixture()
def employees_table(tables):
    """Retourne la table SQLAlchemy 'employees' depuis la metadata."""
    return tables["employees"]


@pytest.fixture()
def contracts_table(tables):
    """Retourne la table SQLAlchemy 'contracts' depuis la metadata."""
    return tables["contracts"]


@pytest.fixture()
def events_table(tables):
    """Retourne la table SQLAlchemy 'events' depuis la metadata."""
    return tables["events"]


@pytest.fixture(scope="session")
def engine(force_test_database_url):
    """Crée un engine SQLAlchemy de session via DATABASE_URL."""
    return create_engine(os.environ["DATABASE_URL"])


@pytest.fixture(scope="session")
def apply_migrations(engine):
    """Crée toutes les tables au début des tests puis les supprime à la fin."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, apply_migrations):
    """Fournit une session SQLAlchemy isolée par test via transaction + rollback."""
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


def reload_module(module_name: str):
    """Force le rechargement d'un module Python pour tester un import à froid."""
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)


class DummySessionRB:
    """Dummy session avec rollback + close (tests commandes CRUD)."""

    def __init__(self) -> None:
        self.closed = False
        self.rolled_back = False

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class DummySessionCloseOnly:
    """Dummy session avec close uniquement (tests auth)."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


@pytest.fixture()
def dummy_session_rb() -> DummySessionRB:
    return DummySessionRB()


@pytest.fixture()
def dummy_session_close_only() -> DummySessionCloseOnly:
    return DummySessionCloseOnly()
