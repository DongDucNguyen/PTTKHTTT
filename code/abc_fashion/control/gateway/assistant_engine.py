"""AssistantEngine — AI Model Service (LLM của Chương 3), có chế độ cơ bản.

Gateway không truy cập CSDL: Frm gắn dữ liệu thật của style lên đối tượng trước khi gọi
(`style.variants` kèm `available`, `style.materials`, `style.size_chart`, `style.reviews`, `style.promotion`).

- Chế độ `model`: khi ABC_FASHION_GATEWAY_MODE=http thì gọi dịch vụ AI thật (external_services/ai_service, cổng 8104:
  /v1/assistant/chat, /summarise, /moderate); hoặc khi đặt ABC_FASHION_LLM_URL (POST JSON {"system","prompt"} → {"text"}).
  Câu trả lời được đối chiếu với dữ liệu thật; câu sai bị loại và ghi thành grounding event.
- Chế độ `basic` (mặc định / khi mô hình lỗi): trả lời bằng mẫu câu từ dữ liệu sản phẩm, không bịa (NFR14).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
import urllib.request

from abc_fashion.control.gateway import _http
from abc_fashion.model.assistant import AssistantMode, GroundingCheck, GroundingEvent
from abc_fashion.model.catalogue import Style
from abc_fashion.model.returns import RETURN_WINDOW_DAYS
from abc_fashion.model.review import FitVote, Review
from abc_fashion.model.sales import FREE_SHIPPING_THRESHOLD, promo_price

LLM_URL = os.environ.get("ABC_FASHION_LLM_URL", "")
LLM_NAME = os.environ.get("ABC_FASHION_LLM_NAME", "chapter3-llm")
BASIC_NAME = "basic-template"

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?:\+?84|0)(?:[\s.-]?\d){8,10}")
_URL = re.compile(r"(https?://|www\.)\S+", re.I)
_MONEY = re.compile(r"(\d{1,3}(?:[.,]\d{3})+|\d{4,})\s*(?:đ|d|vnd|vnđ|dong|đồng)?", re.I)

_BAD_WORDS = ("dm ", "đm", "dmm", "vcl", "vkl", "địt", "dit me", "lồn", "cặc", "đéo", "fuck", "shit", "ngu như")
_ADS = ("zalo", "inbox", "mua sỉ", "giá sỉ", "shopee", "lazada", "tiki", "ib mình", "kết bạn")
_HEALTH = ("chữa", "trị bệnh", "kháng khuẩn", "ung thư", "giảm cân", "y tế", "thải độc")

_INTENTS = [
    ("price", ("gia", "bao nhieu tien", "bao nhieu", "price", "cost", "khuyen mai", "giam")),
    ("stock", ("con hang", "het hang", "ton kho", "con khong", "con size", "stock", "co san")),
    ("fabric", ("chat lieu", "vai", "cotton", "lua", "thanh phan", "material", "fabric")),
    ("fit", ("size", "co nao", "vua", "rong", "hoi chat", "bi chat", "form", "fit", "so do", "cao", "nang", "kg")),
    ("care", ("giat", "ui", "bao quan", "care", "phoi")),
    ("policy", ("doi", "tra", "hoan", "bao hanh", "ship", "giao hang", "van chuyen", "phi")),
]


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFD", (text or "").lower().replace("đ", "d"))
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _money(x: int) -> str:
    return f"{x:,}".replace(",", ".") + " đ"


def mask_personal_data(text: str) -> str:
    """Che e-mail, số điện thoại trước khi lưu / gửi mô hình (NFR16)."""
    return _PHONE.sub("[số điện thoại]", _EMAIL.sub("[email]", text or ""))


class AssistantEngine:
    """Dùng bởi: AssistantFrm, ReviewFrm, StyleDetailFrm."""

    def ask(self, question: str, style: Style) -> dict:
        """Trả `{"answer", "mode", "model_name", "events", "question"}` (`question` đã che dữ liệu cá nhân)."""
        masked = mask_personal_data(question)
        if self._llm_endpoint():
            try:
                raw = self._call_llm(masked, style)
                answer, events = self._ground(raw, style)
                if answer.strip():
                    return {"answer": answer, "mode": AssistantMode.MODEL, "model_name": getattr(self, "last_model", None) or LLM_NAME,
                            "events": events, "question": masked}
            except (OSError, ValueError, KeyError, _http.GatewayUnavailable):
                pass                                    # mô hình lỗi → chế độ cơ bản
        return {"answer": self._basic_answer(masked, style), "mode": AssistantMode.BASIC,
                "model_name": BASIC_NAME, "events": [], "question": masked}

    def summarise_reviews(self, style: Style) -> str:
        reviews: list[Review] = getattr(style, "reviews", None) or []
        if not reviews:
            return ""
        if _http.use_http():                            # LLM thật; lỗi thì dùng bản tóm tắt theo quy tắc bên dưới
            try:
                status, data = _http.call("ai", "POST", "/v1/assistant/summarise", {"reviews": [
                    {"rating": r.rating, "body": mask_personal_data(r.body), "fit_vote": r.fit_vote.value if r.fit_vote else None}
                    for r in reviews]})
                if status == 200 and data.get("summary"):
                    return data["summary"]
            except _http.GatewayUnavailable:
                pass
        avg = sum(r.rating for r in reviews) / len(reviews)
        votes = {v: sum(1 for r in reviews if r.fit_vote == v) for v in FitVote}
        parts = [f"{avg:.1f}/5 sao từ {len(reviews)} đánh giá."]
        top = max(votes, key=votes.get)
        if votes[top]:
            label = {FitVote.RUNS_SMALL: "hơi chật, nên chọn lên một cỡ",
                     FitVote.TRUE_TO_SIZE: "đúng cỡ", FitVote.RUNS_LARGE: "hơi rộng, có thể chọn nhỏ hơn một cỡ"}[top]
            parts.append(f"Đa số ({votes[top]}/{len(reviews)}) cho rằng sản phẩm {label}.")
        good = [r for r in reviews if r.rating >= 4]
        bad = [r for r in reviews if r.rating <= 2]
        if good:
            parts.append("Khen: " + self._snippet(good[0].body))
        if bad:
            parts.append("Chê: " + self._snippet(bad[0].body))
        return " ".join(parts)

    def moderate(self, review: Review) -> tuple[bool, str]:
        text = review.body or ""
        if _http.use_http():                            # kiểm duyệt bằng AI thật; lỗi thì dùng quy tắc bên dưới
            try:
                status, data = _http.call("ai", "POST", "/v1/assistant/moderate", {"text": text})
                if status == 200:
                    return bool(data["approved"]), data.get("reason") or ""
            except (_http.GatewayUnavailable, KeyError):
                pass
        low = " " + text.lower() + " "
        if any(w in low for w in _BAD_WORDS):
            return False, "Có ngôn từ không phù hợp"
        if _EMAIL.search(text) or _PHONE.search(text):
            return False, "Chứa dữ liệu cá nhân (e-mail / số điện thoại)"
        if _URL.search(text) or any(w in low for w in _ADS):
            return False, "Có dấu hiệu quảng cáo / đường dẫn"
        if len(text.strip()) < 5:
            return False, "Nội dung quá ngắn"
        return True, ""

    # ---------- chế độ cơ bản ----------
    def _basic_answer(self, question: str, style: Style) -> str:
        q = _fold(question)
        if any(w in question.lower() for w in _HEALTH):
            return ("Mình không thể đưa ra thông tin về tác dụng sức khoẻ của sản phẩm. "
                    "Bạn có thể hỏi về giá, tồn kho, chất liệu, bảng cỡ hoặc chính sách đổi trả.")
        intents = [name for name, keys in _INTENTS if any(k in q for k in keys)]
        if not intents:
            intents = ["price", "stock", "fabric"]
        lines = [getattr(self, f"_answer_{name}")(style, q) for name in dict.fromkeys(intents)]
        return " ".join(line for line in lines if line)

    def _answer_price(self, style: Style, q: str) -> str:
        variants = [v for v in getattr(style, "variants", []) if v.status is None or v.status.value == "active"]
        if not variants:
            return "Hiện chưa có thông tin giá của sản phẩm này."
        promo = getattr(style, "promotion", None)
        auto = promo is not None and not getattr(promo, "voucher_count", 0)
        prices = sorted({v.price for v in variants})
        text = f"Giá {style.name}: " + (_money(prices[0]) if len(prices) == 1
                                         else f"từ {_money(prices[0])} đến {_money(prices[-1])}") + "."
        if auto:
            text += f" Đang có khuyến mãi \"{promo.name}\", giá sau giảm từ {_money(promo_price(prices[0], promo))}."
        elif promo is not None:
            text += f" Chương trình \"{promo.name}\" đang áp dụng khi nhập mã giảm giá lúc thanh toán."
        return text

    def _answer_stock(self, style: Style, q: str) -> str:
        variants = getattr(style, "variants", [])
        if not variants:
            return ""
        have = [f"{v.colour}/{v.size_label}" for v in variants if (getattr(v, "available", 0) or 0) > 0]
        out = [f"{v.colour}/{v.size_label}" for v in variants if (getattr(v, "available", 0) or 0) <= 0]
        text = ("Còn hàng: " + ", ".join(have) + ".") if have else "Sản phẩm hiện đã hết hàng."
        if have and out:
            text += " Hết hàng: " + ", ".join(out) + "."
        return text

    def _answer_fabric(self, style: Style, q: str) -> str:
        materials = getattr(style, "materials", [])
        if not materials:
            return "Chưa có thông tin chất liệu."
        return f"{style.name} làm từ: " + ", ".join(f"{m.material} {m.percent}%" for m in materials) + "."

    def _answer_fit(self, style: Style, q: str) -> str:
        chart = getattr(style, "size_chart", [])
        parts = []
        if style.fit_type:
            parts.append(f"Dáng {style.fit_type.value}.")
        if style.model_info:
            parts.append(style.model_info + ".")
        if chart:
            by_size: dict[str, list[str]] = {}
            for e in chart:
                by_size.setdefault(e.size_label, []).append(f"{e.measure.value} {e.value_cm:g} cm")
            parts.append("Bảng cỡ: " + "; ".join(f"{s}: {', '.join(m)}" for s, m in by_size.items()) + ".")
        reviews = getattr(style, "reviews", None) or []
        small = sum(1 for r in reviews if r.fit_vote == FitVote.RUNS_SMALL)
        if reviews and small * 2 > len(reviews):
            parts.append("Nhiều khách nhận xét sản phẩm hơi chật, nên cân nhắc lên một cỡ.")
        return " ".join(parts) or "Chưa có bảng cỡ cho sản phẩm này."

    def _answer_care(self, style: Style, q: str) -> str:
        return f"Hướng dẫn bảo quản: {style.care_instructions}" if style.care_instructions else ""

    def _answer_policy(self, style: Style, q: str) -> str:
        return (f"Đổi / trả trong {RETURN_WINDOW_DAYS} ngày kể từ khi nhận hàng. "
                f"Miễn phí vận chuyển cho đơn từ {_money(FREE_SHIPPING_THRESHOLD)}.")

    # ---------- chế độ mô hình ----------
    def _context(self, style: Style) -> str:
        return " ".join(filter(None, [self._answer_price(style, ""), self._answer_stock(style, ""),
                                      self._answer_fabric(style, ""), self._answer_fit(style, ""),
                                      self._answer_care(style, ""), self._answer_policy(style, "")]))

    def _call_llm(self, question: str, style: Style) -> str:
        body = json.dumps({"system": "Chỉ trả lời dựa trên DỮ LIỆU. Không bịa giá, tồn kho, chất liệu. "
                                     "Không nói về tác dụng sức khoẻ.",
                           "prompt": f"DỮ LIỆU: {self._context(style)}\nCÂU HỎI: {question}"}).encode("utf-8")
        if _http.use_http():
            status, data = _http.call("ai", "POST", "/v1/assistant/chat", json.loads(body.decode("utf-8")))
            if status != 200:
                raise ValueError(data)
            self.last_model = data.get("model")
            return data["text"]
        req = urllib.request.Request(LLM_URL, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))["text"]

    @staticmethod
    def _llm_endpoint() -> bool:
        return _http.use_http() or bool(LLM_URL)

    def _ground(self, answer: str, style: Style) -> tuple[str, list[GroundingEvent]]:
        """Loại các câu không khớp dữ liệu thật; mỗi câu loại là một grounding event."""
        variants = getattr(style, "variants", [])
        promo = getattr(style, "promotion", None)
        prices = {v.price for v in variants} | {promo_price(v.price, promo) for v in variants}
        prices |= {FREE_SHIPPING_THRESHOLD}
        materials = {_fold(m.material) for m in getattr(style, "materials", [])}
        in_stock = any((getattr(v, "available", 0) or 0) > 0 for v in variants)
        kept, events = [], []
        for sentence in re.split(r"(?<=[.!?])\s+", answer.strip()):
            s = _fold(sentence)
            check = None
            amounts = {int(re.sub(r"\D", "", m.group(1))) for m in _MONEY.finditer(sentence)}
            if amounts - prices:
                check = GroundingCheck.PRICE
            elif ("het hang" in s and in_stock) or ("con hang" in s and not in_stock):
                check = GroundingCheck.STOCK
            elif any(w in sentence.lower() for w in _HEALTH):
                check = GroundingCheck.HEALTH
            elif "%" in sentence and materials and not any(m in s for m in materials):
                check = GroundingCheck.FABRIC
            elif any(w in s for w in ("ban chay nhat", "hot nhat", "nhieu nguoi mua nhat")):
                check = GroundingCheck.POPULARITY
            if check:
                events.append(GroundingEvent(check_name=check, removed_text=sentence))
            else:
                kept.append(sentence)
        return " ".join(kept), events

    @staticmethod
    def _snippet(text: str, n: int = 90) -> str:
        text = mask_personal_data(" ".join((text or "").split()))
        return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"
