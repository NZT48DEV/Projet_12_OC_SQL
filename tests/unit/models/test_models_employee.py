from collections.abc import Mapping
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.sql.schema import Table

from app.models.employee import Employee, Role


def test_employees_table_exists(tables: Mapping[str, Table]):
    """Vérifie que la table 'employees' est bien déclarée dans la metadata."""
    assert "employees" in tables


def test_employees_columns(employees_table: Table):
    """Vérifie colonnes, NULL/NOT NULL et types principaux de la table employees."""
    cols = employees_table.c

    assert set(cols.keys()) >= {
        "id",
        "first_name",
        "last_name",
        "email",
        "role",
        "password_hash",
        "created_at",
    }

    assert cols.first_name.nullable is False
    assert cols.last_name.nullable is False
    assert cols.email.nullable is False
    assert cols.role.nullable is False
    assert cols.password_hash.nullable is False
    assert cols.created_at.nullable is False

    assert isinstance(cols.first_name.type, String)
    assert isinstance(cols.last_name.type, String)
    assert isinstance(cols.email.type, String)
    assert isinstance(cols.role.type, SAEnum)
    assert isinstance(cols.created_at.type, DateTime)


def test_employees_email_unique_constraint_named(employees_table: Table):
    """Vérifie la présence de la contrainte UNIQUE nommée uq_employees_email."""
    assert "uq_employees_email" in {c.name for c in employees_table.constraints}


def test_employee_instance_creation():
    """Vérifie qu'une instance Employee se crée avec les champs attendus."""
    employee = Employee(
        first_name="Jane",
        last_name="Darc",
        email="jane.darc@test.com",
        role=Role.SALES,
        password_hash="hash",
        created_at=datetime.now(timezone.utc),
    )

    assert employee.first_name == "Jane"
    assert employee.last_name == "Darc"
    assert employee.email == "jane.darc@test.com"
    assert employee.role == Role.SALES
    assert employee.password_hash == "hash"
    assert employee.created_at.tzinfo is not None
