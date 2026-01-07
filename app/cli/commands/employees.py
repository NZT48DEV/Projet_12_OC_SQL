from __future__ import annotations

import argparse

import sentry_sdk
from rich.table import Table

from app.cli.console import console, error, forbidden, info, success, warning
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


def _fmt_dt(dt) -> str:
    """Formate une date/heure pour affichage CLI."""
    return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else "—"


def cmd_create_employee(args: argparse.Namespace) -> None:
    """Crée un employé (bootstrap du premier MANAGEMENT possible)."""
    session = get_session()
    try:
        employees_count = session.query(Employee).count()
        if employees_count == 0:
            if args.role != Role.MANAGEMENT.name:
                error("Le premier compte doit être MANAGEMENT.")
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

        success(
            f"Employé créé : {new_employee.first_name} {new_employee.last_name} "
            f"(email={new_employee.email}, role={new_employee.role})"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except AuthorizationError as exc:
        forbidden(f"Accès refusé : {exc}")
    except KeyError:
        error("Rôle invalide. Choix possibles : MANAGEMENT, SALES, SUPPORT.")
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la création de l'employé : {exc}")
    finally:
        session.close()


def cmd_employees_list(args: argparse.Namespace) -> None:
    """Liste les employés (avec filtre optionnel par rôle)."""
    session = get_session()
    try:
        current_employee = get_current_employee(session)
        is_management = current_employee.role == Role.MANAGEMENT

        repo = EmployeeRepository(session)
        employees = repo.list_by_role(Role[args.role]) if args.role else repo.list_all()

        if not employees:
            info("Aucun employé trouvé.")
            return

        table = Table(title="Employés")

        table.add_column("ID", justify="right", no_wrap=True)
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Rôle", no_wrap=True)
        table.add_column("Statut", justify="center", no_wrap=True)

        # Colonnes sensibles : uniquement MANAGEMENT
        if is_management:
            table.add_column("Créé le", no_wrap=True)
            table.add_column("Désactivé le", no_wrap=True)
            table.add_column("Réactivé le", no_wrap=True)

        for e in employees:
            status = "✅ Actif" if e.is_active else "⛔ Désactivé"

            base_row = [
                str(e.id),
                f"{e.first_name} {e.last_name}",
                e.email,
                e.role.value,
                status,
            ]

            if is_management:
                base_row.extend(
                    [
                        _fmt_dt(e.created_at),
                        _fmt_dt(e.deactivated_at) if not e.is_active else "—",
                        _fmt_dt(e.reactivated_at),
                    ]
                )

            table.add_row(*base_row)

        table.caption = f"{len(employees)} employé(s)"
        console.print(table)

    except NotAuthenticatedError as exc:
        error(str(exc))
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la récupération des employés : {exc}")
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

        success(
            f"Employé désactivé : id={employee.id} | email={employee.email} | "
            f"désactivé_le={_fmt_dt(employee.deactivated_at)}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except ValidationError as exc:
        warning(str(exc))
    except NotFoundError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la désactivation de l'employé : {exc}")
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

        success(
            f"Employé réactivé : id={employee.id} | email={employee.email} | "
            f"réactivé_le={_fmt_dt(employee.reactivated_at)}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except ValidationError as exc:
        warning(str(exc))
    except NotFoundError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la réactivation de l'employé : {exc}")
    finally:
        session.close()


def cmd_employees_delete(args: argparse.Namespace) -> None:
    """Supprime un employé (soft par défaut, hard avec --hard + --confirm)."""
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
            success(f"Employé supprimé définitivement : id={args.employee_id}")
            return

        # SOFT DELETE
        employee = deactivate_employee(
            session=session,
            current_employee=current_employee,
            employee_id=args.employee_id,
        )

        success(
            f"Employé désactivé : id={employee.id} | email={employee.email} | "
            f"désactivé_le={_fmt_dt(employee.deactivated_at)}"
        )

    except NotAuthenticatedError as exc:
        error(str(exc))
    except PermissionDeniedError as exc:
        forbidden(f"Accès refusé : {exc}")
    except ValidationError as exc:
        warning(str(exc))
    except NotFoundError as exc:
        error(str(exc))
    except Exception as exc:
        session.rollback()
        sentry_sdk.capture_exception(exc)
        error(f"Erreur lors de la suppression/désactivation de l'employé : {exc}")
    finally:
        session.close()
