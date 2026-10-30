"""Theme "Midnight Atelier" (uiux-design.md): token màu, font, style ttk, header vector art, phân loại nút.

Mọi màu / font của giao diện lấy từ đây; các `XxxFrm` chỉ dùng tên style (`H2.TLabel`, `Muted.TLabel`…).
Ảnh vẽ bằng `_art.py` theo DPI thật và được cache trên cửa sổ gốc.
"""
from __future__ import annotations

import glob
import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

from abc_fashion.view._art import (BLUE_400, BLUE_500, BLUE_600, BLUE_700, CYAN_400, INK_600, INK_700, INK_800, INK_850,
                                   INK_900, INK_950, SKY_200, SKY_300, TEXT_100, TEXT_300, TEXT_500)
from abc_fashion.view import _art

__all__ = ["BLUE_400", "BLUE_500", "BLUE_600", "BLUE_700", "CYAN_400", "INK_600", "INK_700", "INK_800", "INK_850",
           "INK_900", "INK_950", "SKY_200", "SKY_300", "TEXT_100", "TEXT_300", "TEXT_500"]

SUCCESS, WARNING, DANGER, PROMO, VIOLET = "#3DDC97", "#F7C25C", "#FF7A8A", "#FF9DB5", "#B9A6FF"
DANGER_BG, WARNING_BG, ZEBRA = "#3A1622", "#2E2610", "#101C32"

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "media", "ui", "fonts")

# phân loại nút theo chữ (uiux-design.md 6.2)
PRIMARY_WORDS = ("Đăng nhập", "Đặt hàng", "Tìm", "Lưu", "Gửi", "Thêm vào giỏ", "Thanh toán", "Xác nhận", "Liên kết",
                 "Đăng ký", "Cập nhật trạng thái", "Áp dụng", "Duyệt", "Hoàn tiền", "Xem báo cáo", "Kết thúc kiểm tra")
DANGER_WORDS = ("Xoá", "Huỷ đơn", "Từ chối", "Khoá", "Huỷ phiếu", "Huỷ yêu cầu", "Ẩn")
LINK_WORDS = ("Đăng xuất", "Đăng ký tài khoản khách", "Quay lại")

ICON_FOR = {"btn_browse": "catalogue", "btn_cart": "cart", "btn_orders": "orders", "btn_profile": "profile",
            "btn_logout": "logout", "btn_manage_account": "accounts", "btn_manage_product": "product",
            "btn_manage_review": "review", "btn_view_audit_log": "audit", "btn_manage_order": "order",
            "btn_view_report": "report", "btn_manage_promotion": "promotion", "btn_process_return": "return",
            "btn_inspect_return": "inspect", "btn_view_stock": "stock", "btn_restock": "restock",
            "btn_search": "search", "btn_search_by_image": "image", "btn_search_by_voice": "mic"}

_fonts_loaded = False


# ---------------------------------------------------------------- font
def _load_fonts() -> None:
    """Nạp Be Vietnam Pro cho riêng tiến trình (không cài vào Windows); không có thì dùng Segoe UI."""
    global _fonts_loaded
    if _fonts_loaded or sys.platform != "win32":
        return
    _fonts_loaded = True
    import ctypes
    for path in glob.glob(os.path.join(FONT_DIR, "*.ttf")):
        try:
            ctypes.windll.gdi32.AddFontResourceExW(path, 0x10, 0)       # FR_PRIVATE
        except (AttributeError, OSError):
            pass


def _families(root: tk.Misc) -> tuple[str, str, str]:
    have = set(tkfont.families(root))
    if "Be Vietnam Pro" in have:
        return ("Be Vietnam Pro", "Be Vietnam Pro Medium" if "Be Vietnam Pro Medium" in have else "Be Vietnam Pro",
                "Be Vietnam Pro SemiBold" if "Be Vietnam Pro SemiBold" in have else "Be Vietnam Pro")
    return "Segoe UI", "Segoe UI", "Segoe UI Semibold"


