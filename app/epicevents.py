from __future__ import annotations

import argparse

from app.core.authorization import AuthorizationError, require_role
from app.core.jwt_service import TokenError, create_token_pair, refresh_access_token
from app.core.security import hash_password
from app.core.token_store import clear_tokens, load_refresh_token, save_tokens
from app.db.init_db import init_db
from app.db.session import get_session
from app.models.employee import Employee, Role
from app.services.auth_service import AuthenticationError, authenticate_employee
from app.services.client_service import list_clients
from app.services.contract_service import list_contracts
from app.services.current_employee import NotAuthenticatedError, get_current_employee
from app.services.event_service import list_events

# -------------------------
# Commandes CLI
# -------------------------


def cmd_login(args: argparse.Namespace) -> None:
    """Authentifie un employé et stocke les tokens JWT localement."""
    session = get_session()
    try:
        employee = authenticate_employee(session, args.email, args.password)

        token_pair = create_token_pair(
            employee_id=employee.id,
            access_minutes=20,
            refresh_days=7,
        )
        save_tokens(token_pair.access_token, token_pair.refresh_token)

        print(
            f"✅ Connecté : {employee.first_name} {employee.last_name} "
            f"(role={employee.role})"
        )
        print("ℹ️  Access token valide 20 minutes.")
        print("ℹ️  Utilise `refresh-token` si le token expire.")
    except AuthenticationError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()


def cmd_logout(_: argparse.Namespace) -> None:
    """Supprime les tokens locaux (déconnexion)."""
    clear_tokens()
    print("✅ Déconnecté.")


def cmd_refresh_token(_: argparse.Namespace) -> None:
    """Régénère un access token via le refresh token local."""
    refresh_token = load_refresh_token()
    if not refresh_token:
        print("❌ Aucun refresh token trouvé. Faites `login`.")
        return

    try:
        token_pair = refresh_access_token(
            refresh_token=refresh_token,
            access_minutes=20,
            rotate_refresh=True,
        )
        save_tokens(token_pair.access_token, token_pair.refresh_token)
        print("✅ Token rafraîchi avec succès.")
    except TokenError as exc:
        print(f"❌ Impossible de rafraîchir le token : {exc}")
        print("➡️ Faites `login`.")


def cmd_whoami(_: argparse.Namespace) -> None:
    """Affiche l'utilisateur actuellement authentifié (via access token)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        print(
            f"👤 {employee.first_name} {employee.last_name} "
            f"(email={employee.email}, role={employee.role})"
        )
    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    finally:
        session.close()


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


def cmd_clients_list(_: argparse.Namespace) -> None:
    """Liste tous les clients (lecture seule, authentification requise)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        clients = list_clients(session=session, current_employee=employee)

        if not clients:
            print("ℹ️  Aucun client trouvé.")
            return

        print("📋 Clients :")
        for c in clients:
            # Adapte les champs si ton modèle Client diffère
            print(
                f"- id={c.id} | {c.first_name} | {c.last_name} | {c.email} | "
                f"company={c.company_name} | sales_contact_id={c.sales_contact_id}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la récupération des clients : {exc}")

    finally:
        session.close()


