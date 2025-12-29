from __future__ import annotations

import argparse

from app.cli.commands.contracts import cmd_contracts_list


def add_contract_parsers(subparsers: argparse._SubParsersAction) -> None:
    p_contracts = subparsers.add_parser("contracts", help="Gestion des contrats")
    contracts_sub = p_contracts.add_subparsers(dest="contracts_command", required=True)

    p_contracts_list = contracts_sub.add_parser("list", help="Lister tous les contrats")
    p_contracts_list.set_defaults(func=cmd_contracts_list)