_FONTS: list[tkfont.Font] = []              # giữ tham chiếu: Font bị thu hồi thì named font bị xoá theo


def _named(root, name: str, **kw) -> None:
    if name in tkfont.names(root):
        tkfont.nametofont(name, root).configure(**kw)
    else:
        _FONTS.append(tkfont.Font(root=root, name=name, **kw))


# ---------------------------------------------------------------- ảnh (cache trên cửa sổ gốc)
def scale_of(win: tk.Misc) -> float:
    try:
        return max(1.0, round(win.winfo_fpixels("1i") / 96 * 4) / 4)
    except tk.TclError:
        return 1.0


def _cache(win: tk.Misc) -> dict:
    root = win._root()
    if not hasattr(root, "_abc_images"):
        root._abc_images = {}
    return root._abc_images


def image(win: tk.Misc, key: str, make):
    """PhotoImage vẽ bằng `make(scale)` (Pillow), tạo một lần cho mỗi khoá."""
    cache = _cache(win)
    if key not in cache:
        from PIL import ImageTk
        cache[key] = ImageTk.PhotoImage(make(scale_of(win)), master=win._root())
    return cache[key]


def icon(win: tk.Misc, name: str, size: int = 22, colour: str = SKY_300, gap: int = 10):
    """Biểu tượng nét; `gap` px trong suốt bên phải làm khoảng cách tới chữ (ttk không có tuỳ chọn này)."""
    def make(s: float):
        from PIL import Image
        ic = _art.icon(name, size, s, colour)
        out = Image.new("RGBA", (ic.width + round(gap * s), ic.height), (0, 0, 0, 0))
        out.paste(ic, (0, 0))
        return out
    return image(win, f"icon:{name}:{size}:{colour}:{gap}", make)


def px(win: tk.Misc, v: float) -> int:
    return round(v * scale_of(win))


