"""Cấu hình chung của các dịch vụ bên ngoài (cổng, khoá API, thư mục chạy). Không import gì của hệ thống chính."""
from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))       # external_services/
RUN_DIR = os.path.join(ROOT, "run")                                       # pid, log, sqlite
HOST = "127.0.0.1"                                                        # chỉ nhận kết nối từ chính máy này

SERVICES = {
    # tên: (cổng, biến môi trường khoá API, khoá mặc định cho môi trường dev)
    "payment": (8101, "EXT_PAYMENT_KEY", "dev-payment-key"),
    "shipping": (8102, "EXT_SHIPPING_KEY", "dev-shipping-key"),
    "notify": (8103, "EXT_NOTIFY_KEY", "dev-notify-key"),
    "ai": (8104, "EXT_AI_KEY", "dev-ai-key"),
}


def port(name: str) -> int:
    return int(os.environ.get(f"EXT_{name.upper()}_PORT", SERVICES[name][0]))


def api_key(name: str) -> str:
    return os.environ.get(SERVICES[name][1], SERVICES[name][2])


def db_path(name: str) -> str:
    os.makedirs(RUN_DIR, exist_ok=True)
    return os.path.join(RUN_DIR, f"{name}.sqlite")
