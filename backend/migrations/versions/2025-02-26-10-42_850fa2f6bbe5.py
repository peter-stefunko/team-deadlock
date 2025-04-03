"""empty message

Revision ID: 850fa2f6bbe5
Revises:
Create Date: 2025-02-26 10:42:56.829378

"""

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "850fa2f6bbe5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "articles",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("classification", sa.String(), nullable=True),
        sa.Column("credibility", sa.String(), nullable=True),
        sa.Column("abstract", sa.String(), nullable=True),
        sa.Column("publisher", sa.String(), nullable=True),
        sa.Column("publication_id", sa.BigInteger(), nullable=True),
        sa.Column("source_id", sa.BigInteger(), nullable=True),
        sa.Column("published_at", sa.String(), nullable=True),
        sa.Column("scanned_at", sa.String(), nullable=True),
        sa.Column("text", sa.String(), nullable=True),
        sa.Column("trust_factor", sa.Float(), nullable=False),
    )

    op.create_table(
        "embeddings",
        sa.Column(
            "id", sa.BigInteger(), primary_key=True, autoincrement=True
        ),
        sa.Column(
            "article_id",
            sa.BigInteger(),
            sa.ForeignKey("articles.id"),
            nullable=False,
        ),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("embeddings")
    op.drop_table("articles")
    op.execute("DROP EXTENSION IF EXISTS vector;")
