"""Tiện ích dùng chung cho các màn hình Frm (module riêng tư của view layer, không có trong mô hình VP)."""
from __future__ import annotations

import functools
import logging
import os
import queue
import re
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
from datetime import date, datetime
from tkinter import messagebox, ttk

from abc_fashion.controller._errors import AccessDenied, BusinessError
from abc_fashion.controller._media import media_path  # noqa: F401 - dùng lại ở các màn hình hiện ảnh
from abc_fashion.view import _theme
from abc_fashion.view._format import (enum_choices, fmt_dt, label, money, ship_text,  # noqa: F401
                                        to_float, to_int)
from abc_fashion.view._theme import SKY_300, TEXT_500  # noqa: F401 - màu dùng trong vài màn hình

ERROR_FG = _theme.DANGER
OK_FG = _theme.SUCCESS

log = logging.getLogger("abc_fashion")

try:                                    # mục 13 #10: DateEntry cần tkcalendar
    from tkcalendar import DateEntry as _CalendarEntry
except ImportError:                     # pragma: no cover - chỉ khi thiếu tkcalendar
    _CalendarEntry = None


_CALENDAR_COLOURS = dict(
    background=_theme.BLUE_600, foreground="#FFFFFF", bordercolor=_theme.INK_600, headersbackground=_theme.INK_800,
    headersforeground=_theme.SKY_300, normalbackground=_theme.INK_850, normalforeground=_theme.TEXT_100,
    weekendbackground=_theme.INK_850, weekendforeground=_theme.SKY_300, othermonthbackground=_theme.INK_900,
    othermonthforeground=_theme.TEXT_500, othermonthwebackground=_theme.INK_900, othermonthweforeground=_theme.TEXT_500,
    selectbackground=_theme.BLUE_500, selectforeground="#FFFFFF", disabledbackground=_theme.INK_850,
    disabledforeground=_theme.TEXT_500, tooltipbackground=_theme.INK_800, tooltipforeground=_theme.TEXT_100,
    font="TkDefaultFont", style="DateEntry")

if _CalendarEntry is not None:
    class DateEntry(_CalendarEntry):
        def __init__(self, master, **kw):
            kw.setdefault("date_pattern", "dd/mm/yyyy")
            kw.setdefault("width", 12)
            for k, v in _CALENDAR_COLOURS.items():                   # lịch thả xuống theo theme (uiux-design 6.3)
                kw.setdefault(k, v)
            super().__init__(master, **kw)
else:
    class DateEntry(ttk.Entry):
        """Thay thế tối giản khi không có tkcalendar: ô nhập dd/mm/yyyy."""

        def __init__(self, master, **kw):
            kw.pop("date_pattern", None)
            super().__init__(master, width=kw.pop("width", 12))

        def get_date(self) -> date:
            return datetime.strptime(self.get().strip(), "%d/%m/%Y").date()

        def set_date(self, d: date) -> None:
            self.delete(0, "end")
            self.insert(0, d.strftime("%d/%m/%Y"))


def text_get(txa: tk.Text) -> str:
    return txa.get("1.0", "end").strip()


def text_set(txa: tk.Text, value: str, readonly: bool = False) -> None:
    txa.config(state="normal")
    txa.delete("1.0", "end")
    txa.insert("1.0", value or "")
    if readonly:
        txa.config(state="disabled")


def entry_set(entry: ttk.Entry, value) -> None:
    entry.delete(0, "end")
    entry.insert(0, "" if value is None else str(value))


# ---------------------------------------------------------------- widget
class ChoiceBox(ttk.Combobox):
    """Combobox chỉ đọc giữ cặp (nhãn, giá trị); `value()` trả giá trị đang chọn."""

    def __init__(self, master, choices: list[tuple[str, object]] = (), width: int = 22, **kw):
        super().__init__(master, state="readonly", width=width, **kw)
        self._values: list = []
        self.set_choices(choices)

    def set_choices(self, choices: list[tuple[str, object]], select_first: bool = True) -> None:
        self._values = [v for _, v in choices]
        self["values"] = [str(t) for t, _ in choices]
        if select_first and choices:
            self.current(0)
        elif not choices:
            self.set("")

    def value(self):
        i = self.current()
        return self._values[i] if 0 <= i < len(self._values) else None

    def select_value(self, value, key=None) -> None:
        key = key or (lambda v: v)
        for i, v in enumerate(self._values):
            if v is not None and value is not None and key(v) == key(value):
                self.current(i)
                return
            if v is None and value is None:
                self.current(i)
                return


