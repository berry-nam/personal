"""Add labeling_query_annotations table.

Revision ID: a2c7e4f1b3d5
Revises: 91668302c12a
Create Date: 2026-03-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "a2c7e4f1b3d5"
down_revision = "91668302c12a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "labeling_query_annotations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "task_id",
            sa.Integer(),
            sa.ForeignKey("labeling_tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "labeler_id",
            sa.Integer(),
            sa.ForeignKey("labeling_users.id"),
            nullable=False,
        ),
        sa.Column("scenario", sa.Text(), nullable=False),
        sa.Column(
            "explicit_conditions",
            postgresql.JSONB(),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "implicit_conditions",
            postgresql.JSONB(),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("missing_info", sa.Text(), nullable=True),
        sa.Column("clarity", sa.String(10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default="now()",
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("task_id", "labeler_id"),
    )


def downgrade() -> None:
    op.drop_table("labeling_query_annotations")
