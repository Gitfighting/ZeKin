"""二维码签到 token 服务：HMAC 签名 + 过期校验。

二维码内容为一段 base64url(JSON).signature 字符串：
    payload = {"task_id", "occurrence_date", "nonce", "expires_at"}
    token   = base64url(json(payload)) + "." + hmac_sha256(secret, base64url_payload)

教师端生成 token 渲染为二维码图片；学生扫码后把 token 原样回传，
后端 verify_token 校验签名与有效期。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass

from app.core.config import get_settings


@dataclass(slots=True)
class QrToken:
    task_id: int
    occurrence_date: str | None
    nonce: str
    expires_at: int


class QrTokenError(Exception):
    pass


def _secret() -> bytes:
    return get_settings().jwt_secret_key.encode("utf-8")


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(payload_b64: str) -> str:
    digest = hmac.new(_secret(), payload_b64.encode("ascii"), hashlib.sha256).digest()
    return _b64encode(digest)


def generate_token(
    task_id: int,
    *,
    occurrence_date: str | None = None,
    expire_seconds: int = 120,
) -> tuple[str, QrToken]:
    """生成一个新的二维码 token。"""
    expires_at = int(time.time()) + max(1, expire_seconds)
    token_obj = QrToken(
        task_id=task_id,
        occurrence_date=occurrence_date,
        nonce=secrets.token_urlsafe(8),
        expires_at=expires_at,
    )
    payload = {
        "task_id": token_obj.task_id,
        "occurrence_date": token_obj.occurrence_date,
        "nonce": token_obj.nonce,
        "expires_at": token_obj.expires_at,
    }
    payload_b64 = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    token = f"{payload_b64}.{_sign(payload_b64)}"
    return token, token_obj


def render_qr_data_url(token: str) -> str:
    """将 token 渲染为二维码 PNG，并返回 data URL（供教师端投屏展示）。"""
    try:
        import qrcode
    except ImportError:
        return ""

    from io import BytesIO

    img = qrcode.make(token)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def verify_token(token: str, *, expected_task_id: int | None = None) -> QrToken:
    """校验 token 签名与有效期，返回解析后的 QrToken；失败抛 QrTokenError。"""
    if not token or "." not in token:
        raise QrTokenError("二维码内容无效")

    payload_b64, signature = token.rsplit(".", 1)
    if not hmac.compare_digest(signature, _sign(payload_b64)):
        raise QrTokenError("二维码签名校验失败")

    try:
        payload = json.loads(_b64decode(payload_b64))
    except (ValueError, json.JSONDecodeError) as exc:
        raise QrTokenError("二维码内容解析失败") from exc

    token_obj = QrToken(
        task_id=int(payload.get("task_id", 0)),
        occurrence_date=payload.get("occurrence_date"),
        nonce=str(payload.get("nonce", "")),
        expires_at=int(payload.get("expires_at", 0)),
    )

    if token_obj.expires_at < int(time.time()):
        raise QrTokenError("二维码已过期，请扫描最新二维码")

    if expected_task_id is not None and token_obj.task_id != expected_task_id:
        raise QrTokenError("二维码与当前任务不匹配")

    return token_obj
