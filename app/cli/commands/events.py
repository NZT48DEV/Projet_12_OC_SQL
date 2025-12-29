from __future__ import annotations

import argparse

from app.db.session import get_session
from app.services.current_employee import NotAuthenticatedError, get_current_employee
from app.services.event_service import list_events


def cmd_events_list(_: argparse.Namespace) -> None:
    """Liste tous les événements (lecture seule, authentification requise)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        events = list_events(session=session, current_employee=employee)

        if not events:
            print("ℹ️  Aucun événement trouvé.")
            return

        print("📋 Événements :")
        for ev in events:
            start_str = ev.start_date.strftime("%Y-%m-%d %H:%M")
            end_str = ev.end_date.strftime("%Y-%m-%d %H:%M")
            created_str = ev.created_at.strftime("%Y-%m-%d %H:%M")

            print(
                f"- id={ev.id} | "
                f"contract_id={ev.contract_id} | "
                f"client_id={ev.client_id} | "
                f"support_contact_id={ev.support_contact_id} | "
                f"start={start_str} | "
                f"end={end_str} | "
                f"location={ev.location} | "
                f"attendees={ev.attendees} | "
                f"notes={ev.notes} | "
                f"created_at={created_str}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la récupération des événements : {exc}")
    finally:
        session.close()
