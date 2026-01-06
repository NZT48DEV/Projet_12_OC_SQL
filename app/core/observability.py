import os

import sentry_sdk


def before_send(event, hint):
    # Supprimer toute info utilisateur + IP (empêche la géolocalisation serveur)
    event["user"] = {"ip_address": None}

    # Supprimer le nom de la machine
    event.pop("server_name", None)

    return event


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        release=os.getenv("SENTRY_RELEASE"),
        send_default_pii=False,
        server_name=None,
        before_send=before_send,
    )
