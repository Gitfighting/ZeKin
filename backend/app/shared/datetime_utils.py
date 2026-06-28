from datetime import datetime
from zoneinfo import ZoneInfo

BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def get_beijing_now() -> datetime:
    return datetime.now(BEIJING_TZ)


def to_beijing_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        # SQLite 等存储会丢失时区；本项目业务时间均为北京时间
        value = value.replace(tzinfo=BEIJING_TZ)
    return value.astimezone(BEIJING_TZ).isoformat()


def as_beijing_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=BEIJING_TZ)
    return value.astimezone(BEIJING_TZ)
