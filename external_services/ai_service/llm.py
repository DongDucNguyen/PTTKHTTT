"""LLM THẬT chạy cục bộ qua Ollama (mặc định qwen2.5:3b). Chỉ dùng thư viện chuẩn."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
LLM_NAME = os.environ.get("AI_LLM_MODEL", "qwen2.5:3b")

_avail = {"at": 0.0, "ok": False}


class LlmUnavailable(Exception):
    """Ollama không chạy hoặc chưa có mô hình."""


def available() -> bool:
    if time.time() - _avail["at"] < 8:                      # nhớ kết quả vài giây để /health nhẹ
        return _avail["ok"]
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1.5) as r:
            names = [m["name"] for m in json.load(r).get("models", [])]
        _avail.update(at=time.time(), ok=any(n == LLM_NAME or n.split(":")[0] == LLM_NAME.split(":")[0] and ":" not in LLM_NAME
                                             for n in names))
    except (urllib.error.URLError, OSError, ValueError):
        _avail.update(at=time.time(), ok=False)
    return _avail["ok"]


def chat(system: str, user: str, json_mode: bool = False, temperature: float = 0.2, max_tokens: int = 400,
         timeout: float = 120) -> str:
    body = {"model": LLM_NAME, "stream": False, "keep_alive": "30m",
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "options": {"temperature": temperature, "num_predict": max_tokens}}
    if json_mode:
        body["format"] = "json"
    req = urllib.request.Request(f"{OLLAMA_URL}/api/chat", data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)["message"]["content"].strip()
    except (urllib.error.URLError, OSError, KeyError, ValueError) as e:
        raise LlmUnavailable(str(e)) from e
