"""Ghi âm micro cho tìm kiếm bằng giọng nói: `record_wav` với micro giả, các ca lỗi, và màn hình tìm kiếm (không cần CSDL / AI)."""
from __future__ import annotations

import io
import sys
import types
import wave

import pytest

from abc_fashion.view._util import record_wav


def _fake_sounddevice(pcm: bytes, seen: dict):
    class Stream:
        def __init__(self, **kw):
            seen.update(kw)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, frames):
            seen["frames"] = frames
            return pcm[:frames * 2].ljust(frames * 2, b"\x00"), False

    return types.SimpleNamespace(RawInputStream=Stream)


def _tone(n: int, amp: int) -> bytes:
    import array
    return array.array("h", [amp if i % 2 else -amp for i in range(n)]).tobytes()


def test_record_wav_returns_mono_16bit_wav(monkeypatch):
    seen: dict = {}
    monkeypatch.setitem(sys.modules, "sounddevice", _fake_sounddevice(_tone(16000, 3000), seen))
    data = record_wav(1.0, 16000)
    assert seen["samplerate"] == 16000 and seen["channels"] == 1 and seen["dtype"] == "int16" and seen["frames"] == 16000
    with wave.open(io.BytesIO(data)) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()) == (1, 2, 16000, 16000)


@pytest.mark.parametrize("why, module, expect", [
    ("tắt tiếng", _fake_sounddevice(_tone(16000, 1), {}), "không nghe thấy"),
    ("thiếu thư viện", None, "sounddevice"),
])
def test_record_wav_errors_are_runtime_errors_in_vietnamese(monkeypatch, why, module, expect):
    monkeypatch.setitem(sys.modules, "sounddevice", module)               # None → ImportError khi import
    with pytest.raises(RuntimeError, match=expect):
        record_wav(1.0, 16000)


def test_record_wav_without_microphone(monkeypatch):
    class Broken:
        def RawInputStream(self, **kw):
            raise OSError("Error querying device -1")
    monkeypatch.setitem(sys.modules, "sounddevice", Broken())
    with pytest.raises(RuntimeError, match="không ghi âm được"):
        record_wav(1.0, 16000)


# ---------------------------------------------------------------- màn hình tìm kiếm
@pytest.fixture()
def search_screen(tk_root, monkeypatch):
    from tkinter import filedialog, messagebox

    from abc_fashion.view.catalogue import search_style_frm

    class FakeController:
        """Thay CatalogueController: màn hình dựng được mà không cần CSDL / dịch vụ AI."""

        def __init__(self):
            self.heard: list[bytes] = []

        def find_style_ids_by_voice(self, audio: bytes) -> list[int]:
            self.heard.append(audio)
            return []

        def get_active_styles(self, ids: list[int]) -> list:
            return []

    errors: list = []
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: errors.append(a))
    monkeypatch.setattr(search_style_frm, "CatalogueController", FakeController)
    monkeypatch.setattr(search_style_frm, "RECORD_SECONDS", 1)
    frm = search_style_frm.SearchStyleFrm(None, "")
    yield frm, search_style_frm, filedialog, errors
    frm.destroy()
    assert not errors, errors


def _pump(tk_root, frm, seconds=10):
    import time
    end = time.time() + seconds
    while time.time() < end and "disabled" in frm.btn_search.state():
        tk_root.update()
        time.sleep(0.02)
    tk_root.update()


def test_voice_button_records_then_searches(tk_root, search_screen, monkeypatch):
    frm, mod, _, _ = search_screen
    monkeypatch.setattr(mod, "record_wav", lambda seconds: b"RIFF-fake-wav")
    frm.on_search_by_voice()
    assert "disabled" in frm.btn_search_by_voice.state()
    assert "Đang nghe" in frm.lbl_message.cget("text")
    _pump(tk_root, frm)
    assert frm.catalogue_controller.heard == [b"RIFF-fake-wav"]
    assert "disabled" not in frm.btn_search.state()


def test_voice_button_falls_back_to_file_when_no_microphone(tk_root, search_screen, monkeypatch, tmp_path):
    frm, mod, filedialog, _ = search_screen

    def no_mic(seconds):
        raise RuntimeError("không ghi âm được (không có micro)")
    f = tmp_path / "q.wav"
    f.write_bytes(b"from-file")
    asked = []
    monkeypatch.setattr(mod, "record_wav", no_mic)
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **k: asked.append(k) or str(f))
    frm.on_search_by_voice()
    _pump(tk_root, frm)
    assert asked and frm.catalogue_controller.heard == [b"from-file"]


def test_voice_file_button_skips_recording(tk_root, search_screen, monkeypatch, tmp_path):
    frm, mod, filedialog, _ = search_screen
    f = tmp_path / "q.mp3"
    f.write_bytes(b"mp3-bytes")
    monkeypatch.setattr(mod, "record_wav", lambda s: pytest.fail("không được ghi âm"))
    monkeypatch.setattr(filedialog, "askopenfilename", lambda **k: str(f))
    frm.btn_voice_file.invoke()
    _pump(tk_root, frm)
    assert frm.catalogue_controller.heard == [b"mp3-bytes"]
