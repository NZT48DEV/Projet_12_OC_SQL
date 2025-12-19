from app.db.base import Base
from app.db.engine import get_engine


def init_db():
    """Initialise la base de données (création des tables)."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
