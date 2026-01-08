from __future__ import annotations

import argparse
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


def cmd_contracts_list(_: argparse.Namespace) -> None:
    """Liste les contrats accessibles à l'utilisateur courant."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        contracts = list_contracts(session=session, current_employee=employee)

        if not contracts:
            info("Aucun contrat trouvé.")
            return

        is_management = employee.role == Role.MANAGEMENT

        table = Table(title="Contrats", show_lines=True)

        if is_management:
            table.add_column("ID", justify="right", no_wrap=True)

        table.add_column("Client", justify="center", no_wrap=True)
        table.add_column("Email", justify="center", no_wrap=True)
        table.add_column("Téléphone", justify="center", no_wrap=True)
        table.add_column("Entreprise", justify="center", no_wrap=True)
        table.add_column("Commercial", justify="center", no_wrap=True)
        table.add_column("Restant à payer", justify="center", no_wrap=True)
        table.add_column("Total", justify="center", no_wrap=True)
        table.add_column("Signé", justify="center", no_wrap=True)
        table.add_column("Créé le", justify="center")
        table.add_column("Modifié le", justify="center")

        for ct in contracts:
            client = getattr(ct, "client", None)
            sales = getattr(ct, "sales_contact", None)

            client_name = f"{client.first_name} {client.last_name}" if client else "N/A"
            client_email = client.email if client and client.email else "N/A"
            client_phone = (format_phone_fr(client.phone) or "N/A") if client else "N/A"
            client_company = (client.company_name or "N/A") if client else "N/A"
            client_created = (
                client.created_at.strftime("%Y-%m-%d %H:%M")
                if client and client.created_at
                else "N/A"
            )
            client_updated = (
                client.updated_at.strftime("%Y-%m-%d %H:%M")
                if client and getattr(client, "updated_at", None)
                else "N/A"
            )

            sales_name = f"{sales.first_name} {sales.last_name}" if sales else "N/A"

            row: list[str] = []
            if is_management:
                row.append(str(ct.id))

            row.extend(
                [
                    client_name,
                    client_email,
                    client_phone,
                    client_company,
                    sales_name,
                    str(ct.amount_due),
                    str(ct.total_amount),
                    "✅" if ct.is_signed else "❌",
                    client_created,
                    client_updated,
                ]
            )

            table.add_row(*row)

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
