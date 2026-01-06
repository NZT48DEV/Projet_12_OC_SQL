from __future__ import annotations

import argparse
from datetime import datetime

import sentry_sdk

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


def cmd_events_list(_: argparse.Namespace) -> None:
    session = get_session()
    try:
        employee = get_current_employee(session)
        events = list_events(session=session, current_employee=employee)

        if not events:
            print("ℹ️  Aucun événement trouvé.")
            return

        print("📋 Événements :")
        for ev in events:
            print(
                f"- id={ev.id} | contract_id={ev.contract_id} | "
                f"client_id={ev.client_id} | support_contact_id={ev.support_contact_id} | "
                f"start={ev.start_date} | end={ev.end_date} | "
                f"location={ev.location} | attendees={ev.attendees}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        print(f"❌ Erreur lors de la récupération des événements : {exc}")
    finally:
        session.close()


def cmd_events_create(args: argparse.Namespace) -> None:
    session = get_session()
    try:
        employee = get_current_employee(session)

        try:
            start_dt = datetime.fromisoformat(f"{args.start_date} {args.start_time}")
            end_dt = datetime.fromisoformat(f"{args.end_date} {args.end_time}")
        except ValueError:
            print(
                "❌ Format de date/heure invalide. Attendu : "
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

        print(
            "✅ Événement créé : "
            f"id={event.id} | client_id={event.client_id} | "
            f"contract_id={event.contract_id} | start={event.start_date} | "
            f"end={event.end_date} | location={event.location}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except ValidationError as exc:
        print(f"❌ Données invalides : {exc}")
    except NotFoundError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        print(f"❌ Erreur lors de la création de l'événement : {exc}")
    finally:
        session.close()


def cmd_events_update(args: argparse.Namespace) -> None:
    session = get_session()
    try:
        employee = get_current_employee(session)

        start_dt = None
        end_dt = None

        # Cohérence des paramètres date/heure
        if (args.start_date is None) ^ (args.start_time is None):
            print("❌ Pour modifier le début, fournissez --start-date ET --start-time.")
            return
        if (args.end_date is None) ^ (args.end_time is None):
            print("❌ Pour modifier la fin, fournissez --end-date ET --end-time.")
            return

        if args.start_date is not None:
            try:
                start_dt = datetime.fromisoformat(
                    f"{args.start_date} {args.start_time}"
                )
            except ValueError:
                print("❌ Format début invalide. Attendu : YYYY-MM-DD et HH:MM.")
                return

        if args.end_date is not None:
            try:
                end_dt = datetime.fromisoformat(f"{args.end_date} {args.end_time}")
            except ValueError:
                print("❌ Format fin invalide. Attendu : YYYY-MM-DD et HH:MM.")
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

        print(
            "Événement mis à jour : "
            f"id={event.id} | client_id={event.client_id} | contract_id={event.contract_id} | "
            f"support_contact_id={event.support_contact_id} | start={event.start_date} | "
            f"end={event.end_date} | location={event.location} | attendees={event.attendees}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except ValidationError as exc:
        print(f"❌ Données invalides : {exc}")
    except NotFoundError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        print(f"❌ Erreur lors de la mise à jour de l'événement : {exc}")
    finally:
        session.close()


def cmd_events_reassign(args: argparse.Namespace) -> None:
    session = get_session()
    try:
        employee = get_current_employee(session)

        event = reassign_event(
            session=session,
            current_employee=employee,
            event_id=args.event_id,
            support_contact_id=args.support_contact_id,
        )

        print(
            "✅ Événement réassigné : "
            f"id={event.id} | support_contact_id={event.support_contact_id}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ {exc}")
    except (ValidationError, NotFoundError) as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        print(f"❌ Erreur lors de la réassignation de l'événement : {exc}")
    finally:
        session.close()
