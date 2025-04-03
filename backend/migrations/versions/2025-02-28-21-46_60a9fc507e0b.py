"""Change id of embeddings to string36

Revision ID: 60a9fc507e0b
Revises: 850fa2f6bbe5
Create Date: 2025-02-28 21:46:32.616859

"""

import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "60a9fc507e0b"
down_revision = "850fa2f6bbe5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "embeddings",
        "id",
        type_=sa.String(36),
        default=lambda _: str(uuid.uuid4()),
    )


def downgrade() -> None:
    op.alter_column(
        "embeddings",
        "id",
        type_=sa.BigInteger,
        default=None,
    )
