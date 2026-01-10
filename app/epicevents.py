from __future__ import annotations

import logging

import click
from dotenv import find_dotenv, load_dotenv

from app.cli.click_utils import Args
from app.cli.commands.auth import cmd_login, cmd_logout, cmd_refresh_token, cmd_whoami
from app.cli.commands.clients import (
    cmd_clients_create,
    cmd_clients_list,
    cmd_clients_reassign,
    cmd_clients_update,
)
from app.cli.commands.contracts import (
    cmd_contracts_create,
    cmd_contracts_list,
    cmd_contracts_reassign,
    cmd_contracts_sign,
    cmd_contracts_update,
)
from app.cli.commands.employees import (
    cmd_create_employee,
    cmd_employees_deactivate,
    cmd_employees_delete,
    cmd_employees_list,
    cmd_employees_reactivate,
)
from app.cli.commands.events import (
    cmd_events_create,
    cmd_events_list,
    cmd_events_reassign,
    cmd_events_update,
)
from app.core.observability import init_sentry
from app.db.init_db import init_db
from app.models.employee import Role

load_dotenv(find_dotenv(), override=True)
logging.basicConfig(level=logging.DEBUG)


@click.group(help="Epic Events CRM - CLI")
def cli() -> None:
    init_db()  # charge la config + prépare la DB
    init_sentry()  # lit SENTRY_DSN depuis l'env


# --------
# AUTH
# --------


@cli.command("login")
@click.argument("email")
@click.argument("password")
def login(email: str, password: str) -> None:
    cmd_login(Args(email=email, password=password))


@cli.command("logout")
def logout() -> None:
    cmd_logout(Args())


@cli.command("refresh-token")
def refresh_token() -> None:
    cmd_refresh_token(Args())


@cli.command("whoami")
def whoami() -> None:
    cmd_whoami(Args())


# -----------------
# EMPLOYEES (boot)
# -----------------


@cli.command("create-employee")
@click.argument("first_name")
@click.argument("last_name")
@click.argument("email")
@click.argument("password")
@click.argument("role", type=click.Choice([r.name for r in Role], case_sensitive=True))
def create_employee(
    first_name: str, last_name: str, email: str, password: str, role: str
) -> None:
    cmd_create_employee(
        Args(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role,
        )
    )


@cli.group("employees")
def employees() -> None:
    pass


@employees.command("list")
@click.option(
    "--role",
    type=click.Choice([r.name for r in Role], case_sensitive=True),
    default=None,
)
def employees_list(role: str | None) -> None:
    cmd_employees_list(Args(role=role))


@employees.command("deactivate")
@click.argument("employee_id", type=int)
def employees_deactivate(employee_id: int) -> None:
    cmd_employees_deactivate(Args(employee_id=employee_id))


@employees.command("reactivate")
@click.argument("employee_id", type=int)
def employees_reactivate(employee_id: int) -> None:
    cmd_employees_reactivate(Args(employee_id=employee_id))


@employees.command("delete")
@click.argument("employee_id", type=int)
@click.option("--hard", is_flag=True)
@click.option("--confirm", type=int, default=None)
def employees_delete(employee_id: int, hard: bool, confirm: int | None) -> None:
    cmd_employees_delete(Args(employee_id=employee_id, hard=hard, confirm=confirm))


# --------
# CLIENTS
# --------


@cli.group("clients")
def clients() -> None:
    pass


@clients.command("list")
def clients_list() -> None:
    cmd_clients_list(Args())


@clients.command("create")
@click.argument("first_name")
@click.argument("last_name")
@click.argument("email")
@click.option("--phone", default=None)
@click.option("--company-name", "company_name", default=None)
def clients_create(
    first_name: str,
    last_name: str,
    email: str,
    phone: str | None,
    company_name: str | None,
) -> None:
    cmd_clients_create(
        Args(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
        )
    )


@clients.command("update")
@click.argument("client_id", type=int)
@click.option("--first-name", "first_name", default=None)
@click.option("--last-name", "last_name", default=None)
@click.option("--email", "email", default=None)
@click.option("--phone", "phone", default=None)
@click.option("--company-name", "company_name", default=None)
def clients_update(
    client_id: int,
    first_name: str | None,
    last_name: str | None,
    email: str | None,
    phone: str | None,
    company_name: str | None,
) -> None:
    cmd_clients_update(
        Args(
            client_id=client_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
        )
    )


@clients.command("reassign")
@click.argument("client_id", type=int)
@click.argument("sales_contact_id", type=int)
def clients_reassign(client_id: int, sales_contact_id: int) -> None:
    cmd_clients_reassign(Args(client_id=client_id, sales_contact_id=sales_contact_id))


# ----------
# CONTRACTS
# ----------


@cli.group("contracts")
def contracts() -> None:
    pass


