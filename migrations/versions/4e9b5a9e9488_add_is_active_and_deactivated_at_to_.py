"""add is_active and deactivated_at to employees

Revision ID: 4e9b5a9e9488
Revises: c9d16711bf82
Create Date: 2025-12-30 12:03:29.406707

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4e9b5a9e9488"
down_revision: Union[str, Sequence[str], None] = "c9d16711bf82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "employees",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "employees",
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.alter_column("employees", "is_active", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("employees", "deactivated_at")
    op.drop_column("employees", "is_active")
