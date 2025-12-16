from sqlalchemy import text

from app.db.engine import engine

with engine.connect() as conn:
    value = conn.execute(text("SELECT 1")).scalar_one()

print(f"✅ Engine OK (SELECT 1 -> {value})")
