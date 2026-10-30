"""Dịch vụ AI THẬT (external_services/ai_service: CLIP, Whisper, LLM Ollama) qua các gateway ở chế độ http.

Cần dịch vụ AI chạy và mô hình đã nạp (`cd external_services && python manage.py start ai`); không có thì bỏ qua.
Kết quả của mô hình thật nên chỉ khẳng định các ca rõ ràng (đúng sản phẩm đứng đầu, câu không liên quan → rỗng…).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request

import pytest

from abc_fashion.control.gateway import _http
from abc_fashion.control.gateway.assistant_engine import AssistantEngine
from abc_fashion.control.gateway.search_engine import SearchEngine
from abc_fashion.model.assistant import AssistantMode
from abc_fashion.model.catalogue import FitType, VariantStatus, ProductVariant, Style
from abc_fashion.model.review import FitVote, Review
from conftest import CODE_DIR

EXTERNAL = os.path.join(os.path.dirname(CODE_DIR), "external_services")
PRODUCTS = os.path.join(CODE_DIR, "media", "products")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CJK = re.compile(r"[　-鿿가-힯＀-￯]")

CATALOGUE = [  # id, mã style (= tên file ảnh), tên, danh mục, thương hiệu, mô tả, màu
    (1, "SH-LIN-01", "Linen Regular Shirt", "Shirts", "ABC Basics", "Regular fit linen shirt", ["White"]),
    (2, "JN-SLM-02", "Slim Fit Jeans", "Jeans", "ABC Denim", "Slim fit stretch denim jeans", ["Indigo"]),
    (3, "DR-MID-03", "Floral Midi Dress", "Dresses", "ABC Studio", "Relaxed midi dress in a floral viscose print", ["Floral"]),
    (4, "TS-BAS-04", "Basic Cotton Tee", "Tops", "ABC Basics", "Soft cotton crew neck t-shirt", ["Black"]),
]


def _health() -> dict | None:
    try:
        return json.load(urllib.request.urlopen(_http.base_url("ai") + "/health", timeout=3))
    except (OSError, ValueError):
        return None


def _ready(h) -> bool:
    return bool(h) and "clip=ready, whisper=ready" in h.get("models", "") and h["models"].endswith(":ok")


@pytest.fixture(scope="module")
def ai():
    if not _ready(_health()):
        manage = os.path.join(EXTERNAL, "manage.py")
        if os.path.exists(manage):
            subprocess.run([sys.executable, manage, "start", "ai"], capture_output=True, timeout=400)
        deadline = time.time() + 240
        while time.time() < deadline and not _ready(_health()):
            time.sleep(3)
    if not _ready(_health()):
        pytest.skip("Dịch vụ AI chưa sẵn sàng (cd external_services && python manage.py setup --ai && python manage.py start ai; "
                    "cần Ollama với qwen2.5:3b)")


@pytest.fixture()
def http_mode(ai, monkeypatch):
    monkeypatch.setenv("ABC_FASHION_GATEWAY_MODE", "http")


@pytest.fixture(scope="module")
def indexed(ai):
    os.environ["ABC_FASHION_GATEWAY_MODE"] = "http"
    try:
        entries = []
        for sid, code, name, cat, brand, desc, colours in CATALOGUE:
            path = os.path.join(PRODUCTS, code.lower() + ".jpg")
            if not os.path.exists(path):
                pytest.skip("Chưa có ảnh sản phẩm (python db/fetch_product_photos.py)")
            entries.append({"id": sid, "code": code, "name": name, "brand": brand, "description": desc, "category": cat,
                            "colours": colours, "image_path": path})
        SearchEngine()._push_index(entries)
    finally:
        del os.environ["ABC_FASHION_GATEWAY_MODE"]


# ---------------------------------------------------------------- tìm kiếm bằng ảnh (CLIP)
def test_index_push_is_idempotent(http_mode, indexed):
    entries = [{"id": sid, "code": code, "name": name, "brand": brand, "description": desc, "category": cat, "colours": colours,
                "image_path": os.path.join(PRODUCTS, code.lower() + ".jpg")} for sid, code, name, cat, brand, desc, colours in CATALOGUE]
    assert SearchEngine()._push_index(entries)["status"] == "unchanged"


@pytest.mark.parametrize("sid, code", [(c[0], c[1]) for c in CATALOGUE])
def test_image_search_finds_the_product_first(http_mode, indexed, sid, code):
    with open(os.path.join(PRODUCTS, code.lower() + ".jpg"), "rb") as f:
        ids = SearchEngine().search_by_image(f.read())
    assert ids[0] == sid and set(ids) == {1, 2, 3, 4}


# ---------------------------------------------------------------- tìm kiếm bằng giọng nói (Whisper + LLM + CLIP)
@pytest.mark.parametrize("file, expected", [("vi_dress.mp3", 3), ("en_dress.mp3", 3), ("vi_tee.mp3", 4)])
def test_voice_search_finds_the_product_first(http_mode, indexed, file, expected):
    with open(os.path.join(DATA, file), "rb") as f:
        ids = SearchEngine().search_by_voice(f.read())
    assert ids and ids[0] == expected


def test_voice_search_unrelated_speech_returns_nothing(http_mode, indexed):
    with open(os.path.join(DATA, "noise_vi.mp3"), "rb") as f:
        assert SearchEngine().search_by_voice(f.read()) == []


def test_voice_search_rejects_non_audio(http_mode, indexed):
    with pytest.raises(RuntimeError):
        SearchEngine().search_by_voice(b"khong phai am thanh")


# ---------------------------------------------------------------- trợ lý (LLM)
def _style() -> Style:
    s = Style(id=3, code="ST-X", name="Áo thun cotton", fit_type=FitType.SLIM, care_instructions="Giặt máy, lộn trái")
    v = ProductVariant(id=1, sku="X-BLK-M", size_label="M", colour="Đen", price=450_000, status=VariantStatus.ACTIVE)
    v.available = 12
    s.variants, s.materials, s.size_chart, s.reviews, s.promotion = [v], [], [], [], None
    return s


def test_assistant_answers_with_real_llm_from_the_data(http_mode):
    r = AssistantEngine().ask("Áo này giá bao nhiêu và còn hàng không?", _style())
    assert r["mode"] == AssistantMode.MODEL and "qwen" in r["model_name"]
    assert "450" in r["answer"] and not CJK.search(r["answer"])


def test_assistant_masks_personal_data_before_the_model(http_mode):
    r = AssistantEngine().ask("Mình tên An, sđt 0901234567, áo này giá bao nhiêu?", _style())
    assert "0901234567" not in r["question"] and "0901234567" not in r["answer"]


def test_moderation_by_llm(http_mode):
    eng = AssistantEngine()
    assert eng.moderate(Review(body="Áo đẹp, vải mát, đúng cỡ, mình rất thích"))[0]
    assert eng.moderate(Review(body="Chất vải hơi mỏng, màu nhạt hơn ảnh nhưng vẫn ổn"))[0]       # chê lịch sự vẫn hợp lệ
    ok, reason = eng.moderate(Review(body="Liên hệ 0987654321 để mua rẻ hơn"))
    assert not ok and reason
    assert not eng.moderate(Review(body="Shop lừa đảo, sản phẩm như rác, ngu như bò"))[0]
    assert not eng.moderate(Review(body="Mua sỉ giá tốt inbox zalo nhé"))[0]


def test_review_summary_by_llm(http_mode):
    s = _style()
    s.reviews = [Review(rating=5, body="Vải mát, form đẹp", fit_vote=FitVote.TRUE_TO_SIZE),
                 Review(rating=4, body="Hơi chật ở vai, nên lấy lên một cỡ", fit_vote=FitVote.RUNS_SMALL)]
    text = AssistantEngine().summarise_reviews(s)
    assert 20 < len(text) < 700 and not CJK.search(text)


# ---------------------------------------------------------------- AI tắt: ứng dụng vẫn dùng được
def test_assistant_falls_back_when_ai_is_down(monkeypatch):
    monkeypatch.setenv("ABC_FASHION_GATEWAY_MODE", "http")
    monkeypatch.setenv("ABC_FASHION_AI_URL", "http://127.0.0.1:9")
    eng = AssistantEngine()
    assert eng.ask("Giá bao nhiêu?", _style())["mode"] == AssistantMode.BASIC            # chế độ cơ bản
    assert not eng.moderate(Review(body="Liên hệ 0987654321 để mua rẻ"))[0]           # quy tắc cục bộ
    with pytest.raises(_http.GatewayUnavailable):
        SearchEngine().search_by_image(b"x")                                              # tìm ảnh: báo lỗi để view gợi ý tìm bằng chữ


# ---------------------------------------------------------------- màn hình tìm kiếm gọi AI ở luồng phụ
def test_search_screen_image_search_with_real_ai(db, tk_root, http_mode, indexed, monkeypatch):
    """SearchStyleFrm: chọn ảnh → CLIP ở luồng phụ → kết quả hiện trên bảng (id theo CSDL thử)."""
    from tkinter import filedialog, messagebox

    from abc_fashion.view.catalogue.search_style_frm import SearchStyleFrm

    errors = []
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: errors.append(a))
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **k: os.path.join(PRODUCTS, "dr-mid-03.jpg"))
    sf = SearchStyleFrm(None, "")
    sf.on_search_by_image()
    deadline = time.time() + 60
    while time.time() < deadline and "disabled" in sf.btn_search.state():
        tk_root.update()
        time.sleep(0.05)
    sf.destroy()
    assert not errors and sf.list_style and sf.list_style[0].id == 3


@pytest.mark.parametrize("file, expected", [("vi_dress.mp3", 3), ("vi_tee.mp3", 4)])
def test_search_screen_voice_with_real_ai(db, tk_root, http_mode, indexed, monkeypatch, file, expected):
    """SearchStyleFrm: bấm "Nói để tìm" (micro giả đọc file mẫu) → Whisper + LLM + CLIP ở luồng phụ → đúng sản phẩm đầu."""
    from tkinter import messagebox

    from abc_fashion.view.catalogue import search_style_frm

    errors = []
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: errors.append(a))
    with open(os.path.join(DATA, file), "rb") as f:
        audio = f.read()
    monkeypatch.setattr(search_style_frm, "record_wav", lambda seconds: audio)
    sf = search_style_frm.SearchStyleFrm(None, "")
    sf.on_search_by_voice()
    deadline = time.time() + 90
    while time.time() < deadline and "disabled" in sf.btn_search.state():
        tk_root.update()
        time.sleep(0.05)
    tk_root.update()
    sf.destroy()
    assert not errors and sf.list_style and sf.list_style[0].id == expected


def test_saving_a_style_refreshes_the_ai_index(db, tk_root, http_mode, indexed, monkeypatch):
    """Sửa sản phẩm trong EditStyleFrm → chỉ mục AI tự cập nhật (không cần khởi động lại ứng dụng)."""
    from tkinter import messagebox

    from abc_fashion.control.dao.staff_member_dao import StaffMemberDAO
    from abc_fashion.model.catalogue import Style
    from abc_fashion.model.user import User
    from abc_fashion.view._sync import refresh_search_index
    from abc_fashion.view.product.edit_style_frm import EditStyleFrm

    errors = []
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: errors.append(a))
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)

    def etag() -> str:
        return _http.call("ai", "GET", "/v1/search/index")[1]["etag"]

    def wait_change(old: str | None, seconds: float = 60) -> str:
        deadline = time.time() + seconds
        while time.time() < deadline:
            tk_root.update()
            now = etag()
            if now != old:
                return now
            time.sleep(0.1)
        raise AssertionError("chỉ mục AI không đổi")

    refresh_search_index(tk_root)                                              # chỉ mục theo CSDL thử
    first = wait_change(etag())
    staff = StaffMemberDAO().get_staff_member_by_user(User(id=1))
    frm = EditStyleFrm(staff, Style(id=1))
    frm.txt_name.delete(0, "end")
    frm.txt_name.insert(0, "Áo sơ mi linen đổi tên")
    frm.on_save()
    second = wait_change(first)
    frm.destroy()
    assert second != first and not errors, errors
