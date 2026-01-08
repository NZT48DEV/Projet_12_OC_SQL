"""add updated_at to events

Revision ID: f9771b18721d
Revises: cfa483117a3d
Create Date: 2026-01-08 14:53:41.875487
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f9771b18721d"
down_revision: Union[str, Sequence[str], None] = "cfa483117a3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Ajout de la colonne (nullable au départ)
    op.add_column(
        "events",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # 2) Backfill : updated_at = created_at (ou NOW() si created_at est NULL)
    op.execute(
        """
        UPDATE events
        SET updated_at = COALESCE(created_at, NOW())
        """
    )

    # 3) On rend la colonne non-nullable
    op.alter_column("events", "updated_at", nullable=False)


def downgrade() -> None:
    op.drop_column("events", "updated_at")
