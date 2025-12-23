"""set default for clients created_at

Revision ID: c9d16711bf82
Revises: a02d68703108
Create Date: 2025-12-23 11:45:46.774143

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9d16711bf82"
down_revision: Union[str, Sequence[str], None] = "a02d68703108"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("clients", "created_at", server_default=sa.text("NOW()"))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("clients", "created_at", server_default=None)
