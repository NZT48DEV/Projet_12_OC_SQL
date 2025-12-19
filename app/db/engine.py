from sqlalchemy import create_engine

from app.db.config import DATABASE_URL

_engine = None


def get_engine():
    """Retourne l'engine SQLAlchemy, initialisé à la demande."""
    global _engine

    if _engine is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL non défini")

        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
        )

    return _engine
