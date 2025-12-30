"""add reactivated_at to employees

Revision ID: 9368e9358284
Revises: 4e9b5a9e9488
Create Date: 2025-12-30 13:25:08.824874

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9368e9358284"
down_revision: Union[str, Sequence[str], None] = "4e9b5a9e9488"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "employees",
        sa.Column("reactivated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("employees", "reactivated_at")
