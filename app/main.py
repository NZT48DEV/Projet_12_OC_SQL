import os

import psycopg
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not found in environment variables")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, current_database();")
            user, database = cur.fetchone()

    print(f"Connected to database '{database}' as user '{user}'")


if __name__ == "__main__":
    main()
