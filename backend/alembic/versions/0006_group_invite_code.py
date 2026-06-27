"""Add invite_code to groups

Revision ID: 0006_group_invite_code
Revises: 0005_manual_attendance
Create Date: 2026-06-27
"""

import secrets
import string

from alembic import op
import sqlalchemy as sa

revision = "0006_group_invite_code"
down_revision = "0005_manual_attendance"
branch_labels = None
depends_on = None


def _generate_code(used: set[str]) -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if code not in used:
            used.add(code)
            return code


def upgrade() -> None:
    op.add_column(
        "groups",
        sa.Column("invite_code", sa.String(length=8), nullable=True),
    )

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id FROM groups ORDER BY id")).fetchall()
    used: set[str] = set()
    for (group_id,) in rows:
        code = _generate_code(used)
        connection.execute(
            sa.text("UPDATE groups SET invite_code = :code WHERE id = :id"),
            {"code": code, "id": group_id},
        )

    op.alter_column("groups", "invite_code", nullable=False)
    op.create_unique_constraint("uq_groups_invite_code", "groups", ["invite_code"])


def downgrade() -> None:
    op.drop_constraint("uq_groups_invite_code", "groups", type_="unique")
    op.drop_column("groups", "invite_code")
