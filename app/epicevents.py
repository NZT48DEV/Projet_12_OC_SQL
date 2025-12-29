from __future__ import annotations

from app.cli.parser import build_parser
from app.db.init_db import init_db


def main() -> None:
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
