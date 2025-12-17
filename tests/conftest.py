import importlib
import sys

import pytest

import app.models  # noqa: F401
from app.db.base import Base


@pytest.fixture(scope="session")
def metadata():
    return Base.metadata


@pytest.fixture(scope="session")
def tables(metadata):
    return metadata.tables


@pytest.fixture()
def clients_table(tables):
    return tables["clients"]


def reload_module(module_name: str):
    """
    Force le rechargement d'un module Python.
    Utile pour tester les modules qui lisent l'environnement à l'import.
    """
    if module_name in sys.modules:
        del sys.modules[module_name]
    return importlib.import_module(module_name)
