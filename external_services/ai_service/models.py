"""Nạp các mô hình AI THẬT: CLIP (ảnh ↔ chữ) và Whisper (giọng nói → chữ). Nạp nền khi khởi động, trạng thái ở /health."""
from __future__ import annotations

import io
import os
import subprocess
import threading

import numpy as np

CLIP_NAME = os.environ.get("AI_CLIP_MODEL", "openai/clip-vit-base-patch32")
WHISPER_NAME = os.environ.get("AI_WHISPER_MODEL", "openai/whisper-large-v3-turbo")

status = {"clip": "loading", "whisper": "loading"}          # loading | ready | error: <lý do>
ready = {"clip": threading.Event(), "whisper": threading.Event()}
_lock_clip, _lock_asr = threading.Lock(), threading.Lock()
_clip: dict = {}
_asr = None


def _device():
    import torch
    return "cuda:0" if torch.cuda.is_available() else "cpu"


def load_clip() -> None:
    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
        dev = _device()
        _clip["model"] = CLIPModel.from_pretrained(CLIP_NAME).to(dev).eval()
        _clip["proc"] = CLIPProcessor.from_pretrained(CLIP_NAME)
        _clip["dev"] = dev
        status["clip"] = "ready"
        ready["clip"].set()
    except Exception as e:                                  # noqa: BLE001
        status["clip"] = f"error: {e}"


def load_whisper() -> None:
    global _asr
    try:
        import torch
        from transformers import pipeline
        dev = _device()
        _asr = pipeline("automatic-speech-recognition", model=WHISPER_NAME, device=dev,
                        torch_dtype=torch.float16 if dev.startswith("cuda") else torch.float32)
        status["whisper"] = "ready"
        ready["whisper"].set()
    except Exception as e:                                  # noqa: BLE001
        status["whisper"] = f"error: {e}"


def start_background_load() -> None:
    for fn in (load_clip, load_whisper):
        threading.Thread(target=fn, daemon=True).start()


def wait(name: str, seconds: float = 120) -> bool:
    return ready[name].wait(seconds)


def device_name() -> str:
    try:
        import torch
        return torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    except Exception:                                       # noqa: BLE001
        return "cpu"


# ---------------------------------------------------------------- CLIP
def _norm(x):
    import torch
    return torch.nn.functional.normalize(x, dim=-1)


def embed_images(images: list[bytes]) -> np.ndarray:
    """Vector CLIP đã chuẩn hoá (N × 512) của các ảnh (bytes)."""
    import torch
    from PIL import Image
    pil = [Image.open(io.BytesIO(b)).convert("RGB") for b in images]
    with _lock_clip, torch.no_grad():
        inputs = _clip["proc"](images=pil, return_tensors="pt").to(_clip["dev"])
        out = _norm(_clip["model"].get_image_features(**inputs))
    return out.float().cpu().numpy()


def embed_texts(texts: list[str]) -> np.ndarray:
    import torch
    with _lock_clip, torch.no_grad():
        inputs = _clip["proc"](text=texts, return_tensors="pt", padding=True, truncation=True, max_length=77).to(_clip["dev"])
        out = _norm(_clip["model"].get_text_features(**inputs))
    return out.float().cpu().numpy()


# ---------------------------------------------------------------- Whisper
def decode_audio(data: bytes) -> np.ndarray:
    """Giải mã mọi định dạng (wav / mp3 / m4a / ogg…) về mono 16 kHz float32 bằng ffmpeg đi kèm."""
    import imageio_ffmpeg
    proc = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-nostdin", "-loglevel", "error", "-i", "pipe:0",
                           "-f", "f32le", "-ac", "1", "-ar", "16000", "pipe:1"], input=data, capture_output=True)
    if proc.returncode != 0 or not proc.stdout:
        raise ValueError(proc.stderr.decode("utf-8", "replace")[:200] or "không giải mã được âm thanh")
    return np.frombuffer(proc.stdout, dtype=np.float32).copy()


def transcribe(data: bytes) -> str:
    audio = decode_audio(data)
    if audio.size < 1600:                                   # < 0,1 giây
        return ""
    with _lock_asr:
        out = _asr({"array": audio, "sampling_rate": 16000}, chunk_length_s=30, generate_kwargs={"task": "transcribe"})
    return (out.get("text") or "").strip()
