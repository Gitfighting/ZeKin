"""Add scheduled_publish_at to checkin_tasks

Revision ID: 0009_scheduled_publish_at
Revises: 0008_student_internship_location
Create Date: 2026-06-29
"""

from alembic import op
import sqlalchemy as sa

revision = "0009_scheduled_publish_at"
down_revision = "0008_student_internship_location"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "checkin_tasks",
        sa.Column("scheduled_publish_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("checkin_tasks", "scheduled_publish_at")
