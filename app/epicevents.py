from __future__ import annotations

from app.cli.parser import build_parser
from app.core.observability import init_sentry
from app.db.init_db import init_db


def main() -> None:
    init_db()  # charge la config + prépare la DB
    init_sentry()  # lit SENTRY_DSN depuis l'env déjà chargé

    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
