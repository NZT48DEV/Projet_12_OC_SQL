from __future__ import annotations

import argparse

from app.cli.commands.events import cmd_events_create, cmd_events_list


def add_event_parsers(subparsers: argparse._SubParsersAction) -> None:
    p_events = subparsers.add_parser("events", help="Gestion des événements")
    events_sub = p_events.add_subparsers(dest="events_command", required=True)

    p_events_list = events_sub.add_parser("list", help="Lister tous les événements")
    p_events_list.set_defaults(func=cmd_events_list)

    p_events_create = events_sub.add_parser(
        "create",
        help="Créer un événement (SALES, contrat signé requis)",
    )
    p_events_create.add_argument("client_id", type=int)
    p_events_create.add_argument("contract_id", type=int)

    p_events_create.add_argument("start_date", help="Date de début (YYYY-MM-DD)")
    p_events_create.add_argument("start_time", help="Heure de début (HH:MM)")
    p_events_create.add_argument("end_date", help="Date de fin (YYYY-MM-DD)")
    p_events_create.add_argument("end_time", help="Heure de fin (HH:MM)")

    p_events_create.add_argument("location")
    p_events_create.add_argument("attendees", type=int)
    p_events_create.add_argument("--notes", default=None)

    p_events_create.set_defaults(func=cmd_events_create)