# ---------------------------------------------------------------- style
def apply(root: tk.Misc) -> None:
    """Gọi một lần sau khi tạo Tk: font, toàn bộ style ttk, màu mặc định cho widget tk (Text, Listbox, Toplevel)."""
    _load_fonts()
    regular, medium, semibold = _families(root)
    s = scale_of(root)
    _named(root, "TkDefaultFont", family=regular, size=10)
    _named(root, "TkTextFont", family=regular, size=10)
    _named(root, "TkMenuFont", family=regular, size=10)
    _named(root, "TkHeadingFont", family=medium, size=10)
    _named(root, "TkCaptionFont", family=semibold, size=11)
    _named(root, "TkTooltipFont", family=regular, size=9)
    for name, fam, size in (("AbcDisplay", semibold, 22), ("AbcH1", semibold, 16), ("AbcH2", semibold, 13),
                            ("AbcH3", semibold, 11), ("AbcButton", medium, 10), ("AbcSmall", regular, 9),
                            ("AbcBold", semibold, 10)):
        _named(root, name, family=fam, size=size)

    root.configure(background=INK_900)
    for pattern, value in (("*Toplevel.background", INK_900), ("*Canvas.background", INK_850),
                           ("*Canvas.highlightThickness", 0),
                           ("*Text.background", INK_800), ("*Text.foreground", TEXT_100),
                           ("*Text.insertBackground", TEXT_100), ("*Text.selectBackground", BLUE_600),
                           ("*Text.selectForeground", "#FFFFFF"), ("*Text.relief", "flat"), ("*Text.borderWidth", 0),
                           ("*Text.highlightThickness", 1), ("*Text.highlightBackground", INK_600),
                           ("*Text.highlightColor", BLUE_500), ("*Text.padX", round(8 * s)), ("*Text.padY", round(6 * s)),
                           ("*Text.font", "TkDefaultFont"),
                           ("*Listbox.background", INK_800), ("*Listbox.foreground", TEXT_100),
                           ("*Listbox.selectBackground", BLUE_600), ("*Listbox.selectForeground", "#FFFFFF"),
                           ("*Listbox.relief", "flat"), ("*Listbox.highlightThickness", 0),
                           ("*TCombobox*Listbox.background", INK_800), ("*TCombobox*Listbox.foreground", TEXT_100),
                           ("*TCombobox*Listbox.selectBackground", BLUE_600),
                           ("*TCombobox*Listbox.selectForeground", "#FFFFFF"), ("*TCombobox*Listbox.font", "TkDefaultFont")):
        root.option_add(pattern, value)

    st = ttk.Style(root)
    st.theme_use("clam")
    st.configure(".", background=INK_900, foreground=TEXT_100, fieldbackground=INK_800, bordercolor=INK_600,
                 lightcolor=INK_800, darkcolor=INK_800, troughcolor=INK_900, selectbackground=BLUE_600,
                 selectforeground="#FFFFFF", insertcolor=TEXT_100, focuscolor=BLUE_500, font="TkDefaultFont",
                 arrowcolor=SKY_300)
    st.map(".", foreground=[("disabled", TEXT_500)])
    st.configure("TFrame", background=INK_900)
    st.configure("Card.TFrame", background=INK_850)
    st.configure("TLabel", background=INK_900, foreground=TEXT_100)
    for name, fg, font in (("Muted", TEXT_300, "TkDefaultFont"), ("Field", TEXT_300, "TkDefaultFont"),
                           ("Small", TEXT_300, "AbcSmall"), ("H2", TEXT_100, "AbcH2"), ("H3", TEXT_100, "AbcH3"),
                           ("Display", TEXT_100, "AbcDisplay"), ("Brand", SKY_300, "AbcH1"), ("Price", SKY_200, "AbcH3"),
                           ("Promo", PROMO, "AbcBold"), ("Success", SUCCESS, "TkDefaultFont"),
                           ("Danger", DANGER, "TkDefaultFont"), ("Violet", VIOLET, "TkDefaultFont"),
                           ("Accent", SKY_300, "AbcBold")):
        st.configure(f"{name}.TLabel", foreground=fg, font=font)

    _buttons(root, st, s)

    pad = (round(8 * s), round(5 * s))
    for w in ("TEntry", "TCombobox", "TSpinbox", "DateEntry"):
        st.configure(w, fieldbackground=INK_800, foreground=TEXT_100, bordercolor=INK_600, lightcolor=INK_800,
                     darkcolor=INK_800, padding=pad, insertcolor=TEXT_100, arrowcolor=SKY_300, background=INK_800,
                     arrowsize=round(12 * s))
        st.map(w, bordercolor=[("focus", BLUE_500), ("hover", INK_600)], lightcolor=[("focus", INK_800)],
               fieldbackground=[("readonly", INK_800), ("disabled", INK_850)],
               foreground=[("disabled", TEXT_500), ("readonly", TEXT_100)],
               selectbackground=[("readonly", INK_800), ("!focus", INK_700)],
               selectforeground=[("readonly", TEXT_100)],
               background=[("active", INK_700), ("pressed", INK_700)], arrowcolor=[("disabled", TEXT_500)])

    rowh = round(tkfont.nametofont("TkDefaultFont", root).metrics("linespace") * 1.9)
    st.configure("Treeview", background=INK_850, fieldbackground=INK_850, foreground=TEXT_100, bordercolor=INK_600,
                 lightcolor=INK_850, darkcolor=INK_850, rowheight=rowh, borderwidth=0)
    st.map("Treeview", background=[("selected", BLUE_600)], foreground=[("selected", "#FFFFFF")])
    st.configure("Treeview.Heading", background=INK_800, foreground=SKY_300, font="TkHeadingFont", relief="flat",
                 bordercolor=INK_700, lightcolor=INK_800, darkcolor=INK_800, padding=(round(8 * s), round(6 * s)))
    st.map("Treeview.Heading", background=[("active", INK_700)])

    for orient in ("Vertical", "Horizontal"):
        st.configure(f"{orient}.TScrollbar", troughcolor=INK_900, background=INK_600, bordercolor=INK_900,
                     lightcolor=INK_600, darkcolor=INK_600, arrowcolor=SKY_300, arrowsize=round(12 * s), gripcount=0)
        st.map(f"{orient}.TScrollbar", background=[("active", INK_700), ("pressed", BLUE_600)])

    for w in ("TCheckbutton", "TRadiobutton"):
        st.configure(w, background=INK_900, foreground=TEXT_100, indicatorbackground=INK_800,
                     indicatorforeground="#FFFFFF", upperbordercolor=INK_600, lowerbordercolor=INK_600,
                     indicatormargin=(0, 0, round(6 * s), 0), focuscolor=INK_900)
        st.map(w, indicatorbackground=[("selected", BLUE_500), ("active", INK_700)],
               background=[("active", INK_900)], foreground=[("disabled", TEXT_500)])

    st.configure("TNotebook", background=INK_900, bordercolor=INK_600, lightcolor=INK_900, darkcolor=INK_900,
                 tabmargins=(0, round(4 * s), 0, 0))
    st.configure("TNotebook.Tab", background=INK_850, foreground=TEXT_300, bordercolor=INK_600, lightcolor=INK_850,
                 padding=(round(14 * s), round(6 * s)), font="AbcButton")
    st.map("TNotebook.Tab", background=[("selected", INK_800), ("active", INK_700)],
           foreground=[("selected", SKY_300)], lightcolor=[("selected", BLUE_500)])
    st.configure("TLabelframe", background=INK_900, bordercolor=INK_600, lightcolor=INK_900, darkcolor=INK_900,
                 relief="solid", borderwidth=1, padding=round(10 * s))
    st.configure("TLabelframe.Label", background=INK_900, foreground=SKY_300, font="AbcButton")
    st.configure("TSeparator", background=INK_600)
    st.configure("TProgressbar", background=BLUE_500, troughcolor=INK_800, bordercolor=INK_600)

    try:                                    # biểu tượng cửa sổ cho mọi Toplevel
        root.iconphoto(True, image(root, "logo:32", lambda sc: _art.logo(32, sc)),
                       image(root, "logo:64", lambda sc: _art.logo(64, sc)))
    except Exception:                       # noqa: BLE001 - biểu tượng là phụ
        pass