@contracts.command("list")
@click.option(
    "--view",
    type=click.Choice(["compact", "contact", "full"], case_sensitive=False),
    default="compact",
    show_default=True,
    help="Choix de l'affichage (colonnes).",
)
@click.option(
    "--unsigned", is_flag=True, help="Afficher uniquement les contrats non signés."
)
@click.option(
    "--unpaid",
    is_flag=True,
    help="Afficher uniquement les contrats non entièrement payés.",
)
def contracts_list(view: str, unsigned: bool, unpaid: bool) -> None:
    cmd_contracts_list(Args(view=view, unsigned=unsigned, unpaid=unpaid))


@contracts.command("create")
@click.argument("client_id", type=int)
@click.argument("total")
@click.argument("amount_due")
@click.option("--signed", is_flag=True)
def contracts_create(client_id: int, total: str, amount_due: str, signed: bool) -> None:
    cmd_contracts_create(
        Args(client_id=client_id, total=total, amount_due=amount_due, signed=signed)
    )


@contracts.command("sign")
@click.argument("contract_id", type=int)
def contracts_sign(contract_id: int) -> None:
    cmd_contracts_sign(Args(contract_id=contract_id))


@contracts.command("update")
@click.argument("contract_id", type=int)
@click.option("--total", "total_amount", default=None)
@click.option("--amount-due", "amount_due", default=None)
def contracts_update(
    contract_id: int, total_amount: str | None, amount_due: str | None
) -> None:
    cmd_contracts_update(
        Args(contract_id=contract_id, total_amount=total_amount, amount_due=amount_due)
    )


@contracts.command("reassign")
@click.argument("contract_id", type=int)
@click.argument("sales_contact_id", type=int)
def contracts_reassign(contract_id: int, sales_contact_id: int) -> None:
    cmd_contracts_reassign(
        Args(contract_id=contract_id, sales_contact_id=sales_contact_id)
    )


# ------
# EVENTS
# ------


@cli.group("events")
def events() -> None:
    pass


@events.command("list")
@click.option(
    "--view",
    type=click.Choice(["compact", "contact", "full"], case_sensitive=False),
    default="compact",
    show_default=True,
    help="Choix de l'affichage (colonnes).",
)
@click.option(
    "--without-support",
    is_flag=True,
    help="Afficher uniquement les événements sans support assigné.",
)
@click.option(
    "--assigned-to-me",
    "--mine",
    "assigned_to_me",
    is_flag=True,
    help="Afficher uniquement les événements qui me sont assignés.",
)
def events_list(view: str, without_support: bool, assigned_to_me: bool) -> None:
    cmd_events_list(
        Args(view=view, without_support=without_support, assigned_to_me=assigned_to_me)
    )


@events.command("create")
@click.argument("client_id", type=int)
@click.argument("contract_id", type=int)
@click.argument("start_date")
@click.argument("start_time")
@click.argument("end_date")
@click.argument("end_time")
@click.argument("location")
@click.argument("attendees", type=int)
@click.option("--notes", default=None)
def events_create(
    client_id: int,
    contract_id: int,
    start_date: str,
    start_time: str,
    end_date: str,
    end_time: str,
    location: str,
    attendees: int,
    notes: str | None,
) -> None:
    cmd_events_create(
        Args(
            client_id=client_id,
            contract_id=contract_id,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            location=location,
            attendees=attendees,
            notes=notes,
        )
    )


@events.command("update")
@click.argument("event_id", type=int)
@click.option("--start-date", "start_date", default=None)
@click.option("--start-time", "start_time", default=None)
@click.option("--end-date", "end_date", default=None)
@click.option("--end-time", "end_time", default=None)
@click.option("--location", default=None)
@click.option("--attendees", type=int, default=None)
@click.option("--notes", default=None)
@click.option("--support-contact-id", "support_contact_id", type=int, default=None)
def events_update(
    event_id: int,
    start_date: str | None,
    start_time: str | None,
    end_date: str | None,
    end_time: str | None,
    location: str | None,
    attendees: int | None,
    notes: str | None,
    support_contact_id: int | None,
) -> None:
    cmd_events_update(
        Args(
            event_id=event_id,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            location=location,
            attendees=attendees,
            notes=notes,
            support_contact_id=support_contact_id,
        )
    )


@events.command("reassign")
@click.argument("event_id", type=int)
@click.option("--support-contact-id", "support_contact_id", type=int, required=False)
@click.option(
    "--unassign-support",
    is_flag=True,
    help="Retire le support assigné (support_contact_id = NULL).",
)
def events_reassign(
    event_id: int, support_contact_id: int | None, unassign_support: bool
) -> None:
    cmd_events_reassign(
        Args(
            event_id=event_id,
            support_contact_id=support_contact_id,
            unassign_support=unassign_support,
        )
    )


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
