from __future__ import annotations

import argparse

from app.cli.commands.contracts import (
    cmd_contracts_create,
    cmd_contracts_list,
    cmd_contracts_reassign,
    cmd_contracts_sign,
    cmd_contracts_update,
)


def add_contract_parsers(subparsers: argparse._SubParsersAction) -> None:
    p_contracts = subparsers.add_parser("contracts", help="Gestion des contrats")
    contracts_sub = p_contracts.add_subparsers(dest="contracts_command", required=True)

    p_contracts_list = contracts_sub.add_parser("list", help="Lister tous les contrats")
    p_contracts_list.set_defaults(func=cmd_contracts_list)

    p_contracts_create = contracts_sub.add_parser(
        "create",
        help="Créer un contrat (MANAGEMENT)",
    )
    p_contracts_create.add_argument("client_id", type=int)
    p_contracts_create.add_argument("total")
    p_contracts_create.add_argument("amount_due")
    p_contracts_create.add_argument("--signed", action="store_true")
    p_contracts_create.set_defaults(func=cmd_contracts_create)

    p_contracts_sign = contracts_sub.add_parser(
        "sign",
        help="Signer un contrat (MANAGEMENT)",
    )
    p_contracts_sign.add_argument("contract_id", type=int)
    p_contracts_sign.set_defaults(func=cmd_contracts_sign)

    p_contracts_update = contracts_sub.add_parser(
        "update",
        help="Mettre à jour un contrat (SALES/MANAGEMENT)",
    )
    p_contracts_update.add_argument("contract_id", type=int)
    p_contracts_update.add_argument("--total", dest="total_amount", default=None)
    p_contracts_update.add_argument("--amount-due", dest="amount_due", default=None)
    p_contracts_update.set_defaults(func=cmd_contracts_update)

    p_contracts_reassign = contracts_sub.add_parser(
        "reassign",
        help="Réassigner un contrat à un commercial (SALES sur ses contrats / MANAGEMENT)",
    )
    p_contracts_reassign.add_argument("contract_id", type=int)
    p_contracts_reassign.add_argument("sales_contact_id", type=int)
    p_contracts_reassign.set_defaults(func=cmd_contracts_reassign)
