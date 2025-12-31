from __future__ import annotations

import argparse

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
    session = get_session()
    try:
        employee = get_current_employee(session)
        clients = list_clients(session=session, current_employee=employee)

        if not clients:
            print("ℹ️  Aucun client trouvé.")
            return

        print("📋 Clients :")
        for c in clients:
            print(
                f"- id={c.id} | {c.first_name} | {c.last_name} | {c.email} | "
                f"company={c.company_name} | sales_contact_id={c.sales_contact_id}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()


def cmd_clients_create(args: argparse.Namespace) -> None:
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

        print(
            "✅ Client créé : "
            f"id={client.id} | {client.first_name} {client.last_name} | {client.email} | "
            f"company={client.company_name} | sales_contact_id={client.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except ValidationError as exc:
        print(f"❌ Données invalides : {exc}")
    except ClientAlreadyExistsError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la création du client : {exc}")
    finally:
        session.close()


def cmd_clients_update(args: argparse.Namespace) -> None:
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

        print(
            f"Client mis à jour : "
            f"id={client.id} | {client.first_name} {client.last_name} | {client.email} | "
            f"company={client.company_name} | sales_contact_id={client.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        print(f"Erreur : {exc}")
    except PermissionDeniedError as exc:
        print(f"Accès refusé : {exc}")
    except ValidationError as exc:
        print(f"Données invalides : {exc}")
    except ClientAlreadyExistsError as exc:
        print(f"Erreur : {exc}")
    except Exception as exc:
        session.rollback()
        print(f"Erreur lors de la mise à jour du client : {exc}")
    finally:
        session.close()


def cmd_clients_reassign(args: argparse.Namespace) -> None:
    session = get_session()
    try:
        employee = get_current_employee(session)

        client = reassign_client(
            session=session,
            current_employee=employee,
            client_id=args.client_id,
            new_sales_contact_id=args.sales_contact_id,
        )

        print(
            "✅ Client réassigné : "
            f"id={client.id} | sales_contact_id={client.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except (ValidationError, NotFoundError) as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la réassignation du client : {exc}")
    finally:
        session.close()