def _buttons(root, st: ttk.Style, s: float) -> None:
    """Nút bo góc bằng ảnh 9 lát (uiux-design.md 6.2)."""
    r = 8
    variants = {  # style: (thường, rê chuột, bấm, vô hiệu, chữ, chữ vô hiệu)
        "TButton": ((INK_800, INK_600), (INK_700, BLUE_500), (INK_850, BLUE_500), (INK_850, INK_700), TEXT_100, TEXT_500),
        "Primary.TButton": ((BLUE_500, None), (BLUE_400, None), (BLUE_700, None), (INK_700, None), "#FFFFFF", TEXT_500),
        "Danger.TButton": ((DANGER_BG, "#7A2E40"), ("#4A1C2B", DANGER), ("#2A1018", DANGER), (INK_850, INK_700), DANGER,
                           TEXT_500),
        "Tile.TButton": ((INK_850, INK_700), (INK_800, BLUE_500), (INK_850, BLUE_400), (INK_850, INK_700), TEXT_100,
                         TEXT_500),
    }
    for name, (normal, hover, pressed, disabled, fg, fg_off) in variants.items():
        imgs = [image(root, f"btn:{name}:{k}", lambda sc, fb=fb: _art.frame_image(fb[0], fb[1], r, sc))
                for k, fb in enumerate((normal, hover, pressed, disabled))]
        el = name.replace(".TButton", "").replace("TButton", "Base") + ".abc.border"
        if el not in st.element_names():
            st.element_create(el, "image", imgs[0], ("disabled", imgs[3]), ("pressed", imgs[2]), ("active", imgs[1]),
                              border=round((r + 2) * s), sticky="nsew")
        st.layout(name, [(el, {"sticky": "nsew", "children": [
            ("Button.padding", {"sticky": "nsew", "children": [("Button.label", {"sticky": "nsew"})]})]})])
        tile = name == "Tile.TButton"
        st.configure(name, foreground=fg, background=INK_900, font="AbcButton", anchor="w" if tile else "center",
                     padding=(round(16 * s), round(12 * s)) if tile else (round(14 * s), round(6 * s)))
        st.map(name, foreground=[("disabled", fg_off)], background=[("active", INK_900)])
    st.layout("Link.TButton", [("Button.padding", {"sticky": "nsew", "children": [("Button.label", {"sticky": "nsew"})]})])
    st.configure("Link.TButton", background=INK_900, foreground=SKY_300, font="AbcButton", borderwidth=0, relief="flat",
                 padding=(round(4 * s), round(4 * s)), focuscolor=INK_900, lightcolor=INK_900, darkcolor=INK_900,
                 bordercolor=INK_900)
    st.map("Link.TButton", foreground=[("disabled", TEXT_500), ("active", SKY_200)], background=[("active", INK_900),
                                                                                                   ("pressed", INK_900)])


