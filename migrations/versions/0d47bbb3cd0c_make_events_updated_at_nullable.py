"""make events.updated_at nullable

Revision ID: xxxxxxxxxxxx
Revises: f9771b18721d
Create Date: 2026-01-08 xx:xx:xx.xxxxxx
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0d47bbb3cd0c"
down_revision: Union[str, Sequence[str], None] = "f9771b18721d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "events",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "events",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
