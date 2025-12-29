from __future__ import annotations

import argparse

from app.cli.commands.auth import cmd_login, cmd_logout, cmd_refresh_token, cmd_whoami
from app.cli.commands.clients import cmd_clients_create, cmd_clients_list
from app.cli.commands.contracts import cmd_contracts_list
from app.cli.commands.employees import cmd_create_employee, cmd_management_only
from app.cli.commands.events import cmd_events_list
from app.models.employee import Role


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epicevents", description="Epic Events CRM - CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # auth
    p_login = subparsers.add_parser("login", help="Se connecter")
    p_login.add_argument("email")
    p_login.add_argument("password")
    p_login.set_defaults(func=cmd_login)

    p_logout = subparsers.add_parser("logout", help="Se déconnecter")
    p_logout.set_defaults(func=cmd_logout)

    p_refresh = subparsers.add_parser(
        "refresh-token", help="Régénérer un access token via le refresh token"
    )
    p_refresh.set_defaults(func=cmd_refresh_token)

    p_whoami = subparsers.add_parser("whoami", help="Afficher l'utilisateur courant")
    p_whoami.set_defaults(func=cmd_whoami)

    # management-only
    p_management = subparsers.add_parser(
        "management-only", help="Commande réservée au rôle MANAGEMENT"
    )
    p_management.set_defaults(func=cmd_management_only)

    # employees
    p_create = subparsers.add_parser(
        "create-employee", help="Créer un employé (bootstrap MANAGEMENT)"
    )
    p_create.add_argument("first_name")
    p_create.add_argument("last_name")
    p_create.add_argument("email")
    p_create.add_argument("password")
    p_create.add_argument("role", choices=[r.name for r in Role])
    p_create.set_defaults(func=cmd_create_employee)

    # clients
    p_clients = subparsers.add_parser("clients", help="Gestion des clients")
    clients_sub = p_clients.add_subparsers(dest="clients_command", required=True)

    p_clients_list = clients_sub.add_parser("list", help="Lister tous les clients")
    p_clients_list.set_defaults(func=cmd_clients_list)

    p_clients_create = clients_sub.add_parser("create", help="Créer un client (SALES)")
    p_clients_create.add_argument("first_name")
    p_clients_create.add_argument("last_name")
    p_clients_create.add_argument("email")
    p_clients_create.add_argument("--phone", default=None)
    p_clients_create.add_argument("--company-name", dest="company_name", default=None)
    p_clients_create.set_defaults(func=cmd_clients_create)

    # contracts
    p_contracts = subparsers.add_parser("contracts", help="Gestion des contrats")
    contracts_sub = p_contracts.add_subparsers(dest="contracts_command", required=True)

    p_contracts_list = contracts_sub.add_parser("list", help="Lister tous les contrats")
    p_contracts_list.set_defaults(func=cmd_contracts_list)

    # events
    p_events = subparsers.add_parser("events", help="Gestion des événements")
    events_sub = p_events.add_subparsers(dest="events_command", required=True)

    p_events_list = events_sub.add_parser("list", help="Lister tous les événements")
    p_events_list.set_defaults(func=cmd_events_list)

    return parser