def cmd_contracts_list(_: argparse.Namespace) -> None:
    """Liste tous les contrats (lecture seule, authentification requise)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        contracts = list_contracts(session=session, current_employee=employee)

        if not contracts:
            print("ℹ️  Aucun contrat trouvé.")
            return

        print("📋 Contrats :")
        for ct in contracts:
            contract_id = ct.id
            client_id = ct.client_id
            sales_contact_id = ct.sales_contact_id
            total_amount = ct.total_amount
            amount_due = ct.amount_due
            is_signed = ct.is_signed
            created_at = ct.created_at

            print(
                f"- id={contract_id} | "
                f"client_id={client_id} | "
                f"sales_contact_id={sales_contact_id} | "
                f"total={total_amount} | "
                f"due={amount_due} | "
                f"signed={is_signed} | "
                f"created_at={created_at}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la récupération des contrats : {exc}")
    finally:
        session.close()


def cmd_events_list(_: argparse.Namespace) -> None:
    """Liste tous les événements (lecture seule, authentification requise)."""
    session = get_session()
    try:
        employee = get_current_employee(session)
        events = list_events(session=session, current_employee=employee)

        if not events:
            print("ℹ️  Aucun événement trouvé.")
            return

        print("📋 Événements :")
        for ev in events:
            event_id = ev.id
            contract_id = ev.contract_id
            client_id = ev.client_id
            support_contact_id = ev.support_contact_id
            start_date = ev.start_date
            end_date = ev.end_date
            location = ev.location
            attendees = ev.attendees
            notes = ev.notes
            created_at = ev.created_at

            start_str = start_date.strftime("%Y-%m-%d %H:%M")
            end_str = end_date.strftime("%Y-%m-%d %H:%M")
            created_str = created_at.strftime("%Y-%m-%d %H:%M")

            print(
                f"- id={event_id} | "
                f"contract_id={contract_id} | "
                f"client_id={client_id} | "
                f"support_contact_id={support_contact_id} | "
                f"start={start_str} | "
                f"end={end_str} | "
                f"location={location} | "
                f"attendees={attendees} | "
                f"notes={notes} | "
                f"created_at={created_str}"
            )

    except NotAuthenticatedError as exc:
        print(f"❌ {exc}")
    except Exception as exc:
        session.rollback()
        print(f"❌ Erreur lors de la récupération des événements : {exc}")
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


# -------------------------
# Parser CLI
# -------------------------


def build_parser() -> argparse.ArgumentParser:
    """Construit le parser des commandes CLI."""
    parser = argparse.ArgumentParser(
        prog="epicevents",
        description="Epic Events CRM - CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # login
    p_login = subparsers.add_parser("login", help="Se connecter")
    p_login.add_argument("email")
    p_login.add_argument("password")
    p_login.set_defaults(func=cmd_login)

    # logout
    p_logout = subparsers.add_parser("logout", help="Se déconnecter")
    p_logout.set_defaults(func=cmd_logout)

    # refresh-token
    p_refresh = subparsers.add_parser(
        "refresh-token",
        help="Régénérer un access token via le refresh token",
    )
    p_refresh.set_defaults(func=cmd_refresh_token)

    # whoami
    p_whoami = subparsers.add_parser(
        "whoami",
        help="Afficher l'utilisateur courant",
    )
    p_whoami.set_defaults(func=cmd_whoami)

    # management-only
    p_management = subparsers.add_parser(
        "management-only",
        help="Commande réservée au rôle MANAGEMENT",
    )
    p_management.set_defaults(func=cmd_management_only)

    # create-employee (positionnels)
    p_create = subparsers.add_parser(
        "create-employee",
        help="Créer un employé (bootstrap du premier MANAGEMENT autorisé)",
    )
    p_create.add_argument("first_name")
    p_create.add_argument("last_name")
    p_create.add_argument("email")
    p_create.add_argument("password")
    p_create.add_argument("role", choices=[r.name for r in Role])
    p_create.set_defaults(func=cmd_create_employee)

    # clients
    p_clients = subparsers.add_parser("clients", help="Gestion des clients")
    clients_sub = p_clients.add_subparsers(dest="clients_command", required=True)

    p_clients_list = clients_sub.add_parser("list", help="Lister tous les clients")
    p_clients_list.set_defaults(func=cmd_clients_list)

    # contracts
    p_contracts = subparsers.add_parser("contracts", help="Gestion des contrats")
    contracts_sub = p_contracts.add_subparsers(dest="contracts_command", required=True)

    p_contracts_list = contracts_sub.add_parser("list", help="Lister tous les contrats")
    p_contracts_list.set_defaults(func=cmd_contracts_list)

    # events
    p_events = subparsers.add_parser("events", help="Gestion des événements")
    events_sub = p_events.add_subparsers(dest="events_command", required=True)

    p_events_list = events_sub.add_parser("list", help="Lister tous les événements")
    p_events_list.set_defaults(func=cmd_events_list)

    return parser


# -------------------------
# Point d'entrée
# -------------------------


def main() -> None:
    """Point d'entrée de la CLI."""
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
