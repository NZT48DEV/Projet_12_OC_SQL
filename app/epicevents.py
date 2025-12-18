# app/epicevents.py
from __future__ import annotations

import argparse

from app.core.authorization import AuthorizationError, require_role
from app.core.security import hash_password
from app.core.session_store import clear_session, save_current_employee
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.employee import Employee, Role
from app.services.auth_service import AuthenticationError, authenticate_employee
from app.services.current_employee import NotAuthenticatedError, get_current_employee


def cmd_init_db(_: argparse.Namespace) -> None:
    """Commande CLI: initialise la base (création des tables)."""
    init_db()
    print("✅ Tables créées dans la base epic_crm.")


def cmd_create_employee(args: argparse.Namespace) -> None:
    """
    Commande CLI: crée un employé (usage dev/setup).

    Attend: first_name, last_name, email, role, password.
    Hash le mot de passe avant stockage.
    """
    session = SessionLocal()
    try:
        employee = Employee(
            first_name=args.first_name,
            last_name=args.last_name,
            email=args.email,
            role=args.role,  # string parmi les choices (valeurs Role)
            password_hash=hash_password(args.password),
        )
        session.add(employee)
        session.commit()
        session.refresh(employee)
        print(
            f"✅ Employé créé : id={employee.id}, "
            f"email={employee.email}, role={employee.role}"
        )
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur création employé : {exc}")
    finally:
        session.close()


def cmd_login(args: argparse.Namespace) -> None:
    """
    Commande CLI: authentifie un employé et persiste une session locale.

    En cas de succès: sauvegarde l'id de l'employé dans le session_store.
    """
    session = SessionLocal()
    try:
        employee = authenticate_employee(session, args.email, args.password)
        save_current_employee(employee.id)
        print(
            f"✅ Connecté : {employee.first_name} "
            f"{employee.last_name} (role={employee.role})"
        )
        print("✅ Session sauvegardée (auth persistante).")
    except AuthenticationError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()


def cmd_logout(_: argparse.Namespace) -> None:
    """Commande CLI: supprime la session locale (déconnexion)."""
    clear_session()
    print("✅ Déconnecté.")


def cmd_whoami(_: argparse.Namespace) -> None:
    """Commande CLI: affiche l'utilisateur actuellement connecté (si session valide)."""
    session = SessionLocal()
    try:
        employee = get_current_employee(session)
        print(
            f"✅ Session active : {employee.first_name} {employee.last_name} "
            f"(role={employee.role}, id={employee.id})"
        )
    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()


def cmd_management_only(_: argparse.Namespace) -> None:
    """
    Commande CLI: exemple de commande protégée par autorisation.

    Autorise uniquement les utilisateurs ayant le rôle MANAGEMENT.
    """
    session = SessionLocal()
    try:
        employee = get_current_employee(session)
        require_role(employee.role, {Role.MANAGEMENT})
        print("✅ Action autorisée (MANAGEMENT).")
    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except AuthorizationError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()


def build_parser() -> argparse.ArgumentParser:
    """
    Construit le parseur CLI et enregistre les sous-commandes.

    Returns:
        Le parser argparse configuré.
    """
    parser = argparse.ArgumentParser(prog="epicevents")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init-db", help="Créer les tables en base (setup/dev)")
    p_init.set_defaults(func=cmd_init_db)

    p_create = sub.add_parser("create-employee", help="Créer un employé (dev)")
    p_create.add_argument("first_name")
    p_create.add_argument("last_name")
    p_create.add_argument("email")
    p_create.add_argument(
        "role",
        choices=[r.value for r in Role],
        help="Rôle (MANAGEMENT, SALES, SUPPORT)",
    )
    p_create.add_argument("password")
    p_create.set_defaults(func=cmd_create_employee)

    p_login = sub.add_parser("login", help="Se connecter avec email + mot de passe")
    p_login.add_argument("email")
    p_login.add_argument("password")
    p_login.set_defaults(func=cmd_login)

    p_whoami = sub.add_parser(
        "whoami", help="Afficher l'utilisateur actuellement connecté"
    )
    p_whoami.set_defaults(func=cmd_whoami)

    p_logout = sub.add_parser(
        "logout", help="Se déconnecter (supprime la session locale)"
    )
    p_logout.set_defaults(func=cmd_logout)

    p_mgmt = sub.add_parser(
        "management-only", help="Commande réservée au rôle MANAGEMENT"
    )
    p_mgmt.set_defaults(func=cmd_management_only)

    return parser


def main() -> None:
    """Point d'entrée CLI: parse les arguments puis exécute la commande choisie."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
