"""Chỉ mục sản phẩm cho tìm kiếm: vector CLIP của ảnh và của mô tả chữ, lưu bền trên đĩa."""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading

import numpy as np

from common import config

DIR = os.path.join(config.RUN_DIR, "ai_index")
MIN_TEXT_COSINE = 0.24
_lock = threading.RLock()
_state: dict = {"meta": [], "img": None, "has_img": None, "txt": None, "etag": ""}


def _tokens(text: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-zA-ZÀ-ỹ0-9]+", (text or "").lower()):
        out.add(w)
        if len(w) > 3 and w.endswith("s"):                  # số nhiều tiếng Anh đơn giản
            out.add(w[:-1])
    return out


def doc_text(item: dict) -> str:
    """Chuỗi mô tả một style cho CLIP (tiếng Anh) — tên, danh mục, thương hiệu, màu."""
    return ", ".join(p for p in (item.get("name"), item.get("category"), item.get("brand"), " ".join(item.get("colours", []))) if p)


def etag_of(meta: list[dict], images: dict[str, bytes]) -> str:
    h = hashlib.sha256(json.dumps(meta, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for k in sorted(images):
        h.update(k.encode()); h.update(hashlib.sha256(images[k]).digest())
    return h.hexdigest()[:16]


def count() -> int:
    return len(_state["meta"])


def etag() -> str:
    return _state["etag"]


def build(meta: list[dict], images: dict[str, bytes], models) -> dict:
    """Tính vector cho toàn bộ danh mục và lưu xuống đĩa. Trả `{status, count, etag}`."""
    tag = etag_of(meta, images)
    with _lock:
        if tag == _state["etag"] and meta:
            return {"status": "unchanged", "count": len(meta), "etag": tag}
        txt = models.embed_texts([doc_text(m) for m in meta]) if meta else np.zeros((0, 512), dtype=np.float32)
        img = np.zeros((len(meta), txt.shape[1] if len(meta) else 512), dtype=np.float32)
        has = np.zeros(len(meta), dtype=bool)
        keyed = [(i, images[m["image"]]) for i, m in enumerate(meta) if m.get("image") in images]
        if keyed:
            vec = models.embed_images([b for _, b in keyed])
            for (i, _), v in zip(keyed, vec):
                img[i], has[i] = v, True
        _state.update(meta=meta, img=img, has_img=has, txt=txt, etag=tag)
        os.makedirs(DIR, exist_ok=True)
        np.savez(os.path.join(DIR, "vectors.npz"), img=img, has=has, txt=txt)
        with open(os.path.join(DIR, "meta.json"), "w", encoding="utf-8") as f:
            json.dump({"etag": tag, "meta": meta}, f, ensure_ascii=False)
    return {"status": "updated", "count": len(meta), "etag": tag, "with_images": int(has.sum())}


def load() -> None:
    try:
        data = np.load(os.path.join(DIR, "vectors.npz"))
        with open(os.path.join(DIR, "meta.json"), encoding="utf-8") as f:
            info = json.load(f)
        _state.update(meta=info["meta"], img=data["img"], has_img=data["has"], txt=data["txt"], etag=info["etag"])
    except (OSError, ValueError, KeyError):
        pass


def rank_by_image(query_vec: np.ndarray, limit: int = 20) -> list[tuple[int, float]]:
    """Xếp hạng theo độ giống ảnh (cosine, chính) và mô tả chữ (phụ, 15%). Trả [(id style, điểm)] giảm dần."""
    with _lock:
        meta, img, has, txt = _state["meta"], _state["img"], _state["has_img"], _state["txt"]
        if not meta:
            return []
        s_img = np.where(has, img @ query_vec, 0.0)
        s_txt = txt @ query_vec
        score = np.where(has, 0.85 * s_img + 0.15 * s_txt, s_txt)
        order = np.argsort(-score)[:limit]
        return [(int(meta[i]["id"]), float(score[i])) for i in order]


def rank_by_text(text_vec: np.ndarray, query_text: str, limit: int = 20) -> list[tuple[int, float]]:
    """Xếp hạng theo CLIP chữ↔ảnh (softmax, 60%) và trùng từ khoá với tên / mô tả / màu (40%)."""
    with _lock:
        meta, img, has, txt = _state["meta"], _state["img"], _state["has_img"], _state["txt"]
        if not meta:
            return []
        cos = np.where(has, img @ text_vec, txt @ text_vec)
        logits = 100.0 * cos
        prob = np.exp(logits - logits.max()); prob /= prob.sum()
        q = _tokens(query_text)
        out = []
        for i, m in enumerate(meta):
            d = _tokens(" ".join([m.get("code", ""), m.get("name", ""), m.get("category", ""), m.get("brand", ""),
                                  m.get("description", ""), " ".join(m.get("colours", []))]))
            lex = len(q & d) / max(len(q), 1)
            # ngưỡng hiệu chỉnh trên dữ liệu thật: truy vấn liên quan có cosine CLIP 0,24–0,33, không liên quan 0,17–0,235
            if lex > 0 or cos[i] >= MIN_TEXT_COSINE:         # loại kết quả không liên quan
                out.append((int(m["id"]), float(0.6 * prob[i] + 0.4 * lex)))
        out.sort(key=lambda x: -x[1])
        return out[:limit]
