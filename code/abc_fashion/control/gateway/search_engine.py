"""SearchEngine — AI Model Service (CLIP cho ảnh, Whisper cho giọng nói).

Chế độ `http` (ABC_FASHION_GATEWAY_MODE=http): gọi dịch vụ AI THẬT (external_services/ai_service, cổng 8104) — CLIP
mã hoá ảnh, Whisper nhận dạng giọng nói. Chế độ `sandbox` (mặc định): bản giả lập dưới đây.

Sandbox dùng một "chỉ mục vector" đơn giản ở `media/search_index.json` (do `db/setup_db.py --index` sinh từ
dữ liệu sản phẩm): mỗi style có màu trung bình của ảnh và các từ khoá. Gateway không truy cập CSDL.
"""
from __future__ import annotations

import io
import json
import math
import os
import unicodedata

from abc_fashion.control.gateway import _http

_CODE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
INDEX_PATH = os.environ.get("ABC_FASHION_SEARCH_INDEX", os.path.join(_CODE_DIR, "media", "search_index.json"))
MAX_RESULTS = 20


def _fold(text: str) -> str:
    """Chữ thường, bỏ dấu tiếng Việt."""
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


class SearchEngine:
    """Dùng bởi: SearchStyleFrm."""

    def search_by_image(self, image: bytes) -> list[int]:
        """Mã hoá ảnh, tìm style gần nhất; trả id style theo độ phù hợp giảm dần."""
        if _http.use_http():
            return self._remote("/v1/search/image", "query-image", image)
        from PIL import Image                       # Pillow chỉ cần khi tìm bằng ảnh

        index = self._load_index()
        with Image.open(io.BytesIO(image)) as im:               # màu trung bình = thu về 1×1 bằng bộ lọc BOX
            query = list(im.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0)))
        scored = []
        for entry in index:
            colours = entry.get("colours") or []
            if colours:
                scored.append((min(math.dist(query, c) for c in colours), entry["id"]))
        scored.sort()
        return [sid for _, sid in scored[:MAX_RESULTS]]

    def search_by_voice(self, audio: bytes) -> list[int]:
        """Chuyển giọng nói thành văn bản rồi tìm như văn bản.

        Sandbox chưa có Whisper: chấp nhận file bản ghi (.txt UTF-8) làm "kết quả nhận dạng".
        """
        if _http.use_http():
            return self._remote("/v1/search/voice", "query-audio", audio)
        try:
            transcript = audio.decode("utf-8")
        except UnicodeDecodeError:
            raise RuntimeError("Dịch vụ nhận dạng giọng nói (Whisper) chưa sẵn sàng trong sandbox") from None
        words = [w for w in _fold(transcript).split() if len(w) > 1]
        if not words:
            return []
        scored = []
        for entry in self._load_index():
            keywords = _fold(" ".join(entry.get("keywords", [])))
            hits = sum(1 for w in words if w in keywords)
            if hits:
                scored.append((-hits, entry["id"]))
        scored.sort()
        return [sid for _, sid in scored[:MAX_RESULTS]]

    @staticmethod
    def _remote(path: str, filename: str, data: bytes) -> list[int]:
        status, body = _http.call("ai", "POST", path, files={"file": (filename, data, "application/octet-stream")})
        if status != 200:
            raise RuntimeError(body.get("error", {}).get("message", f"Dịch vụ AI trả lỗi {status}"))
        return [int(i) for i in body["ids"]][:MAX_RESULTS]

    def _push_index(self, entries: list[dict]) -> dict:
        """Đẩy danh mục sản phẩm lên dịch vụ AI (gọi khi khởi động ở chế độ http). `entries`: id, code, name, brand,
        description, category, colours và `image_path` (đường dẫn file ảnh cục bộ hoặc None)."""
        files, meta = {}, []
        for e in entries:
            item = {k: v for k, v in e.items() if k != "image_path"}
            path = e.get("image_path")
            if path and os.path.exists(path):
                with open(path, "rb") as fh:
                    files[f"image_{e['id']}"] = (os.path.basename(path), fh.read(), "image/jpeg")
                item["image"] = f"image_{e['id']}"
            meta.append(item)
        status, body = _http.call("ai", "PUT", "/v1/search/index", fields={"meta": json.dumps(meta, ensure_ascii=False)},
                                  files=files)
        if status != 200:
            raise RuntimeError(body.get("error", {}).get("message", f"Đẩy chỉ mục lỗi {status}"))
        return body

    def _load_index(self) -> list[dict]:
        if not os.path.exists(INDEX_PATH):
            raise RuntimeError("Chưa có chỉ mục tìm kiếm (chạy: python db/setup_db.py --index)")
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
