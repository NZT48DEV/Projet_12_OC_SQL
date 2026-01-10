from __future__ import annotations

import argparse

import sentry_sdk
from rich.table import Table

from app.cli.console import console, error, forbidden, info, success
from app.db.session import get_session
from app.models.employee import Role
from app.services.client_service import (
    ClientAlreadyExistsError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    create_client,
    list_clients,
    reassign_client,
    update_client,
)
from app.services.current_employee import NotAuthenticatedError, get_current_employee
from app.utils.phone import format_phone_fr


def cmd_clients_list(_: argparse.Namespace) -> None:
    """Liste les clients accessibles à l'utilisateur courant."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        clients = list_clients(session=session, current_employee=employee)

        if not clients:
            info("Aucun client trouvé.")
            return

        is_management = employee.role == Role.MANAGEMENT

        table = Table(title="Clients", show_lines=True)

        # Affichage de l'ID uniquement pour MANAGEMENT
        if is_management:
            table.add_column("ID Client", justify="center", no_wrap=True)

        table.add_column("Nom complet", justify="center")
        table.add_column("Email", justify="center", no_wrap=True)
        table.add_column("Téléphone", justify="center", no_wrap=True)
        table.add_column("Entreprise", justify="center")
        table.add_column("Contact Commercial", justify="center")
        table.add_column("Créé le", justify="center", no_wrap=True)
        table.add_column("Modifié le", justify="center", no_wrap=True)

        for c in clients:
            commercial = (
                f"{c.sales_contact.first_name} {c.sales_contact.last_name}"
                if getattr(c, "sales_contact", None)
                else "N/A"
            )

            row: list[str] = []

            if is_management:
                row.append(str(c.id))

            row.extend(
                [
                    f"{c.first_name} {c.last_name}",
                    c.email,
                    format_phone_fr(c.phone) or "N/A",
                    c.company_name or "N/A",
                    commercial,
                    c.created_at.strftime("%Y-%m-%d %H:%M"),
                    c.updated_at.strftime("%Y-%m-%d %H:%M") if c.updated_at else "N/A",
                ]
            )

            table.add_row(*row)

        table.caption = f"{len(clients)} client(s)"
        console.print(table)

    except NotAuthenticatedError as exc:
        error(str(exc))
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la récupération des clients : {exc}")
    finally:
        session.close()


def cmd_clients_create(args: argparse.Namespace) -> None:
    """Crée un nouveau client."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        client = create_client(
            session=session,
            current_employee=employee,
            first_name=args.first_name,
            last_name=args.last_name,
            email=args.email,
            phone=args.phone,
            company_name=args.company_name,
        )

        success(
            "Client créé : "
            f"id={client.id} | {client.first_name} {client.last_name} | {client.email} | "
            f"company={client.company_name} | sales_contact_id={client.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except ValidationError as exc:
        error(f"Données invalides : {exc}")
    except ClientAlreadyExistsError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la création du client : {exc}")
    finally:
        session.close()


def cmd_clients_update(args: argparse.Namespace) -> None:
    """Met à jour les informations d'un client."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        client = update_client(
            session=session,
            current_employee=employee,
            client_id=args.client_id,
            first_name=args.first_name,
            last_name=args.last_name,
            email=args.email,
            phone=args.phone,
            company_name=args.company_name,
        )

        success(
            "Client mis à jour : "
            f"id={client.id} | {client.first_name} {client.last_name} | {client.email} | "
            f"company={client.company_name} | sales_contact_id={client.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except ValidationError as exc:
        error(f"Données invalides : {exc}")
    except ClientAlreadyExistsError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la mise à jour du client : {exc}")
    finally:
        session.close()


def cmd_clients_reassign(args: argparse.Namespace) -> None:
    """Réassigne un client à un autre commercial."""
    session = get_session()
    try:
        employee = get_current_employee(session)

        client = reassign_client(
            session=session,
            current_employee=employee,
            client_id=args.client_id,
            new_sales_contact_id=args.sales_contact_id,
        )

        success(
            "Client réassigné : "
            f"id={client.id} | sales_contact_id={client.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except (ValidationError, NotFoundError) as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la réassignation du client : {exc}")
    finally:
        session.close()
