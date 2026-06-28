from datetime import datetime
from zoneinfo import ZoneInfo

from app.shared.datetime_utils import get_beijing_now, to_beijing_iso


def test_to_beijing_iso_from_utc():
    utc = datetime(2026, 6, 26, 23, 42, tzinfo=ZoneInfo("UTC"))
    assert to_beijing_iso(utc) == "2026-06-27T07:42:00+08:00"


def test_to_beijing_iso_from_naive_assumes_beijing():
    naive = datetime(2026, 6, 27, 14, 15)
    assert to_beijing_iso(naive) == "2026-06-27T14:15:00+08:00"


def test_get_beijing_now_has_shanghai_tz():
    now = get_beijing_now()
    assert now.tzinfo == ZoneInfo("Asia/Shanghai")
