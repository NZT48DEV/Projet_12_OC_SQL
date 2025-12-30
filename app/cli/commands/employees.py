from __future__ import annotations

import argparse

from app.core.authorization import AuthorizationError, require_role
from app.core.security import hash_password
from app.db.session import get_session
from app.models.employee import Employee, Role
from app.repositories.employee_repository import EmployeeRepository
from app.services.current_employee import NotAuthenticatedError, get_current_employee


def cmd_management_only(_: argparse.Namespace) -> None:
    """Exécute une action réservée au rôle MANAGEMENT."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        require_role(employee.role, allowed={Role.MANAGEMENT})
        print("🔐 Action MANAGEMENT autorisée.")
    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except AuthorizationError as exc:
        print(f"⛔ Accès refusé : {exc}")
    finally:
        session.close()


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
    session = get_session()
    try:
        # Auth obligatoire
        get_current_employee(session)

        repo = EmployeeRepository(session)

        if args.role:
            employees = repo.list_by_role(Role[args.role])
        else:
            employees = repo.list_all()

        if not employees:
            print("Aucun employé trouvé.")
            return

        print("Employés :")
        for e in employees:
            print(f"- id={e.id} | email={e.email} | role={e.role.value}")

    finally:
        session.close()
