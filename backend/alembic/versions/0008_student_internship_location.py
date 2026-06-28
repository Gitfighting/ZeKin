"""Add internship location fields to student profiles

Revision ID: 0008_student_internship_location
Revises: 0007_student_dormitory_location
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_student_internship_location"
down_revision = "0007_student_dormitory_location"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "student_profiles",
        sa.Column("internship_company", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("internship_longitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("internship_latitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("internship_address", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("student_profiles", "internship_address")
    op.drop_column("student_profiles", "internship_latitude")
    op.drop_column("student_profiles", "internship_longitude")
    op.drop_column("student_profiles", "internship_company")
