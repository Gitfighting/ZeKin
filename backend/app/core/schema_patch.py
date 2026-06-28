"""SQLite 兼容：为旧库补齐 student_profiles 位置字段（无 alembic.ini 时 create_all 不会 ALTER）。"""
from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

LOCATION_COLUMNS: tuple[tuple[str, str], ...] = (
    ("dormitory_longitude", "FLOAT"),
    ("dormitory_latitude", "FLOAT"),
    ("dormitory_address", "VARCHAR(255)"),
    ("internship_company", "VARCHAR(255)"),
    ("internship_longitude", "FLOAT"),
    ("internship_latitude", "FLOAT"),
    ("internship_address", "VARCHAR(255)"),
)


def ensure_student_location_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    if "student_profiles" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("student_profiles")}
    pending = [(name, sql_type) for name, sql_type in LOCATION_COLUMNS if name not in existing]
    if not pending:
        return

    with engine.begin() as connection:
        for name, sql_type in pending:
            connection.execute(
                text(f"ALTER TABLE student_profiles ADD COLUMN {name} {sql_type}")
            )
