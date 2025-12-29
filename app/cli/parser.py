from __future__ import annotations

import argparse

from app.cli.parsers.auth import add_auth_parsers
from app.cli.parsers.clients import add_client_parsers
from app.cli.parsers.contracts import add_contract_parsers
from app.cli.parsers.employees import add_employee_parsers
from app.cli.parsers.events import add_event_parsers


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epicevents",
        description="Epic Events CRM - CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_auth_parsers(subparsers)
    add_employee_parsers(subparsers)
    add_client_parsers(subparsers)
    add_contract_parsers(subparsers)
    add_event_parsers(subparsers)

    return parser
