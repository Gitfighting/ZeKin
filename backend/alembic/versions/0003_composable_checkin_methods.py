"""Composable checkin methods: schedule_mode, qr token, unified verification results

Revision ID: 0003_composable_checkin_methods
Revises: 0002_add_recurring_and_daily_report
Create Date: 2026-06-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_composable_checkin_methods"
down_revision = "0002_add_recurring_and_daily_report"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("checkin_tasks") as batch_op:
        batch_op.add_column(
            sa.Column("schedule_mode", sa.String(length=20), nullable=False, server_default="one_time")
        )
        batch_op.add_column(sa.Column("current_qr_token", sa.Text(), nullable=True))

    with op.batch_alter_table("checkin_records") as batch_op:
        batch_op.add_column(sa.Column("occurrence_date", sa.String(length=10), nullable=True))
        batch_op.add_column(
            sa.Column("verification_results_jsonb", sa.JSON(), nullable=True, server_default="{}")
        )
        batch_op.add_column(
            sa.Column("enabled_methods_jsonb", sa.JSON(), nullable=True, server_default="[]")
        )
    op.create_index(
        "ix_checkin_records_occurrence_date", "checkin_records", ["occurrence_date"]
    )


def downgrade() -> None:
    op.drop_index("ix_checkin_records_occurrence_date", table_name="checkin_records")
    with op.batch_alter_table("checkin_records") as batch_op:
        batch_op.drop_column("enabled_methods_jsonb")
        batch_op.drop_column("verification_results_jsonb")
        batch_op.drop_column("occurrence_date")
    with op.batch_alter_table("checkin_tasks") as batch_op:
        batch_op.drop_column("current_qr_token")
        batch_op.drop_column("schedule_mode")
