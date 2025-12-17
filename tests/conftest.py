import importlib
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.db.base import Base
from app.db.config import DATABASE_URL


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
def engine():
    """Crée un engine SQLAlchemy de session via DATABASE_URL."""
    engine = create_engine(DATABASE_URL)
    return engine


@pytest.fixture(scope="session")
def apply_migrations(engine):
    """
    Crée toutes les tables au début des tests d'intégration puis les supprime à la fin.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, apply_migrations):
    """
    Fournit une session SQLAlchemy isolée par test (transaction + rollback).
    """
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
    """
    Force le rechargement d'un module Python (utile pour tester les imports).
    """
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)
