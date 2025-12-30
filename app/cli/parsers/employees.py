from __future__ import annotations

import argparse

from app.cli.commands.employees import (
    cmd_create_employee,
    cmd_employees_list,
    cmd_management_only,
)
from app.models.employee import Role


def add_employee_parsers(subparsers: argparse._SubParsersAction) -> None:
    # management-only
    p_management = subparsers.add_parser(
        "management-only",
        help="Commande réservée au rôle MANAGEMENT",
    )
    p_management.set_defaults(func=cmd_management_only)

    # create-employee
    p_create = subparsers.add_parser(
        "create-employee",
        help="Créer un employé (bootstrap MANAGEMENT)",
    )
    p_create.add_argument("first_name")
    p_create.add_argument("last_name")
    p_create.add_argument("email")
    p_create.add_argument("password")
    p_create.add_argument("role", choices=[r.name for r in Role])
    p_create.set_defaults(func=cmd_create_employee)


def add_employee_group_parsers(subparsers: argparse._SubParsersAction) -> None:
    p_employees = subparsers.add_parser(
        "employees",
        help="Gestion des employés",
    )
    employees_sub = p_employees.add_subparsers(
        dest="employees_command",
        required=True,
    )

    p_list = employees_sub.add_parser(
        "list",
        help="Lister les employés",
    )
    p_list.add_argument(
        "--role",
        choices=[r.name for r in Role],
        default=None,
        help="Filtrer par rôle",
    )
    p_list.set_defaults(func=cmd_employees_list)
