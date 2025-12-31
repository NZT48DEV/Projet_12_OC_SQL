from __future__ import annotations

import argparse
from decimal import Decimal

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


def cmd_contracts_list(_: argparse.Namespace) -> None:
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
                f"- id={ct.id} | client_id={ct.client_id} | "
                f"sales_contact_id={ct.sales_contact_id} | "
                f"total={ct.total_amount} | due={ct.amount_due} | "
                f"signed={ct.is_signed}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()


def cmd_contracts_create(args: argparse.Namespace) -> None:
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

        print(
            "✅ Contrat créé : "
            f"id={contract.id} | client_id={contract.client_id} | "
            f"sales_contact_id={contract.sales_contact_id} | "
            f"total={contract.total_amount} | due={contract.amount_due} | "
            f"signed={contract.is_signed}"
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
        print(f"❌ Erreur lors de la création du contrat : {exc}")
    finally:
        session.close()


def cmd_contracts_sign(args: argparse.Namespace) -> None:
    session = get_session()
    current_employee = get_current_employee(session)

    try:
        require_role(
            current_employee.role,
            allowed={Role.MANAGEMENT},
        )

        contract = sign_contract(
            session,
            current_employee,
            contract_id=args.contract_id,
        )

        print(f"✅ Contrat {contract.id} signé.")

    except AuthorizationError as e:
        print(f"⛔ {e}")
    except PermissionDeniedError as e:
        print(f"⛔ {e}")
    except NotFoundError as e:
        print(f"❌ {e}")
    except ValidationError as e:
        print(f"⚠️ {e}")


def cmd_contracts_update(args: argparse.Namespace) -> None:
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

        print(
            "Contrat mis à jour : "
            f"id={contract.id} | client_id={contract.client_id} | "
            f"total={contract.total_amount} | amount_due={contract.amount_due} | "
            f"signed={contract.is_signed} | sales_contact_id={contract.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        print(f"Erreur : {exc}")
    except PermissionDeniedError as exc:
        print(f"Accès refusé : {exc}")
    except NotFoundError as exc:
        print(f"Erreur : {exc}")
    except ValidationError as exc:
        print(f"Données invalides : {exc}")
    except Exception as exc:
        session.rollback()
        print(f"Erreur lors de la mise à jour du contrat : {exc}")
    finally:
        session.close()


def cmd_contracts_reassign(args: argparse.Namespace) -> None:
    session = get_session()
    try:
        employee = get_current_employee(session)

        contract = reassign_contract(
            session=session,
            current_employee=employee,
            contract_id=args.contract_id,
            new_sales_contact_id=args.sales_contact_id,
        )

        print(
            "✅ Contrat réassigné : "
            f"id={contract.id} | sales_contact_id={contract.sales_contact_id}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except (ValidationError, NotFoundError) as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la réassignation du contrat : {exc}")
    finally:
        session.close()
