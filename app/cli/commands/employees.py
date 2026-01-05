from __future__ import annotations

import argparse

from app.core.authorization import AuthorizationError, require_role
from app.core.security import hash_password
from app.db.session import get_session
from app.models.employee import Employee, Role
from app.repositories.employee_repository import EmployeeRepository
from app.services.current_employee import NotAuthenticatedError, get_current_employee
from app.services.employee_service import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
    deactivate_employee,
    hard_delete_employee,
    reactivate_employee,
)


def cmd_create_employee(args: argparse.Namespace) -> None:
    """Crée un employé (bootstrap du premier MANAGEMENT possible)."""
    session = get_session()
    try:
        employees_count = session.query(Employee).count()
        if employees_count == 0:
            if args.role != Role.MANAGEMENT.name:
                print("❌ Le premier compte doit être MANAGEMENT.")
                return
        else:
            current_employee = get_current_employee(session)
            require_role(current_employee.role, allowed={Role.MANAGEMENT})

        new_employee = Employee(
            first_name=args.first_name,
            last_name=args.last_name,
            email=args.email,
            role=Role[args.role],
            password_hash=hash_password(args.password),
        )
        session.add(new_employee)
        session.commit()
        session.refresh(new_employee)

        print(
            f"✅ Employé créé : {new_employee.first_name} {new_employee.last_name} "
            f"(email={new_employee.email}, role={new_employee.role})"
        )
    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except AuthorizationError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except KeyError:
        print("❌ Rôle invalide. Choix possibles : MANAGEMENT, SALES, SUPPORT.")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la création de l'employé : {exc}")
    finally:
        session.close()


def cmd_employees_list(args: argparse.Namespace) -> None:
    """Liste les employés (auth obligatoire)."""
    session = get_session()
    try:
        get_current_employee(session)

        repo = EmployeeRepository(session)
        employees = repo.list_by_role(Role[args.role]) if args.role else repo.list_all()

        if not employees:
            print("Aucun employé trouvé.")
            return

        print("Employés :")
        for e in employees:
            print(f"- id={e.id} | email={e.email} | role={e.role.value}")

    finally:
        session.close()


def cmd_employees_deactivate(args: argparse.Namespace) -> None:
    """Désactive un employé (soft delete) — réservé MANAGEMENT."""
    session = get_session()
    try:
        current_employee = get_current_employee(session)

        employee = deactivate_employee(
            session=session,
            current_employee=current_employee,
            employee_id=args.employee_id,
        )

        deactivated_at = (
            employee.deactivated_at.strftime("%d/%m/%Y %H:%M:%S")
            if employee.deactivated_at
            else "N/A"
        )

        print(
            f"✅ Employé désactivé : id={employee.id} | email={employee.email} | "
            f"désactivé_le={deactivated_at}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except ValidationError as exc:
        print(f"⚠️ {exc}")
    except NotFoundError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la désactivation de l'employé : {exc}")
    finally:
        session.close()


def cmd_employees_reactivate(args: argparse.Namespace) -> None:
    """Réactive un employé désactivé — réservé MANAGEMENT."""
    session = get_session()
    try:
        current_employee = get_current_employee(session)

        employee = reactivate_employee(
            session=session,
            current_employee=current_employee,
            employee_id=args.employee_id,
        )

        reactivated_at = (
            employee.reactivated_at.strftime("%d/%m/%Y %H:%M:%S")
            if getattr(employee, "reactivated_at", None)
            else "N/A"
        )

        print(
            f"✅ Employé réactivé : id={employee.id} | email={employee.email} | "
            f"réactivé_le={reactivated_at}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except ValidationError as exc:
        print(f"⚠️ {exc}")
    except NotFoundError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la réactivation de l'employé : {exc}")
    finally:
        session.close()


def cmd_employees_delete(args: argparse.Namespace) -> None:
    """
    Supprime un employé.
    - par défaut : soft delete (désactivation)
    - avec --hard : suppression définitive (dangereux) + --confirm obligatoire
    Réservé MANAGEMENT.
    """
    session = get_session()
    try:
        current_employee = get_current_employee(session)

        # HARD DELETE
        if getattr(args, "hard", False):
            if args.confirm is None:
                raise ValidationError("Option --confirm obligatoire avec --hard.")

            hard_delete_employee(
                session=session,
                current_employee=current_employee,
                employee_id=args.employee_id,
                confirm_employee_id=args.confirm,
            )
            print(f"✅ Employé supprimé définitivement : id={args.employee_id}")
            return

        # SOFT DELETE (par défaut)
        employee = deactivate_employee(
            session=session,
            current_employee=current_employee,
            employee_id=args.employee_id,
        )

        deactivated_at = (
            employee.deactivated_at.strftime("%d/%m/%Y %H:%M:%S")
            if employee.deactivated_at
            else "N/A"
        )

        print(
            f"✅ Employé désactivé : id={employee.id} | email={employee.email} | "
            f"désactivé_le={deactivated_at}"
        )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except PermissionDeniedError as exc:
        print(f"⛔ Accès refusé : {exc}")
    except ValidationError as exc:
        print(f"⚠️ {exc}")
    except NotFoundError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la suppression/désactivation de l'employé : {exc}")
    finally:
        session.close()
