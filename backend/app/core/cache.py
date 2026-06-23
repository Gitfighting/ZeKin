import json
import logging
from typing import Any

import redis

from app.core.config import get_settings


logger = logging.getLogger("app.core.cache")


class RedisCache:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
        )

    def get_json(self, key: str) -> dict[str, Any] | None:
        try:
            value = self._client.get(key)
        except redis.RedisError as exc:
            logger.warning("Redis 读取失败，已降级 key=%s error=%s", key, exc.__class__.__name__)
            return None
        if not value:
            return None
        return json.loads(value)

    def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        try:
            self._client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
        except redis.RedisError as exc:
            logger.warning("Redis 写入失败，已降级 key=%s error=%s", key, exc.__class__.__name__)


cache = RedisCache()
