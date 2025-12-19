from sqlalchemy.orm import sessionmaker

from app.db.engine import get_engine

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
)


def get_session():
    """Retourne une session SQLAlchemy liée à l'engine."""
    return SessionLocal(bind=get_engine())
