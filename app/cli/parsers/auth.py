from __future__ import annotations

import argparse

from app.cli.commands.auth import cmd_login, cmd_logout, cmd_refresh_token, cmd_whoami


def add_auth_parsers(subparsers: argparse._SubParsersAction) -> None:
    # login
    p_login = subparsers.add_parser("login", help="Se connecter")
    p_login.add_argument("email")
    p_login.add_argument("password")
    p_login.set_defaults(func=cmd_login)

    # logout
    p_logout = subparsers.add_parser("logout", help="Se déconnecter")
    p_logout.set_defaults(func=cmd_logout)

    # refresh-token
    p_refresh = subparsers.add_parser(
        "refresh-token",
        help="Régénérer un access token via le refresh token",
    )
    p_refresh.set_defaults(func=cmd_refresh_token)

    # whoami
    p_whoami = subparsers.add_parser(
        "whoami",
        help="Afficher l'utilisateur courant",
    )
    p_whoami.set_defaults(func=cmd_whoami)
