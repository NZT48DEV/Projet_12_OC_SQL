from __future__ import annotations

import argparse
from datetime import datetime

import sentry_sdk
from rich.table import Table

from app.cli.console import console, error, forbidden, info, success, warning
from app.db.session import get_session
from app.services.current_employee import NotAuthenticatedError, get_current_employee
from app.services.event_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    create_event,
    list_events,
    reassign_event,
    update_event,
)


def _fmt_dt(dt: datetime | None) -> str:
    """Formate une date/heure pour affichage CLI."""
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"


def cmd_events_list(_: argparse.Namespace) -> None:
    """Liste les événements accessibles à l'utilisateur courant."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        events = list_events(session=session, current_employee=employee)

        if not events:
            info("Aucun événement trouvé.")
            return

        table = Table(title="Événements")

        table.add_column("ID", justify="right", no_wrap=True)
        table.add_column("Client ID", justify="right")
        table.add_column("Contrat ID", justify="right")
        table.add_column("Support ID", justify="right")
        table.add_column("Début", no_wrap=True)
        table.add_column("Fin", no_wrap=True)
        table.add_column("Lieu")
        table.add_column("Participants", justify="right")

        for ev in events:
            table.add_row(
                str(ev.id),
                str(ev.client_id) if ev.client_id is not None else "",
                str(ev.contract_id) if ev.contract_id is not None else "",
                str(ev.support_contact_id) if ev.support_contact_id is not None else "",
                _fmt_dt(ev.start_date),
                _fmt_dt(ev.end_date),
                ev.location or "",
                str(ev.attendees) if ev.attendees is not None else "",
            )

        table.caption = f"{len(events)} événement(s)"
        console.print(table)

    except NotAuthenticatedError as exc:
        error(str(exc))
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la récupération des événements : {exc}")
    finally:
        session.close()


def cmd_events_create(args: argparse.Namespace) -> None:
    """Crée un événement."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        try:
            start_dt = datetime.fromisoformat(f"{args.start_date} {args.start_time}")
            end_dt = datetime.fromisoformat(f"{args.end_date} {args.end_time}")
        except ValueError:
            error(
                "Format de date/heure invalide. Attendu : "
                "start_date=YYYY-MM-DD start_time=HH:MM end_date=YYYY-MM-DD end_time=HH:MM"
            )
            return

        event = create_event(
            session=session,
            current_employee=employee,
            client_id=args.client_id,
            contract_id=args.contract_id,
            start_date=start_dt,
            end_date=end_dt,
            location=args.location,
            attendees=args.attendees,
            notes=args.notes,
        )

        success(
            "Événement créé : "
            f"id={event.id} | client_id={event.client_id} | "
            f"contract_id={event.contract_id} | start={event.start_date} | "
            f"end={event.end_date} | location={event.location}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except ValidationError as exc:
        error(f"Données invalides : {exc}")
    except NotFoundError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la création de l'événement : {exc}")
    finally:
        session.close()


def cmd_events_update(args: argparse.Namespace) -> None:
    """Met à jour un événement."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        start_dt = None
        end_dt = None

        # Cohérence des paramètres date/heure
        if (args.start_date is None) ^ (args.start_time is None):
            error("Pour modifier le début, fournissez --start-date ET --start-time.")
            return
        if (args.end_date is None) ^ (args.end_time is None):
            error("Pour modifier la fin, fournissez --end-date ET --end-time.")
            return

        if args.start_date is not None:
            try:
                start_dt = datetime.fromisoformat(
                    f"{args.start_date} {args.start_time}"
                )
            except ValueError:
                error("Format début invalide. Attendu : YYYY-MM-DD et HH:MM.")
                return

        if args.end_date is not None:
            try:
                end_dt = datetime.fromisoformat(f"{args.end_date} {args.end_time}")
            except ValueError:
                error("Format fin invalide. Attendu : YYYY-MM-DD et HH:MM.")
                return

        event = update_event(
            session=session,
            current_employee=employee,
            event_id=args.event_id,
            start_date=start_dt,
            end_date=end_dt,
            location=args.location,
            attendees=args.attendees,
            notes=args.notes,
            support_contact_id=args.support_contact_id,
        )

        success(
            "Événement mis à jour : "
            f"id={event.id} | client_id={event.client_id} | contract_id={event.contract_id} | "
            f"support_contact_id={event.support_contact_id} | start={event.start_date} | "
            f"end={event.end_date} | location={event.location} | attendees={event.attendees}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except ValidationError as exc:
        error(f"Données invalides : {exc}")
    except NotFoundError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la mise à jour de l'événement : {exc}")
    finally:
        session.close()


def cmd_events_reassign(args: argparse.Namespace) -> None:
    """Réassigne un événement à un support."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        event = reassign_event(
            session=session,
            current_employee=employee,
            event_id=args.event_id,
            support_contact_id=args.support_contact_id,
        )

        success(
            "Événement réassigné : "
            f"id={event.id} | support_contact_id={event.support_contact_id}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(str(exc))
    except ValidationError as exc:
        warning(str(exc))
    except NotFoundError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la réassignation de l'événement : {exc}")
    finally:
        session.close()
