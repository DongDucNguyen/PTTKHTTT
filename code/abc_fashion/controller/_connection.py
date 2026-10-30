"""Cấu hình kết nối / dịch vụ ngoài cho ứng dụng nhúng controller (module riêng tư của controller layer).

Ứng dụng web không được import control layer, nên các nút bật cần thiết được đưa ra đây:
- use_connection_per_thread / release_connection: mỗi luồng request một kết nối CSDL, đóng ở cuối request.
- external_services_enabled: đang ở chế độ http (dịch vụ ngân hàng / vận chuyển / AI thật) hay sandbox.
"""
from __future__ import annotations

from abc_fashion.control.dao.dao import DAO
from abc_fashion.control.gateway import _http


def use_connection_per_thread() -> None:
    DAO._per_thread = True


def release_connection() -> None:
    DAO._release_thread_connection()


def external_services_enabled() -> bool:
    return _http.use_http()
