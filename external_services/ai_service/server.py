"""DỊCH VỤ AI THẬT (cổng 8104): tìm kiếm bằng ảnh (CLIP), bằng giọng nói (Whisper) và trợ lý (LLM Ollama).

Khác ba dịch vụ mô phỏng, dịch vụ này chạy mô hình thật:
  - CLIP  openai/clip-vit-base-patch32       mã hoá ảnh / chữ vào cùng không gian vector
  - Whisper openai/whisper-large-v3-turbo    nhận dạng giọng nói (tiếng Việt, tiếng Anh…)
  - LLM  qwen2.5:3b chạy bằng Ollama          trợ lý hỏi đáp, tóm tắt và kiểm duyệt đánh giá
Mô hình tải một lần về ổ đĩa (~2,5 GB cho CLIP + Whisper) và nạp nền khi khởi động; trạng thái ở /health.
"""
from __future__ import annotations

import json
import re

from fastapi import File, Request, UploadFile
from fastapi.responses import JSONResponse

from ai_service import catalogue, llm, models
from common.app import ApiError, create_app

app = create_app("ai", "AI Model Service (CLIP · Whisper · LLM)", extra_health=lambda: {
    "models": f"clip={models.status['clip']}, whisper={models.status['whisper']}, "
              f"llm={llm.LLM_NAME}:{'ok' if llm.available() else 'khong-chay'}",
    "device": models.device_name(), "index": catalogue.count()})
catalogue.load()
models.start_background_load()

_CJK = re.compile(r"[　-〿぀-ヿ㐀-䶿一-鿿가-힯＀-￯]+")
_PII = re.compile(r"(?:[\w.+-]+@[\w-]+\.[\w.-]+)|(?:(?:\+?84|0)(?:[\s.-]?\d){8,10})", re.I)
_URL = re.compile(r"(https?://|www\.)\S+", re.I)


def _need(name: str) -> None:
    if not models.wait(name, 120):
        raise ApiError(503, "model_loading", f"Mô hình {name} đang nạp ({models.status[name]}), thử lại sau")


def _llm(system: str, user: str, **kw) -> str:
    """Gọi LLM; loại ký tự Hán / Nhật / Hàn lạc vào câu trả lời (qwen thỉnh thoảng bị)."""
    try:
        return _CJK.sub("", llm.chat(system, user, **kw)).strip()
    except llm.LlmUnavailable as e:
        raise ApiError(503, "llm_unavailable", f"LLM (Ollama) không sẵn sàng: {e}") from e


# ---------------------------------------------------------------- tìm kiếm
@app.put("/v1/search/index")
async def put_index(request: Request):
    """Nhận danh mục sản phẩm (meta JSON + ảnh) và dựng chỉ mục vector. Gọi lại với dữ liệu cũ thì không tính lại."""
    form = await request.form()
    try:
        meta = json.loads(form["meta"])
    except (KeyError, ValueError):
        raise ApiError(422, "invalid_meta", "Thiếu trường meta (JSON danh sách style)") from None
    images = {k: await v.read() for k, v in form.multi_items() if hasattr(v, "read")}
    _need("clip")
    return catalogue.build(meta, images, models)


@app.get("/v1/search/index")
def index_info():
    return {"count": catalogue.count(), "etag": catalogue.etag()}


@app.post("/v1/search/image")
async def search_image(file: UploadFile = File(...)):
    if not catalogue.count():
        raise ApiError(409, "index_empty", "Chưa có chỉ mục sản phẩm (ứng dụng sẽ đẩy lên khi khởi động)")
    data = await file.read()
    _need("clip")
    try:
        vec = models.embed_images([data])[0]
    except Exception as e:                                  # noqa: BLE001 - ảnh hỏng
        raise ApiError(422, "invalid_image", f"Không đọc được ảnh: {e}") from e
    ranked = catalogue.rank_by_image(vec)
    return {"ids": [i for i, _ in ranked], "scores": [round(s, 4) for _, s in ranked]}


