"""Materialize recurring task occurrences

Revision ID: 0004_checkin_task_occurrences
Revises: 0003_composable_checkin_methods
Create Date: 2026-06-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_checkin_task_occurrences"
down_revision = "0003_composable_checkin_methods"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "checkin_task_occurrences",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("checkin_tasks.id"), nullable=False),
        sa.Column("occurrence_date", sa.String(length=10), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="not_started"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("task_id", "occurrence_date", name="uq_task_occurrence_date"),
    )
    op.create_index(
        "ix_checkin_task_occurrences_task_id", "checkin_task_occurrences", ["task_id"]
    )
    op.create_index(
        "ix_checkin_task_occurrences_occurrence_date",
        "checkin_task_occurrences",
        ["occurrence_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_checkin_task_occurrences_occurrence_date", table_name="checkin_task_occurrences"
    )
    op.drop_index(
        "ix_checkin_task_occurrences_task_id", table_name="checkin_task_occurrences"
    )
    op.drop_table("checkin_task_occurrences")
