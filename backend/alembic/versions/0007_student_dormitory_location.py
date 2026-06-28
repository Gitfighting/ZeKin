"""Add dormitory location fields to student profiles

Revision ID: 0007_student_dormitory_location
Revises: 0006_group_invite_code
Create Date: 2026-06-28
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_student_dormitory_location"
down_revision = "0006_group_invite_code"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "student_profiles",
        sa.Column("dormitory_longitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("dormitory_latitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("dormitory_address", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("student_profiles", "dormitory_address")
    op.drop_column("student_profiles", "dormitory_latitude")
    op.drop_column("student_profiles", "dormitory_longitude")
