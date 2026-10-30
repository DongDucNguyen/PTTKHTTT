"""Lưu / tìm file media (ảnh sản phẩm, bằng chứng trả hàng) — module riêng tư của controller layer.

CSDL lưu đường dẫn tương đối dạng `media/<thư mục>/<tên>`; file nằm dưới thư mục `code/`.
"""
from __future__ import annotations

import os
import uuid

CODE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEDIA_DIR = os.path.join(CODE_DIR, "media")


def media_path(url: str | None) -> str | None:
    """Đường dẫn tuyệt đối của file media; `None` với URL ngoài (CDN) hoặc rỗng."""
    if not url or "://" in url:
        return None
    return url if os.path.isabs(url) else os.path.join(CODE_DIR, url)


def save_media(file_name: str, data: bytes, subdir: str) -> str:
    """Ghi `data` thành file mới trong `media/<subdir>/` (giữ phần mở rộng của `file_name`); trả đường dẫn tương đối."""
    ext = os.path.splitext(file_name)[1].lower()
    rel = os.path.join("media", subdir, uuid.uuid4().hex[:12] + ext).replace("\\", "/")
    os.makedirs(os.path.dirname(media_path(rel)), exist_ok=True)
    with open(media_path(rel), "wb") as fh:
        fh.write(data)
    return rel


def delete_media_file(url: str | None, subdir: str) -> None:
    """Xoá file do ứng dụng tự lưu trong `media/<subdir>/` (không đụng file ngoài thư mục đó)."""
    if url and url.startswith(f"media/{subdir}/"):
        try:
            os.remove(media_path(url))
        except OSError:
            pass
