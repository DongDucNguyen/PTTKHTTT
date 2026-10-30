"""Lớp HTTP dùng chung cho các gateway (module riêng tư của control.gateway; không phải một gateway).

Chế độ gateway: biến môi trường ABC_FASHION_GATEWAY_MODE = `sandbox` (mặc định, chạy trong tiến trình như cũ) hoặc `http`
(gọi các dịch vụ bên ngoài ở thư mục external_services/ qua HTTP). Mỗi dịch vụ có địa chỉ và khoá API ghi đè được:
ABC_FASHION_<PAYMENT|SHIPPING|NOTIFY|AI>_URL và ABC_FASHION_<...>_KEY. Chỉ dùng thư viện chuẩn.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
import uuid

DEFAULTS = {  # dịch vụ: (địa chỉ, khoá API dev, thời gian chờ mặc định tính bằng giây)
    "payment": ("http://127.0.0.1:8101", "dev-payment-key", 15),
    "shipping": ("http://127.0.0.1:8102", "dev-shipping-key", 15),
    "notify": ("http://127.0.0.1:8103", "dev-notify-key", 10),
    "ai": ("http://127.0.0.1:8104", "dev-ai-key", 90),         # Whisper / LLM có thể mất vài giây
}


class GatewayUnavailable(Exception):
    """Không kết nối được tới dịch vụ ngoài (mạng, quá hạn, 5xx, sai khoá API)."""


def use_http() -> bool:
    return os.environ.get("ABC_FASHION_GATEWAY_MODE", "sandbox").strip().lower() == "http"


def base_url(service: str) -> str:
    return os.environ.get(f"ABC_FASHION_{service.upper()}_URL", DEFAULTS[service][0]).rstrip("/")


def api_key(service: str) -> str:
    return os.environ.get(f"ABC_FASHION_{service.upper()}_KEY", DEFAULTS[service][1])


def timeout_of(service: str) -> float:
    env = os.environ.get("ABC_FASHION_HTTP_TIMEOUT")
    return float(env) if env else float(DEFAULTS[service][2])


def _multipart(fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode("utf-8"))
    for k, (filename, data, ctype) in files.items():
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{filename}"\r\n'
                      f"Content-Type: {ctype}\r\n\r\n").encode("utf-8") + data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def call(service: str, method: str, path: str, json_body: dict | None = None, fields: dict[str, str] | None = None,
         files: dict[str, tuple[str, bytes, str]] | None = None, headers: dict[str, str] | None = None,
         timeout: float | None = None) -> tuple[int, dict]:
    """Gọi một dịch vụ; trả `(mã HTTP, JSON)` cho mọi phản hồi 2xx / 4xx. 5xx, 401, mất kết nối → GatewayUnavailable."""
    hdrs = {"Authorization": f"Bearer {api_key(service)}", **(headers or {})}
    data = None
    if files is not None or fields is not None:
        data, hdrs["Content-Type"] = _multipart(fields or {}, files or {})
    elif json_body is not None:
        data, hdrs["Content-Type"] = json.dumps(json_body).encode("utf-8"), "application/json"
    req = urllib.request.Request(base_url(service) + path, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout or timeout_of(service)) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise GatewayUnavailable(f"Không kết nối được dịch vụ {service} ({base_url(service)}): {e}") from e
    if status >= 500 or status == 401:
        raise GatewayUnavailable(f"Dịch vụ {service} trả lỗi {status}: {raw[:200].decode('utf-8', 'replace')}")
    try:
        return status, json.loads(raw.decode("utf-8")) if raw else {}
    except ValueError as e:
        raise GatewayUnavailable(f"Dịch vụ {service} trả dữ liệu không phải JSON") from e
