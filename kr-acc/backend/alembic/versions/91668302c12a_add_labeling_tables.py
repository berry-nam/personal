"""Add labeling tables

Revision ID: 91668302c12a
Revises:
Create Date: 2026-03-14 03:59:44.549381
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '91668302c12a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # labeling_users
    op.create_table(
        'labeling_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='labeler', nullable=False),
        sa.Column('invite_code_used', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    # labeling_tasks
    op.create_table(
        'labeling_tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('query_id', sa.String(length=20), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('query_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('assigned_to', sa.Integer(), sa.ForeignKey('labeling_users.id'), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('query_id'),
    )

    # labeling_task_results
    op.create_table(
        'labeling_task_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('labeling_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('company_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rank_position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'company_name'),
    )

    # labeling_rubric_criteria
    op.create_table(
        'labeling_rubric_criteria',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('weight', sa.Integer(), server_default='3', nullable=False),
        sa.Column('criteria_type', sa.String(length=30), server_default='other', nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # labeling_labels
    op.create_table(
        'labeling_labels',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('labeling_tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('result_id', sa.Integer(), sa.ForeignKey('labeling_task_results.id', ondelete='CASCADE'), nullable=False),
        sa.Column('labeler_id', sa.Integer(), sa.ForeignKey('labeling_users.id'), nullable=False),
        sa.Column('overall_rating', sa.Integer(), nullable=False),
        sa.Column('rank_position', sa.Integer(), nullable=True),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'result_id', 'labeler_id'),
        sa.CheckConstraint('overall_rating >= 1 AND overall_rating <= 5', name='ck_labeling_labels_rating'),
    )

    # labeling_rubric_scores
    op.create_table(
        'labeling_rubric_scores',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('label_id', sa.Integer(), sa.ForeignKey('labeling_labels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('criterion_id', sa.Integer(), sa.ForeignKey('labeling_rubric_criteria.id'), nullable=False),
        sa.Column('score', sa.String(length=20), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label_id', 'criterion_id'),
    )


def downgrade() -> None:
    op.drop_table('labeling_rubric_scores')
    op.drop_table('labeling_labels')
    op.drop_table('labeling_rubric_criteria')
    op.drop_table('labeling_task_results')
    op.drop_table('labeling_tasks')
    op.drop_table('labeling_users')