def make_table(parent, columns: list[tuple[str, str, int]], height: int = 8,
               selectmode: str = "browse") -> ttk.Treeview:
    """Treeview có thanh cuộn. `columns` = [(khoá, tiêu đề, độ rộng)]. Đặt `tree.box` lên lưới."""
    box = ttk.Frame(parent)
    tree = ttk.Treeview(box, columns=[c[0] for c in columns], show="headings", height=height,
                        selectmode=selectmode)
    for key, heading, width in columns:
        tree.heading(key, text=heading)
        tree.column(key, width=width, anchor="e" if heading.endswith(("tiền", "giá", "SL", "Tổng")) else "w",
                    stretch=True)
    sb = ttk.Scrollbar(box, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    sb.grid(row=0, column=1, sticky="ns")
    box.columnconfigure(0, weight=1)
    box.rowconfigure(0, weight=1)
    tree.tag_configure("odd", background=_theme.ZEBRA)                # dòng xen kẽ (tag tạo trước = ưu tiên thấp)
    tree.tag_configure("bad", foreground=ERROR_FG)
    tree.tag_configure("mark", background=_theme.WARNING_BG, foreground=_theme.WARNING)
    tree.box = box
    tree.nominal_widths = {key: width for key, _, width in columns}
    return tree


def fill_table(tree: ttk.Treeview, rows) -> None:
    """`rows` = [(iid, values)] hoặc [(iid, values, tags)]."""
    keep = tree.selection()                                  # giữ dòng đang chọn khi nạp lại (làm tươi nền)
    tree.delete(*tree.get_children())
    for n, row in enumerate(rows):
        iid, values = row[0], row[1]
        extra = row[2] if len(row) > 2 else ()
        tags = (("odd",) if n % 2 else ()) + ((extra,) if isinstance(extra, str) else tuple(extra))
        tree.insert("", "end", iid=str(iid), values=values, tags=tags)
    still = [i for i in keep if tree.exists(i)]
    if still:
        tree.selection_set(still)
    _fit_columns(tree)


def selected(tree: ttk.Treeview, items: list):
    sel = tree.selection()
    if not sel:
        return None
    return next((i for i in items if str(i.id) == sel[0]), None)


def selected_all(tree: ttk.Treeview, items: list) -> list:
    sel = set(tree.selection())
    return [i for i in items if str(i.id) in sel]


def body(win: tk.Toplevel, title: str, padding: int = 16, header: bool = True, subtitle: str = "ABC Fashion") -> ttk.Frame:
    """Khung chung của mọi màn hình (uiux-design.md 6.1): header vector art + vùng nội dung."""
    win.title(f"ABC Fashion — {title}")
    win.configure(background=_theme.INK_900)
    win.minsize(_theme.px(win, 440), _theme.px(win, 160))   # đủ rộng để không cắt tiêu đề cửa sổ
    if header:
        _theme.header(win, title, subtitle)
    frame = ttk.Frame(win, padding=_theme.px(win, padding))
    frame.pack(fill="both", expand=True)
    win.after_idle(lambda: _theme.polish(win))              # gắn style nút sau khi màn hình dựng xong
    return frame


def message_label(parent) -> ttk.Label:
    return ttk.Label(parent, foreground=ERROR_FG, wraplength=_theme.px(parent, 640), justify="left")


def show(lbl: ttk.Label, text: str, ok: bool = False) -> None:
    lbl.config(text=text, foreground=OK_FG if ok else ERROR_FG)


def form_rows(parent, rows: list[tuple[str, tk.Widget]], start: int = 0, column: int = 0) -> int:
    """Đặt các cặp (nhãn, widget) theo lưới; trả số dòng kế tiếp."""
    r = start
    for text, widget in rows:
        ttk.Label(parent, text=text, style="Field.TLabel").grid(row=r, column=column, sticky="w",
                                                                 padx=(0, _theme.px(parent, 12)), pady=_theme.px(parent, 4))
        widget.grid(row=r, column=column + 1, sticky="we", pady=_theme.px(parent, 4))
        r += 1
    return r


def button_row(parent, buttons: list[ttk.Button], row: int, column: int = 0, columnspan: int = 2) -> None:
    box = ttk.Frame(parent)
    box.grid(row=row, column=column, columnspan=columnspan, sticky="e", pady=(_theme.px(parent, 12), 0))
    for b in buttons:
        b.pack(in_=box, side="left", padx=(_theme.px(parent, 8), 0))
    last = buttons[-1] if buttons else None                # nút cuối = hành động chính (uiux-design 6.2)
    if last is not None and not str(last.cget("style")) and _theme.classify(str(last.cget("text"))) is None             and str(last.cget("text")) not in ("Đóng", "Huỷ", "Quay lại"):
        last.configure(style="Primary.TButton")


def modal(child: tk.Toplevel, parent: tk.Misc) -> None:
    """Mở `child` mô thức và chờ nó đóng."""
    try:
        child.transient(parent.winfo_toplevel())
        child.wait_visibility()
        child.grab_set()
    except tk.TclError:
        pass
    parent.wait_window(child)


def confirm(parent, text: str) -> bool:
    return messagebox.askyesno("Xác nhận", text, parent=parent)


def info(parent, text: str) -> None:
    messagebox.showinfo("Thông báo", text, parent=parent)


def warn(parent, text: str) -> None:
    messagebox.showwarning("Chú ý", text, parent=parent)


def guarded(handler):
    """Mục 5.5: exception (mất kết nối, lỗi SQL) → hộp lỗi, ghi log; chương trình không tắt.

    Lỗi nghiệp vụ controller ném ra (BusinessError) không phải lỗi hệ thống: hiện ở `lbl_message` của màn hình nếu
    có, không thì hộp cảnh báo. AccessDenied → hộp "Không có quyền" rồi đóng màn hình.
    """
    @functools.wraps(handler)
    def wrapper(self, *args, **kwargs):
        try:
            return handler(self, *args, **kwargs)
        except AccessDenied as e:
            messagebox.showerror("Không có quyền", str(e), parent=self)
            self.after(0, self.destroy)
        except BusinessError as e:
            lbl = getattr(self, "lbl_message", None)
            if lbl is not None and lbl.winfo_exists():
                show(lbl, str(e))
            else:
                warn(self, str(e))
        except Exception as e:                  # noqa: BLE001 - hàng rào cuối của giao diện
            log.exception("Lỗi trong %s.%s", type(self).__name__, handler.__name__)
            try:
                messagebox.showerror("Lỗi hệ thống", str(e), parent=self)
            except tk.TclError:
                messagebox.showerror("Lỗi hệ thống", str(e))
    return wrapper


def logout(home: tk.Toplevel) -> None:
    """Đóng mọi cửa sổ của phiên, hiện lại LoginFrm (mục 9.1)."""
    from abc_fashion.view.account import login_frm

    login = login_frm.CURRENT_LOGIN
    root = home.master
    for w in list(root.winfo_children()):
        if isinstance(w, tk.Toplevel) and w is not login:
            w.destroy()
    if login is not None and login.winfo_exists():
        login.txt_password.delete(0, "end")
        login.deiconify()
        login.lift()
        login.txt_email.focus_set()


def home_window(win: tk.Toplevel, title: str, greeting: str, buttons: list[tuple[str, str, object]]) -> ttk.Frame:
    """Trang chủ (uiux-design.md 7.2): header lớn có lời chào + lưới ô 2 cột có biểu tượng; Đăng xuất là liên kết.

    `buttons` = [(thuộc tính, nhãn, handler)].
    """
    frame = body(win, title, padding=24, header=False)
    hero = _theme.header(win, greeting, title, tall=True)
    hero.pack_forget()
    hero.pack(side="top", fill="x", before=frame)
    tiles = [b for b in buttons if b[0] != "btn_logout"]
    for i, (attr, text, cmd) in enumerate(tiles):
        btn = ttk.Button(frame, text=text, command=cmd, style="Tile.TButton", compound="left", width=24,
                         image=_theme.icon(win, _theme.ICON_FOR.get(attr, "dot")))
        btn.grid(row=i // 2, column=i % 2, sticky="we", padx=_theme.px(win, 6), pady=_theme.px(win, 6))
        setattr(win, attr, btn)
    for attr, text, cmd in buttons:
        if attr == "btn_logout":
            btn = ttk.Button(frame, text=text, command=cmd, style="Link.TButton", compound="left",
                             image=_theme.icon(win, "logout", 18))
            btn.grid(row=(len(tiles) + 1) // 2, column=1, sticky="e", pady=(_theme.px(win, 12), 0))
            setattr(win, attr, btn)
    frame.columnconfigure((0, 1), weight=1, uniform="tile")
    win.resizable(False, False)
    return frame


def read_file(path: str) -> bytes:
    """Đọc file người dùng chọn (ảnh / âm thanh / bằng chứng) để chuyển cho controller."""
    with open(path, "rb") as fh:
        return fh.read()


# ---------------------------------------------------------------- media
def open_media(url: str | None) -> bool:
    """Mở ảnh / video bằng chương trình mặc định của hệ điều hành (file trong media/ hoặc đường dẫn http). False nếu không mở được."""
    if not url:
        return False
    try:
        if url.startswith(("http://", "https://")):
            import webbrowser
            return webbrowser.open(url)
        path = media_path(url)
        if not path or not os.path.exists(path):
            return False
        if sys.platform == "win32":
            os.startfile(path)                          # noqa: S606 - đường dẫn do ứng dụng tự sao chép vào media/
        else:
            import subprocess
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])
        return True
    except OSError:
        return False


def show_image(canvas: tk.Canvas, path: str | None, size: tuple[int, int]) -> None:
    """Vẽ ảnh lên canvas (Pillow); thiếu file / Pillow thì vẽ khung trống."""
    canvas.delete("all")
    w, h = size
    full = media_path(path) if path else None
    try:
        from PIL import Image, ImageTk
        if not full or not os.path.exists(full):
            raise FileNotFoundError(full)
        with Image.open(full) as im:
            im.thumbnail(size)
            photo = ImageTk.PhotoImage(im.copy())
        canvas.create_image(w // 2, h // 2, image=photo)
        canvas.image = photo                      # giữ tham chiếu để ảnh không bị thu hồi
    except Exception:                             # noqa: BLE001 - ảnh là phụ
        canvas.create_rectangle(2, 2, w - 2, h - 2, outline=_theme.INK_600, dash=(4, 3))
        canvas.create_text(w // 2, h // 2, text="(không có ảnh)", fill=_theme.TEXT_500)


# ---------------------------------------------------------------- ghi âm
def record_wav(seconds: float = 5.0, samplerate: int = 16000) -> bytes:
    """Ghi âm `seconds` giây từ micro mặc định (thư viện `sounddevice`), trả file WAV mono 16-bit.

    Gọi ở luồng phụ (`run_in_thread`): hàm chờ đủ thời gian ghi và không chạm Tk. Ném RuntimeError (thông báo tiếng Việt)
    khi thiếu thư viện, không có micro hoặc ghi được toàn khoảng lặng — view khi đó cho khách chọn file âm thanh.
    """
    import array
    import io
    import wave
    try:
        import sounddevice as sd
    except (ImportError, OSError) as e:
        raise RuntimeError("chưa cài thư viện ghi âm (pip install sounddevice)") from e
    frames = int(seconds * samplerate)
    try:
        with sd.RawInputStream(samplerate=samplerate, channels=1, dtype="int16") as stream:
            raw, _ = stream.read(frames)
        pcm = bytes(raw)
    except Exception as e:                              # noqa: BLE001 - không có micro, bị chặn quyền, thiết bị bận…
        raise RuntimeError(f"không ghi âm được ({e})") from e
    samples = array.array("h")
    samples.frombytes(pcm[:len(pcm) // 2 * 2])
    if not samples or max(max(samples), -min(samples)) < 100:
        raise RuntimeError("không nghe thấy tiếng nói (micro đang tắt hoặc bị tắt tiếng?)")
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(samplerate)
        w.writeframes(pcm)
    return out.getvalue()


# ---------------------------------------------------------------- giao diện chung
_NUMERIC = re.compile(r"^[+\-−]?\d[\d.,]*\s*(đ|%)?$")


def _fit_columns(tree: ttk.Treeview) -> None:
    """Giãn cột vừa nội dung (không hẹp hơn độ rộng gợi ý) và canh phải các cột toàn số / tiền."""
    try:
        font = tkfont.Font(root=tree, font=ttk.Style(tree).lookup("Treeview", "font") or "TkDefaultFont")
    except tk.TclError:
        font = tkfont.nametofont("TkDefaultFont")
    nominal = getattr(tree, "nominal_widths", {})
    rows = [tree.item(i, "values") for i in tree.get_children()]
    for n, col in enumerate(tree["columns"]):
        cells = [str(r[n]) for r in rows if n < len(r)]
        width = max([font.measure(tree.heading(col, "text")) + 28] + [font.measure(c) + 18 for c in cells[:300]])
        numeric = any(cells) and all(c == "" or _NUMERIC.match(c.strip()) for c in cells)
        tree.column(col, width=min(max(width, nominal.get(col, 0)), 420), anchor="e" if numeric else "w")


def enable_dpi_awareness() -> None:
    """Windows: bật DPI-aware trước khi tạo Tk để chữ không bị phóng to mờ trên màn hình scale 125–200%."""
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


def apply_theme(root: tk.Misc) -> None:
    """Theme "Midnight Atelier" (uiux-design.md): font, màu, style ttk — xem view/_theme.py."""
    _theme.apply(root)


def watch(win: tk.Misc, signature, reload, interval_ms: int = 3000) -> None:
    """Cứ `interval_ms` kiểm tra `signature()` (đọc CSDL); đổi so với lần trước thì gọi `reload()`.

    Dùng để màn hình tự cập nhật khi dữ liệu nền đổi (vd. kiện hàng tiến trạng thái). Tự dừng khi cửa sổ đóng.
    """
    state = {"sig": signature()}

    def tick():
        try:
            if not win.winfo_exists():
                return
            sig = signature()
            if sig != state["sig"]:
                state["sig"] = sig
                reload()
        except tk.TclError:
            return
        except Exception:                           # noqa: BLE001 - mất kết nối thoáng qua: thử lại ở lần sau
            log.exception("watch")
        win.after(interval_ms, tick)

    win.after(interval_ms, tick)


def run_in_thread(win: tk.Misc, work, done, poll_ms: int = 100) -> None:
    """Chạy `work()` ở luồng phụ, rồi gọi `done(kết_quả_hoặc_ngoại_lệ)` ở luồng giao diện.

    Luồng phụ KHÔNG chạm Tk: nó chỉ đặt kết quả vào hàng đợi; luồng giao diện hỏi hàng đợi định kỳ bằng `after`.
    Nhờ vậy an toàn dù vòng lặp Tk chưa chạy (kiểm thử) và DAO / widget chỉ bị gọi ở luồng giao diện (mục 11, quy tắc 6).
    """
    box: queue.Queue = queue.Queue(maxsize=1)

    def run():
        try:
            box.put(work())
        except Exception as e:                      # noqa: BLE001 - chuyển ngoại lệ về luồng giao diện xử lý
            box.put(e)

    def poll():
        try:
            if not win.winfo_exists():
                return
            result = box.get_nowait()
        except queue.Empty:
            win.after(poll_ms, poll)
            return
        except tk.TclError:
            return
        done(result)

    threading.Thread(target=run, daemon=True).start()
    win.after(poll_ms, poll)
