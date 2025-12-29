from __future__ import annotations

import argparse

from app.cli.commands.clients import cmd_clients_create, cmd_clients_list


def add_client_parsers(subparsers: argparse._SubParsersAction) -> None:
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
