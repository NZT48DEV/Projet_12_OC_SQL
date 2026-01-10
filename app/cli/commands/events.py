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
    unassign_event_support,
    update_event,
)


def _fmt_datetime(dt: datetime | None) -> str:
    return dt.strftime("%d/%m/%y %H:%M") if dt else "N/A"


def _fmt_event_dt(dt: datetime | None) -> str:
    return dt.strftime("%d/%m/%y %H:%M") if dt else "N/A"


# Colonnes disponibles (clé -> label)
_COLUMNS = {
    "event_id": "ID Event",
    "contract_id": "Contrat ID",
    "client_name": "Client",
    "client_contact": "Contact client",
    "start": "Début",
    "end": "Fin",
    "support_name": "Support",
    "location": "Lieu",
    "attendees": "Participants",
    "notes": "Notes",
    "created_at": "Créé le",
    "updated_at": "Modifié le",
}

# Presets de vues
_VIEWS = {
    "compact": [
        "event_id",
        "contract_id",
        "client_name",
        "start",
        "end",
        "support_name",
        "location",
        "attendees",
    ],
    "contact": [
        "event_id",
        "contract_id",
        "client_name",
        "client_contact",
        "start",
        "end",
        "support_name",
        "location",
        "attendees",
    ],
    "full": [
        "event_id",
        "contract_id",
        "client_name",
        "client_contact",
        "start",
        "end",
        "support_name",
        "location",
        "attendees",
        "notes",
        "created_at",
        "updated_at",
    ],
}


def cmd_events_list(args: argparse.Namespace) -> None:
    """Liste les événements accessibles à l'utilisateur courant."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        events = list_events(
            session=session,
            current_employee=employee,
            without_support=getattr(args, "without_support", False),
            assigned_to_me=getattr(args, "assigned_to_me", False),
        )

        if not events:
            info("Aucun événement trouvé.")
            return

        view = (getattr(args, "view", None) or "compact").lower()
        columns = _VIEWS.get(view, _VIEWS["compact"])

        table = Table(title=f"Événements ({view})")

        # Ajout dynamique des colonnes
        for col in columns:
            label = _COLUMNS[col]
            if col in {"event_id", "contract_id", "attendees"}:
                table.add_column(label, justify="right", no_wrap=True)
            else:
                table.add_column(label)

        for ev in events:
            client = getattr(ev, "client", None)
            support = getattr(ev, "support_contact", None)

            client_name = "N/A"
            client_contact = "N/A"
            if client:
                first = getattr(client, "first_name", "") or ""
                last = getattr(client, "last_name", "") or ""
                client_name = f"{first} {last}".strip() or "N/A"

                email = getattr(client, "email", None) or "N/A"
                phone = getattr(client, "phone", None) or "N/A"
                # ✅ contact sur 2 lignes, lisible sans réglages Rich
                client_contact = f"{email}\n{phone}"

            support_name = "N/A"
            if support:
                sf = getattr(support, "first_name", "") or ""
                sl = getattr(support, "last_name", "") or ""
                support_name = f"{sf} {sl}".strip() or "N/A"

            notes = (getattr(ev, "notes", None) or "").strip() or "N/A"

            row_map = {
                "event_id": str(getattr(ev, "id", "N/A")),
                "contract_id": str(getattr(ev, "contract_id", "N/A")),
                "client_name": client_name,
                "client_contact": client_contact,
                "start": _fmt_event_dt(getattr(ev, "start_date", None)),
                "end": _fmt_event_dt(getattr(ev, "end_date", None)),
                "support_name": support_name,
                "location": getattr(ev, "location", None) or "N/A",
                "attendees": (
                    str(getattr(ev, "attendees", "N/A"))
                    if getattr(ev, "attendees", None) is not None
                    else "N/A"
                ),
                "notes": notes,
                "created_at": _fmt_datetime(getattr(ev, "created_at", None)),
                "updated_at": _fmt_datetime(getattr(ev, "updated_at", None)),
            }

            table.add_row(*[row_map[c] for c in columns])

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
    """Réassigne le support d'un événement."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        if getattr(args, "unassign_support", False):
            event = unassign_event_support(
                session=session,
                current_employee=employee,
                event_id=args.event_id,
            )
            success(f"Support retiré : id={event.id}")
            return

        event = reassign_event(
            session=session,
            current_employee=employee,
            event_id=args.event_id,
            support_contact_id=args.support_contact_id,
        )
        success(
            f"Événement réassigné : id={event.id} | support_contact_id={event.support_contact_id}"
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
