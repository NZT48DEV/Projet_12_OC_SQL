"""add updated_at to clients

Revision ID: 330d2fa9c983
Revises: 9368e9358284
Create Date: 2026-01-08 11:11:19.503126
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "330d2fa9c983"
down_revision: Union[str, Sequence[str], None] = "9368e9358284"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ajout de updated_at (nullable pour compatibilité données existantes)
    op.add_column(
        "clients",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Harmonisation created_at avec timezone=True
    op.alter_column(
        "clients",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Retour à l'ancien type de created_at
    op.alter_column(
        "clients",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text("now()"),
    )

    # Suppression de updated_at
    op.drop_column("clients", "updated_at")
