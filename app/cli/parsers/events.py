from __future__ import annotations

import argparse

from app.cli.commands.events import cmd_events_list


def add_event_parsers(subparsers: argparse._SubParsersAction) -> None:
    p_events = subparsers.add_parser("events", help="Gestion des événements")
    events_sub = p_events.add_subparsers(dest="events_command", required=True)

    p_events_list = events_sub.add_parser("list", help="Lister tous les événements")
    p_events_list.set_defaults(func=cmd_events_list)
