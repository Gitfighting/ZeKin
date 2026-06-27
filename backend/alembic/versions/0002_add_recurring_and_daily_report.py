"""Add is_recurring/recurrence_rule to checkin_tasks; add daily_reports table

Revision ID: 0002_add_recurring_and_daily_report
Revises: 0001_initial_schema
Create Date: 2026-06-26
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_recurring_and_daily_report"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. 给 checkin_tasks 添加循环任务字段 ──────────────────────────────
    with op.batch_alter_table("checkin_tasks") as batch_op:
        batch_op.add_column(
            sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default="false")
        )
        batch_op.add_column(
            sa.Column("recurrence_rule", sa.String(length=100), nullable=True)
        )

    # ── 2. 创建日报表 ────────────────────────────────────────────────────
    op.create_table(
        "daily_reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "student_profile_id",
            sa.Integer(),
            sa.ForeignKey("student_profiles.id"),
            nullable=False,
        ),
        sa.Column(
            "task_id",
            sa.Integer(),
            sa.ForeignKey("checkin_tasks.id"),
            nullable=True,
        ),
        sa.Column("report_date", sa.String(length=10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("work_hours", sa.Float(), nullable=True),
        sa.Column("mood", sa.String(length=20), nullable=True),
        sa.Column("photo_urls_jsonb", sa.JSON(), nullable=True, server_default="[]"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="submitted"),
        sa.Column("teacher_comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_daily_reports_student_profile_id", "daily_reports", ["student_profile_id"])
    op.create_index("ix_daily_reports_task_id", "daily_reports", ["task_id"])


def downgrade() -> None:
    op.drop_index("ix_daily_reports_task_id", table_name="daily_reports")
    op.drop_index("ix_daily_reports_student_profile_id", table_name="daily_reports")
    op.drop_table("daily_reports")
    with op.batch_alter_table("checkin_tasks") as batch_op:
        batch_op.drop_column("recurrence_rule")
        batch_op.drop_column("is_recurring")
