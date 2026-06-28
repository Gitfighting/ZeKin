"""使用高德地理编码 API 校验默认寝室/实习地址能否解析。

用法（需配置 Web 服务 Key）：
  set AMAP_WEB_KEY=你的Key
  python backend/scripts/verify_amap_geocode.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.shared.student_default_locations import (  # noqa: E402
    DEFAULT_DORMITORY_ADDRESS,
    DEFAULT_DORMITORY_LATITUDE,
    DEFAULT_DORMITORY_LONGITUDE,
    DEFAULT_INTERNSHIP_ADDRESS,
    DEFAULT_INTERNSHIP_LATITUDE,
    DEFAULT_INTERNSHIP_LONGITUDE,
)

ADDRESSES = [
    ("寝室", DEFAULT_DORMITORY_ADDRESS, DEFAULT_DORMITORY_LONGITUDE, DEFAULT_DORMITORY_LATITUDE),
    (
        "实习",
        DEFAULT_INTERNSHIP_ADDRESS,
        DEFAULT_INTERNSHIP_LONGITUDE,
        DEFAULT_INTERNSHIP_LATITUDE,
    ),
]


def geocode(address: str, key: str) -> dict | None:
    query = urllib.parse.urlencode({"key": key, "address": address, "city": "衡阳"})
    url = f"https://restapi.amap.com/v3/geocode/geo?{query}"
    with urllib.request.urlopen(url, timeout=20) as response:
        payload = json.loads(response.read())
    if payload.get("status") != "1" or not payload.get("geocodes"):
        return None
    return payload["geocodes"][0]


def main() -> None:
    key = os.environ.get("AMAP_WEB_KEY") or os.environ.get("VITE_AMAP_WEB_KEY", "").strip()
    if not key:
        print("未设置 AMAP_WEB_KEY，跳过在线校验。")
        print("默认坐标已写入 student_default_locations.py（OSM 检索结果）。")
        for label, address, lng, lat in ADDRESSES:
            print(f"  [{label}] {address}")
            print(f"         -> {lng}, {lat}")
        return

    ok = True
    for label, address, expected_lng, expected_lat in ADDRESSES:
        result = geocode(address, key)
        if result is None:
            ok = False
            print(f"[失败] {label}: 高德无法解析 — {address}")
            continue
        location = result.get("location", "")
        lng_str, lat_str = location.split(",")
        lng, lat = float(lng_str), float(lat_str)
        delta = abs(lng - expected_lng) + abs(lat - expected_lat)
        status = "通过" if delta < 0.05 else "偏差较大"
        if delta >= 0.05:
            ok = False
        print(f"[{status}] {label}")
        print(f"  地址: {address}")
        print(f"  高德: {lng}, {lat}  ({result.get('formatted_address', '')})")
        print(f"  种子: {expected_lng}, {expected_lat}")

    if not ok:
        sys.exit(1)
    print("高德地理编码校验完成。")


if __name__ == "__main__":
    main()
