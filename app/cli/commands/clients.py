from __future__ import annotations

import argparse

import sentry_sdk
from rich.table import Table

from app.cli.console import console, error, forbidden, info, success
from app.db.session import get_session
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


def cmd_clients_list(_: argparse.Namespace) -> None:
    """Liste les clients accessibles à l'utilisateur courant."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        clients = list_clients(session=session, current_employee=employee)

        if not clients:
            info("Aucun client trouvé.")
            return

        table = Table(title="Clients")

        table.add_column("ID", justify="right", no_wrap=True)
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Entreprise")
        table.add_column("Sales ID", justify="right")

        for c in clients:
            table.add_row(
                str(c.id),
                f"{c.first_name} {c.last_name}",
                c.email,
                c.company_name or "",
                str(c.sales_contact_id) if c.sales_contact_id is not None else "",
            )

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