# ---------------------------------------------------------------- header vector art
def header(win: tk.Toplevel, title: str, subtitle: str = "ABC Fashion", tall: bool = False) -> tk.Canvas:
    """Đầu cửa sổ: logo + tiêu đề trên nền dải lụa (uiux-design.md 6.1, 7.2). Tranh neo phải, tiêu đề bên trái."""
    h, art_w = (132, 640) if tall else (64, 760)
    cnv = tk.Canvas(win, height=px(win, h), width=1, background=INK_950, highlightthickness=0, borderwidth=0)
    art = image(win, f"hero:{art_w}" if tall else f"banner:{art_w}",
                (lambda s: _art.hero(art_w, h, s)) if tall else (lambda s: _art.banner(art_w, h, s)))
    item = cnv.create_image(0, 0, image=art, anchor="ne")
    cnv.bind("<Configure>", lambda e: cnv.coords(item, e.width, 0))
    x = px(win, 24 if tall else 16)
    if tall:
        cnv.create_text(x, px(win, 52), text=title, anchor="w", fill=TEXT_100, font="AbcDisplay")
        cnv.create_text(x, px(win, 92), text=subtitle, anchor="w", fill=SKY_300, font="AbcButton")
    else:
        lg = image(win, "logo:36", lambda s: _art.logo(36, s))
        cnv.create_image(x, px(win, h / 2), image=lg, anchor="w")
        tx = x + px(win, 48)
        cnv.create_text(tx, px(win, 24), text=title, anchor="w", fill=TEXT_100, font="AbcH1")
        cnv.create_text(tx, px(win, 46), text=subtitle, anchor="w", fill=TEXT_300, font="AbcSmall")
    cnv.pack(side="top", fill="x")
    return cnv


# ---------------------------------------------------------------- phân loại nút sau khi màn hình dựng xong
def classify(text: str) -> str | None:
    t = (text or "").strip()
    if t.startswith(LINK_WORDS):
        return "Link.TButton"
    if t.startswith(DANGER_WORDS):
        return "Danger.TButton"
    if t.startswith(PRIMARY_WORDS) and not t.startswith("Tìm bằng"):
        return "Primary.TButton"
    return None


def polish(win: tk.Misc) -> None:
    """Gắn style cho nút chưa có style theo chữ trên nút; con trỏ bàn tay cho mọi nút."""
    try:
        if not win.winfo_exists():
            return
        stack = list(win.winfo_children())
    except tk.TclError:
        return
    while stack:
        w = stack.pop()
        stack.extend(w.winfo_children())
        if isinstance(w, ttk.Button):
            try:
                if not str(w.cget("style")):
                    style = classify(str(w.cget("text")))
                    if style:
                        w.configure(style=style)
                w.configure(cursor="hand2")
            except tk.TclError:
                pass
