"""Add manual attendance override columns to checkin_records

Revision ID: 0005_manual_attendance
Revises: 0004_checkin_task_occurrences
Create Date: 2026-06-27
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_manual_attendance"
down_revision = "0004_checkin_task_occurrences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "checkin_records",
        sa.Column("manual_status", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "checkin_records",
        sa.Column("manual_remark", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("checkin_records", "manual_remark")
    op.drop_column("checkin_records", "manual_status")