@app.post("/v1/search/voice")
async def search_voice(file: UploadFile = File(...)):
    if not catalogue.count():
        raise ApiError(409, "index_empty", "Chưa có chỉ mục sản phẩm (ứng dụng sẽ đẩy lên khi khởi động)")
    data = await file.read()
    _need("whisper"), _need("clip")
    try:
        transcript = models.transcribe(data)
    except ValueError as e:
        raise ApiError(422, "invalid_audio", str(e)) from e
    if not transcript:
        return {"transcript": "", "query": "", "ids": [], "scores": []}
    query = transcript
    try:                                                    # LLM chuyển lời nói (tiếng Việt…) thành cụm từ khoá tiếng Anh cho danh mục
        query = _llm("You turn a shopper's spoken request into a short English product search phrase for a fashion catalogue "
                     "(item type, colour, style). Reply with the phrase only, no quotes, no explanation.", transcript,
                     temperature=0, max_tokens=30, timeout=30).strip().strip('"')
    except ApiError:
        pass                                                # không có LLM: dùng nguyên lời nhận dạng
    ranked = catalogue.rank_by_text(models.embed_texts([query])[0], f"{query} {transcript}")
    return {"transcript": transcript, "query": query, "ids": [i for i, _ in ranked], "scores": [round(s, 4) for _, s in ranked]}


# ---------------------------------------------------------------- trợ lý
@app.post("/v1/assistant/chat")
async def chat(request: Request):
    body = await request.json()
    system, prompt = (body.get("system") or "").strip(), (body.get("prompt") or "").strip()
    if not prompt:
        raise ApiError(422, "empty_prompt", "Thiếu prompt")
    text = _llm(system + "\nChỉ dùng tiếng Việt (tuyệt đối không dùng chữ Hán), tối đa 4 câu, giọng thân thiện. Số tiền ghi dạng 450.000 đ.", prompt,
                temperature=0.2, max_tokens=350)
    return {"text": text, "model": llm.LLM_NAME}


@app.post("/v1/assistant/summarise")
async def summarise(request: Request):
    reviews = (await request.json()).get("reviews") or []
    if not reviews:
        return {"summary": ""}
    avg = sum(int(r.get("rating") or 0) for r in reviews) / len(reviews)
    lines = "\n".join(f"- {r.get('rating')} sao" + (f" ({r['fit_vote']})" if r.get("fit_vote") else "") + f": {r.get('body', '')}"
                      for r in reviews[:40])
    text = _llm("Bạn tóm tắt đánh giá sản phẩm thời trang bằng tiếng Việt, 2–3 câu: điểm trung bình, ưu điểm, nhược điểm, độ vừa cỡ. "
                "Chỉ dựa trên đánh giá được cung cấp, không bịa thêm.",
                f"Điểm trung bình thật: {avg:.1f}/5 từ {len(reviews)} đánh giá.\n{lines}", temperature=0.2, max_tokens=220)
    return {"summary": text, "model": llm.LLM_NAME}


@app.post("/v1/assistant/moderate")
async def moderate(request: Request):
    text = ((await request.json()).get("text") or "").strip()
    if len(text) < 5:
        return {"approved": False, "reason": "Nội dung quá ngắn", "engine": "rules"}
    if _PII.search(text):
        return {"approved": False, "reason": "Chứa dữ liệu cá nhân (e-mail / số điện thoại)", "engine": "rules"}
    if _URL.search(text):
        return {"approved": False, "reason": "Có đường dẫn / quảng cáo", "engine": "rules"}
    raw = _llm('Bạn là người kiểm duyệt đánh giá sản phẩm thời trang. TỪ CHỐI nếu nội dung có: lời lẽ thô tục hoặc xúc phạm; '
               'quảng cáo, rao bán, mời liên hệ ngoài kênh; lộ thông tin cá nhân; hoặc không liên quan tới sản phẩm. '
               'Lời chê sản phẩm lịch sự là HỢP LỆ. Trả về JSON đúng dạng {"approved": true hoặc false, "reason": "lý do ngắn bằng tiếng Việt, rỗng nếu hợp lệ"}.',
               text, json_mode=True, temperature=0, max_tokens=80, timeout=60)
    try:
        verdict = json.loads(raw)
        approved = bool(verdict.get("approved"))
        return {"approved": approved, "reason": "" if approved else str(verdict.get("reason") or "Không đạt kiểm duyệt"),
                "engine": f"llm:{llm.LLM_NAME}"}
    except (ValueError, AttributeError):
        raise ApiError(502, "bad_llm_output", "LLM trả về dữ liệu không đúng định dạng") from None
