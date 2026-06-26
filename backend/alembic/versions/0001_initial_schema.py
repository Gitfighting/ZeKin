"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-24
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account", sa.String(length=64), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("user_type", sa.String(length=20), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("wechat_openid", sa.String(length=128), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("account"),
        sa.UniqueConstraint("phone"),
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("org_type", sa.String(length=50), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("student_no", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("college", sa.String(length=100), nullable=False),
        sa.Column("major", sa.String(length=100), nullable=False),
        sa.Column("grade", sa.String(length=20), nullable=False),
        sa.Column("class_name", sa.String(length=100), nullable=False),
        sa.Column("dormitory", sa.String(length=100), nullable=False),
        sa.Column("activated", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="imported"),
        *_timestamps(),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("student_no"),
        sa.UniqueConstraint("phone"),
    )
    op.create_table(
        "teacher_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("teacher_no", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("department", sa.String(length=100), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("user_id"),
        sa.UniqueConstraint("teacher_no"),
    )
    op.create_table(
        "admin_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("scope", sa.String(length=100), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("group_type", sa.String(length=50), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "group_members",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("student_profile_id", sa.Integer(), sa.ForeignKey("student_profiles.id"), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("group_id", "student_profile_id"),
    )
    op.create_table(
        "group_teachers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("teacher_profile_id", sa.Integer(), sa.ForeignKey("teacher_profiles.id"), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("group_id", "teacher_profile_id"),
    )
    op.create_table(
        "checkin_types",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "rule_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type_id", sa.Integer(), sa.ForeignKey("checkin_types.id"), nullable=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rules_jsonb", sa.JSON(), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "checkin_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type_id", sa.Integer(), sa.ForeignKey("checkin_types.id"), nullable=False),
        sa.Column("teacher_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("rules_snapshot_jsonb", sa.JSON(), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "face_encodings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_profile_id", sa.Integer(), sa.ForeignKey("student_profiles.id"), nullable=False),
        sa.Column("encoding", sa.LargeBinary(), nullable=False),
        sa.Column("dimension", sa.Integer(), nullable=False, server_default="128"),
        sa.Column("model_name", sa.String(length=64), nullable=False, server_default="face_recognition"),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="admin_upload"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("quality_jsonb", sa.JSON(), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "checkin_task_groups",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("checkin_tasks.id"), nullable=False),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("task_id", "group_id"),
    )
    op.create_table(
        "checkin_task_students",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("checkin_tasks.id"), nullable=False),
        sa.Column("student_profile_id", sa.Integer(), sa.ForeignKey("student_profiles.id"), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("task_id", "student_profile_id"),
    )
    op.create_table(
        "checkin_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("checkin_tasks.id"), nullable=False),
        sa.Column("student_profile_id", sa.Integer(), sa.ForeignKey("student_profiles.id"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("location_result_jsonb", sa.JSON(), nullable=False),
        sa.Column("dynamic_code_result_jsonb", sa.JSON(), nullable=False),
        sa.Column("face_result_jsonb", sa.JSON(), nullable=False),
        sa.Column("submit_payload_jsonb", sa.JSON(), nullable=False),
        sa.Column("evaluation_messages_jsonb", sa.JSON(), nullable=False),
        sa.Column("need_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamps(),
    )
    op.create_table(
        "checkin_record_attachments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("record_id", sa.Integer(), sa.ForeignKey("checkin_records.id"), nullable=False),
        sa.Column("file_path", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "checkin_exceptions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("record_id", sa.Integer(), sa.ForeignKey("checkin_records.id"), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("checkin_tasks.id"), nullable=False),
        sa.Column("student_profile_id", sa.Integer(), sa.ForeignKey("student_profiles.id"), nullable=False),
        sa.Column("exception_types_jsonb", sa.JSON(), nullable=False),
        sa.Column("messages_jsonb", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "appeals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("record_id", sa.Integer(), sa.ForeignKey("checkin_records.id"), nullable=False),
        sa.Column("student_profile_id", sa.Integer(), sa.ForeignKey("student_profiles.id"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("attachment_ids_jsonb", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "review_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("record_id", sa.Integer(), sa.ForeignKey("checkin_records.id"), nullable=False),
        sa.Column("reviewer_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("read_status", sa.String(length=20), nullable=False),
        *_timestamps(),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        *_timestamps(),
    )


def downgrade() -> None:
    for table_name in [
        "audit_logs",
        "messages",
        "review_logs",
        "appeals",
        "checkin_exceptions",
        "checkin_record_attachments",
        "checkin_records",
        "checkin_task_students",
        "checkin_task_groups",
        "face_encodings",
        "checkin_tasks",
        "rule_templates",
        "checkin_types",
        "group_teachers",
        "group_members",
        "groups",
        "admin_profiles",
        "teacher_profiles",
        "student_profiles",
        "organizations",
        "users",
    ]:
        op.drop_table(table_name)
