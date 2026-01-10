from __future__ import annotations

import argparse
from datetime import datetime
from decimal import Decimal

import sentry_sdk
from rich.table import Table

from app.cli.console import console, error, forbidden, info, success
from app.core.authorization import AuthorizationError, require_role
from app.db.session import get_session
from app.models.employee import Role
from app.services.contract_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    create_contract,
    list_contracts,
    reassign_contract,
    sign_contract,
    update_contract,
)
from app.services.current_employee import NotAuthenticatedError, get_current_employee
from app.utils.phone import format_phone_fr


def _fmt_dt(dt: datetime | None) -> str:
    return dt.strftime("%d/%m/%y %H:%M") if dt else "N/A"


_COLUMNS = {
    "contract_id": "ID Contrat",
    "client_name": "Client",
    "client_email": "Email",
    "client_phone": "Téléphone",
    "company": "Entreprise",
    "sales_name": "Commercial",
    "amount_due": "Restant à payer",
    "total": "Total",
    "signed": "Signé",
    "created_at": "Créé le",
    "updated_at": "Modifié le",
}

_VIEWS = {
    # ID Contract, Client, Entreprise, Commercial, Restant, Total, Signé
    "compact": [
        "contract_id",
        "client_name",
        "company",
        "sales_name",
        "amount_due",
        "total",
        "signed",
    ],
    # ID Contract, Client, Email, Téléphone, Entreprise, Signé, Créé le, Modifié le
    "contact": [
        "contract_id",
        "client_name",
        "client_email",
        "client_phone",
        "company",
        "signed",
        "created_at",
        "updated_at",
    ],
    # tout
    "full": [
        "contract_id",
        "client_name",
        "client_email",
        "client_phone",
        "company",
        "sales_name",
        "amount_due",
        "total",
        "signed",
        "created_at",
        "updated_at",
    ],
}


def cmd_contracts_list(args: argparse.Namespace) -> None:
    """Liste les contrats accessibles à l'utilisateur courant."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        contracts = list_contracts(
            session=session,
            current_employee=employee,
            unsigned=getattr(args, "unsigned", False),
            unpaid=getattr(args, "unpaid", False),
        )

        if not contracts:
            info("Aucun contrat trouvé.")
            return

        view = (getattr(args, "view", None) or "compact").lower()
        columns = _VIEWS.get(view, _VIEWS["compact"])

        table = Table(title=f"Contrats ({view})")

        for col in columns:
            label = _COLUMNS[col]
            if col in {"contract_id"}:
                table.add_column(label, justify="right", no_wrap=True)
            else:
                table.add_column(label)

        for ct in contracts:
            client = getattr(ct, "client", None)
            sales = getattr(ct, "sales_contact", None)

            client_name = "N/A"
            client_email = "N/A"
            client_phone = "N/A"
            company = "N/A"

            if client:
                first = getattr(client, "first_name", "") or ""
                last = getattr(client, "last_name", "") or ""
                client_name = f"{first} {last}".strip() or "N/A"
                client_email = getattr(client, "email", None) or "N/A"
                client_phone = (
                    format_phone_fr(getattr(client, "phone", None) or "") or "N/A"
                )
                company = getattr(client, "company_name", None) or "N/A"

            sales_name = "N/A"
            if sales:
                sf = getattr(sales, "first_name", "") or ""
                sl = getattr(sales, "last_name", "") or ""
                sales_name = f"{sf} {sl}".strip() or "N/A"

            row_map = {
                "contract_id": str(getattr(ct, "id", "N/A")),
                "client_name": client_name,
                "client_email": client_email,
                "client_phone": client_phone,
                "company": company,
                "sales_name": sales_name,
                "amount_due": str(getattr(ct, "amount_due", "N/A")),
                "total": str(getattr(ct, "total_amount", "N/A")),
                "signed": "✅" if getattr(ct, "is_signed", False) else "❌",
                "created_at": _fmt_dt(getattr(ct, "created_at", None)),
                "updated_at": _fmt_dt(getattr(ct, "updated_at", None)),
            }

            table.add_row(*[row_map[c] for c in columns])

        table.caption = f"{len(contracts)} contrat(s)"
        console.print(table)

    except NotAuthenticatedError as exc:
        error(str(exc))
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la récupération des contrats : {exc}")
    finally:
        session.close()


def cmd_contracts_create(args: argparse.Namespace) -> None:
    """Crée un nouveau contrat."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        contract = create_contract(
            session=session,
            current_employee=employee,
            client_id=args.client_id,
            total_amount=Decimal(args.total),
            amount_due=Decimal(args.amount_due),
            is_signed=args.signed,
        )

        success(
            "Contrat créé : "
            f"id={contract.id} | client_id={contract.client_id} | "
            f"sales_contact_id={contract.sales_contact_id} | "
            f"total={contract.total_amount} | due={contract.amount_due} | "
            f"signed={contract.is_signed}"
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
        error(f"Erreur lors de la création du contrat : {exc}")
    finally:
        session.close()


def cmd_contracts_sign(args: argparse.Namespace) -> None:
    """Signe un contrat (réservé MANAGEMENT)."""
    session = get_session()
    try:
        current_employee = get_current_employee(session)
        require_role(current_employee.role, allowed={Role.MANAGEMENT})

        contract = sign_contract(
            session=session,
            current_employee=current_employee,
            contract_id=args.contract_id,
        )

        success(f"Contrat {contract.id} signé.")

    except NotAuthenticatedError as exc:
        error(str(exc))
    except (AuthorizationError, PermissionDeniedError) as exc:
        forbidden(str(exc))
    except NotFoundError as exc:
        error(str(exc))
    except ValidationError as exc:
        info(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la signature du contrat : {exc}")
    finally:
        session.close()


def cmd_contracts_update(args: argparse.Namespace) -> None:
    """Met à jour les montants d'un contrat."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        total_amount = (
            Decimal(args.total_amount) if args.total_amount is not None else None
        )
        amount_due = Decimal(args.amount_due) if args.amount_due is not None else None

        contract = update_contract(
            session=session,
            current_employee=employee,
            contract_id=args.contract_id,
            total_amount=total_amount,
            amount_due=amount_due,
        )

        success(
            "Contrat mis à jour : "
            f"id={contract.id} | client_id={contract.client_id} | "
            f"total={contract.total_amount} | amount_due={contract.amount_due} | "
            f"signed={contract.is_signed} | sales_contact_id={contract.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(str(exc))
    except NotFoundError as exc:
        error(str(exc))
    except ValidationError as exc:
        error(f"Données invalides : {exc}")
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la mise à jour du contrat : {exc}")
    finally:
        session.close()


def cmd_contracts_reassign(args: argparse.Namespace) -> None:
    """Réassigne un contrat à un autre commercial."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        contract = reassign_contract(
            session=session,
            current_employee=employee,
            contract_id=args.contract_id,
            new_sales_contact_id=args.sales_contact_id,
        )

        success(
            "Contrat réassigné : "
            f"id={contract.id} | sales_contact_id={contract.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(str(exc))
    except (ValidationError, NotFoundError) as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la réassignation du contrat : {exc}")
    finally:
        session.close()
