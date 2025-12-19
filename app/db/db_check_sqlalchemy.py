from sqlalchemy import text

from app.db.engine import get_engine

with get_engine().connect() as conn:
    value = conn.execute(text("SELECT 1")).scalar_one()

print(f"✅ Engine OK (SELECT 1 -> {value})")
