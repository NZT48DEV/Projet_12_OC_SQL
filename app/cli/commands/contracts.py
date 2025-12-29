from __future__ import annotations

import argparse

from app.db.session import get_session
from app.services.contract_service import list_contracts
from app.services.current_employee import NotAuthenticatedError, get_current_employee


def cmd_contracts_list(_: argparse.Namespace) -> None:
    """Liste tous les contrats (lecture seule, authentification requise)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        contracts = list_contracts(session=session, current_employee=employee)

        if not contracts:
            print("ℹ️  Aucun contrat trouvé.")
            return

        print("📋 Contrats :")
        for ct in contracts:
            print(
                f"- id={ct.id} | "
                f"client_id={ct.client_id} | "
                f"sales_contact_id={ct.sales_contact_id} | "
                f"total={ct.total_amount} | "
                f"due={ct.amount_due} | "
                f"signed={ct.is_signed} | "
                f"created_at={ct.created_at}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la récupération des contrats : {exc}")
    finally:
        session.close()
