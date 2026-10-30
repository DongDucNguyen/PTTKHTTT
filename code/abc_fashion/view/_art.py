"""Phần tử đồ hoạ vector của giao diện (uiux-design.md mục 5), vẽ bằng Pillow.

Mọi hình vẽ ở độ phân giải gấp SS lần rồi thu nhỏ để khử răng cưa. Hàm nhận kích thước *logic* (px ở 100%) và
`scale` (hệ số DPI) và trả ảnh RGBA. Không chạm tkinter: `_theme.py` đổi sang PhotoImage, `make_ui_assets.py` xuất PNG.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

SS = 4                                          # hệ số vẽ phóng to (supersampling)

# token màu (uiux-design.md mục 2) — _theme.py dùng lại
INK_950, INK_900, INK_850, INK_800, INK_700, INK_600 = "#060A13", "#0A1120", "#0E182B", "#132038", "#1B2C4B", "#27406A"
BLUE_700, BLUE_600, BLUE_500, BLUE_400 = "#173E9E", "#1F4FD1", "#2F6BFF", "#5B8CFF"
SKY_300, SKY_200, CYAN_400 = "#8CC1FF", "#BCD9FF", "#36C2F0"
TEXT_100, TEXT_300, TEXT_500 = "#E6EEFC", "#A3B4D1", "#6E81A3"


def rgb(hex_: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha


def mix(a: str, b: str, t: float) -> str:
    ca, cb = rgb(a), rgb(b)
    return "#" + "".join(f"{round(ca[i] + (cb[i] - ca[i]) * t):02x}" for i in range(3))


def _px(v: float, scale: float) -> int:
    return max(1, round(v * scale))


def _finish(big: Image.Image, size: tuple[int, int]) -> Image.Image:
    return big.resize(size, Image.LANCZOS)


def _gradient(size: tuple[int, int], top: str, bottom: str, horizontal: bool = False, alpha=(255, 255)) -> Image.Image:
    """Ảnh dải màu tuyến tính (dọc mặc định)."""
    w, h = size
    n = w if horizontal else h
    line = Image.new("RGBA", (n, 1))
    ca, cb = rgb(top, alpha[0]), rgb(bottom, alpha[1])
    line.putdata([tuple(round(ca[k] + (cb[k] - ca[k]) * i / max(1, n - 1)) for k in range(4)) for i in range(n)])
    if horizontal:
        return line.resize((w, h), Image.NEAREST)
    return line.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT).resize((w, h), Image.NEAREST)


def _paint(img: Image.Image, mask: Image.Image, fill: Image.Image | str, opacity: float = 1.0) -> None:
    """Tô `fill` (màu hoặc ảnh dải màu) lên `img` theo `mask` (L)."""
    layer = fill if isinstance(fill, Image.Image) else Image.new("RGBA", img.size, rgb(fill))
    a = ImageChops.multiply(layer.getchannel("A"), mask)
    if opacity < 1:
        a = a.point(lambda v: round(v * opacity))
    layer = layer.copy()
    layer.putalpha(a)
    img.alpha_composite(layer)


def _wave_band(size, y0: float, amp: float, thick: float, freq: float, phase: float) -> Image.Image:
    """Mặt nạ một dải lụa lượn sóng chạy ngang ảnh."""
    w, h = size
    steps = 160
    top, bottom = [], []
    for i in range(steps + 1):
        x = w * i / steps
        t = i / steps
        y = y0 + amp * math.sin(2 * math.pi * freq * t + phase)
        th = thick * (0.55 + 0.45 * math.sin(math.pi * t + phase / 2) ** 2)
        top.append((x, y))
        bottom.append((x, y + th))
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon(top + bottom[::-1], fill=255)
    return m


def _stitch(d: ImageDraw.ImageDraw, size, y0, amp, freq, phase, colour, width, dash, gap) -> None:
    """Đường chỉ may nét đứt theo một đường sóng."""
    w, _ = size
    pts = [(w * i / 400, y0 + amp * math.sin(2 * math.pi * freq * i / 400 + phase)) for i in range(401)]
    run, on, seg = 0.0, True, [pts[0]]
    for a, b in zip(pts, pts[1:]):
        run += math.dist(a, b)
        seg.append(b)
        if run >= (dash if on else gap):
            if on and len(seg) > 1:
                d.line(seg, fill=colour, width=width)
            on, run, seg = not on, 0.0, [b]


def _sparkles(d: ImageDraw.ImageDraw, size, n: int, seed: int, r_max: float, region=(0.0, 1.0)) -> None:
    rnd = random.Random(seed)
    w, h = size
    for _ in range(n):
        x = w * (region[0] + (region[1] - region[0]) * rnd.random())
        y = h * rnd.random()
        r = r_max * (0.3 + 0.7 * rnd.random())
        d.ellipse((x - r, y - r, x + r, y + r), fill=rgb(rnd.choice([CYAN_400, SKY_300, SKY_200]), rnd.randint(90, 220)))


def _fade_left(img: Image.Image, start: float, end: float) -> Image.Image:
    """Mặt nạ trong suốt dần về bên trái (để chữ tiêu đề đọc rõ)."""
    w, h = img.size
    ramp = Image.new("L", (w, 1))
    def smooth(x: int) -> int:                  # smoothstep: không thấy "mép" ở chỗ bắt đầu mờ dần
        t = min(1.0, max(0.0, (x - w * start) / (w * (end - start))))
        return round(255 * t * t * (3 - 2 * t))
    ramp.putdata([smooth(x) for x in range(w)])
    return ImageChops.multiply(img.getchannel("A"), ramp.resize((w, h)))


# ---------------------------------------------------------------- dải lụa (header, hero)
def silk(size: tuple[int, int], scale: float = 1.0, seed: int = 7, fade=(0.28, 0.72), moon: bool = False) -> Image.Image:
    """Nền `ink-950` với các dải lụa xanh chồng lớp ở bên phải, đường chỉ, chấm sáng."""
    w, h = _px(size[0], scale) * SS, _px(size[1], scale) * SS
    big = (w, h)
    art = Image.new("RGBA", big, (0, 0, 0, 0))
    if moon:
        r = h * 0.62
        cx, cy = w * 0.83, h * 0.30
        m = Image.new("L", big, 0)
        ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
        _paint(art, m, _gradient(big, SKY_300, BLUE_600), 0.22)
        m2 = Image.new("L", big, 0)
        ImageDraw.Draw(m2).ellipse((cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), fill=255)
        _paint(art, m2, _gradient(big, SKY_200, BLUE_500), 0.18)
    bands = [  # y0, biên độ, độ dày, tần số, pha, màu trên, màu dưới, độ đục
        (0.10, 0.16, 0.42, 0.9, 0.6, BLUE_700, INK_700, 0.85),
        (0.34, 0.14, 0.40, 1.1, 2.2, BLUE_600, BLUE_700, 0.80),
        (0.55, 0.12, 0.36, 0.8, 4.1, BLUE_500, BLUE_600, 0.70),
        (0.74, 0.10, 0.34, 1.3, 1.4, BLUE_400, BLUE_500, 0.55),
    ]
    for y0, amp, th, fq, ph, c1, c2, op in bands:
        mask = _wave_band(big, h * y0, h * amp, h * th, fq, ph + seed)
        _paint(art, mask, _gradient(big, c1, c2, horizontal=True), op)
    d = ImageDraw.Draw(art)
    _stitch(d, big, h * 0.50, h * 0.13, 1.0, 3.0 + seed, rgb(CYAN_400, 170), max(SS, round(SS * scale)), 6 * SS * scale,
            5 * SS * scale)
    _sparkles(d, big, 18 if h > 100 * SS else 10, seed, 1.6 * SS * scale, (0.45, 1.0))
    art.putalpha(_fade_left(art, *fade))
    out = Image.new("RGBA", big, rgb(INK_950))
    glow = _gradient(big, INK_950, mix(INK_950, BLUE_700, 0.35), horizontal=True)
    out.alpha_composite(glow)
    out.alpha_composite(art)
    return _finish(out, (big[0] // SS, big[1] // SS))


def banner(width: int = 1600, height: int = 64, scale: float = 1.0) -> Image.Image:
    return silk((width, height), scale, seed=3, fade=(0.20, 0.85))


def hero(width: int = 900, height: int = 132, scale: float = 1.0) -> Image.Image:
    return silk((width, height), scale, seed=11, fade=(0.15, 0.75), moon=True)


# ---------------------------------------------------------------- logo
def _hanger(d: ImageDraw.ImageDraw, cx, top, wid, hgt, colour, width) -> None:
    """Móc treo áo: móc cong + vai tam giác + thanh ngang."""
    r = wid * 0.09
    d.arc((cx - r, top, cx + r, top + 2 * r), 180, 90, fill=colour, width=width)
    neck = (cx, top + 2 * r + hgt * 0.12)
    d.line([(cx, top + 2 * r), neck], fill=colour, width=width)
    left, right = (cx - wid / 2, top + hgt), (cx + wid / 2, top + hgt)
    d.line([neck, left, right, neck], fill=colour, width=width, joint="curve")
    for p in (left, right, neck):
        d.ellipse((p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2), fill=colour)


def logo(size: int = 40, scale: float = 1.0) -> Image.Image:
    s = _px(size, scale) * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), radius=s * 0.26, fill=255)
    _paint(img, m, _gradient((s, s), BLUE_400, BLUE_700))
    d = ImageDraw.Draw(img)
    _hanger(d, s * 0.5, s * 0.20, s * 0.66, s * 0.50, rgb("#FFFFFF"), max(2, round(s * 0.075)))
    r = s * 0.07
    d.ellipse((s * 0.74 - r, s * 0.22 - r, s * 0.74 + r, s * 0.22 + r), fill=rgb(CYAN_400))
    return _finish(img, (s // SS, s // SS))


# ---------------------------------------------------------------- tranh màn hình đăng nhập
def login_art(width: int = 360, height: int = 460, scale: float = 1.0) -> Image.Image:
    w, h = _px(width, scale) * SS, _px(height, scale) * SS
    big = (w, h)
    img = _gradient(big, INK_950, mix(INK_900, BLUE_700, 0.25))
    d = ImageDraw.Draw(img)
    _sparkles(d, big, 34, 5, 2.0 * SS * scale)
    # mặt trăng hai lớp
    for k, (c1, c2, op) in enumerate(((SKY_300, BLUE_600, 0.20), (SKY_200, BLUE_500, 0.22))):
        r = w * (0.30 - 0.09 * k)
        cx, cy = w * 0.70, h * 0.20
        m = Image.new("L", big, 0)
        ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
        _paint(img, m, _gradient(big, c1, c2), op)
    # dải lụa phía dưới
    for y0, amp, th, fq, ph, c1, c2, op in ((0.70, 0.04, 0.16, 0.8, 0.4, BLUE_700, INK_700, 0.9),
                                            (0.78, 0.035, 0.14, 1.1, 2.0, BLUE_600, BLUE_700, 0.85),
                                            (0.86, 0.03, 0.16, 0.9, 3.6, BLUE_500, BLUE_600, 0.75)):
        _paint(img, _wave_band(big, h * y0, h * amp, h * th, fq, ph), _gradient(big, c1, c2, horizontal=True), op)
    d = ImageDraw.Draw(img)
    _stitch(d, big, h * 0.80, h * 0.025, 1.2, 1.0, rgb(CYAN_400, 190), round(1.6 * SS * scale), 7 * SS * scale,
            5 * SS * scale)
    # giá treo
    lw = round(3 * SS * scale)
    bar_y, x0, x1 = h * 0.36, w * 0.12, w * 0.88
    d.line([(x0, bar_y), (x1, bar_y)], fill=rgb(SKY_300), width=lw)
    d.line([(x0 + lw, bar_y), (x0 - w * 0.04, h * 0.74)], fill=rgb(SKY_300, 200), width=lw)
    d.line([(x1 - lw, bar_y), (x1 + w * 0.04, h * 0.74)], fill=rgb(SKY_300, 200), width=lw)
    garments = [(0.27, _shirt, (BLUE_400, BLUE_600)), (0.50, _dress, (SKY_300, BLUE_500)), (0.73, _tee, (BLUE_500, BLUE_700))]
    for fx, draw, colours in garments:
        cx = w * fx
        _hanger(d, cx, bar_y - h * 0.035, w * 0.17, h * 0.06, rgb(SKY_200), round(2 * SS * scale))
        draw(img, cx, bar_y + h * 0.03, w * 0.20, h * 0.27, colours)
    # túi mua sắm
    bx, by, bw, bh = w * 0.08, h * 0.60, w * 0.19, h * 0.17
    m = Image.new("L", big, 0)
    ImageDraw.Draw(m).rounded_rectangle((bx, by, bx + bw, by + bh), radius=bw * 0.08, fill=255)
    _paint(img, m, _gradient(big, CYAN_400, BLUE_600))
    d = ImageDraw.Draw(img)
    d.arc((bx + bw * 0.25, by - bh * 0.30, bx + bw * 0.75, by + bh * 0.30), 180, 360, fill=rgb(SKY_200), width=lw)
    return _finish(img, (w // SS, h // SS))


def _garment(img, poly, colours, seams=()) -> None:
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(0.6 * SS))
    _paint(img, m, _gradient(img.size, *colours))
    d = ImageDraw.Draw(img)
    for seg in seams:
        d.line(seg, fill=rgb(INK_950, 110), width=SS * 2)


def _shirt(img, cx, top, wid, hgt, colours) -> None:
    s = wid / 2
    poly = [(cx - s * 0.35, top), (cx - s, top + hgt * 0.10), (cx - s * 1.1, top + hgt * 0.42), (cx - s * 0.78, top + hgt * 0.45),
            (cx - s * 0.70, top + hgt), (cx + s * 0.70, top + hgt), (cx + s * 0.78, top + hgt * 0.45),
            (cx + s * 1.1, top + hgt * 0.42), (cx + s, top + hgt * 0.10), (cx + s * 0.35, top), (cx, top + hgt * 0.14)]
    _garment(img, poly, colours, [[(cx, top + hgt * 0.14), (cx, top + hgt)]])


def _dress(img, cx, top, wid, hgt, colours) -> None:
    s = wid / 2
    poly = [(cx - s * 0.30, top), (cx - s * 0.55, top + hgt * 0.38), (cx - s * 0.42, top + hgt * 0.45),
            (cx - s * 1.05, top + hgt * 1.08), (cx + s * 1.05, top + hgt * 1.08), (cx + s * 0.42, top + hgt * 0.45),
            (cx + s * 0.55, top + hgt * 0.38), (cx + s * 0.30, top), (cx, top + hgt * 0.10)]
    _garment(img, poly, colours, [[(cx - s * 0.45, top + hgt * 0.44), (cx + s * 0.45, top + hgt * 0.44)]])


def _tee(img, cx, top, wid, hgt, colours) -> None:
    s = wid / 2
    poly = [(cx - s * 0.32, top), (cx - s * 1.0, top + hgt * 0.12), (cx - s * 1.1, top + hgt * 0.30), (cx - s * 0.72, top + hgt * 0.32),
            (cx - s * 0.72, top + hgt * 0.92), (cx + s * 0.72, top + hgt * 0.92), (cx + s * 0.72, top + hgt * 0.32),
            (cx + s * 1.1, top + hgt * 0.30), (cx + s * 1.0, top + hgt * 0.12), (cx + s * 0.32, top)]
    _garment(img, poly, colours)
    d = ImageDraw.Draw(img)
    d.arc((cx - s * 0.32, top - hgt * 0.08, cx + s * 0.32, top + hgt * 0.10), 0, 180, fill=rgb(INK_950, 130), width=SS * 2)


# ---------------------------------------------------------------- biểu tượng nét (24 px)
def icon(name: str, size: int = 24, scale: float = 1.0, colour: str = SKY_300) -> Image.Image:
    s = _px(size, scale) * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = s / 24
    c = rgb(colour)
    lw = max(SS, round(2 * u))
    ICONS.get(name, _i_dot)(d, u, c, lw)
    return _finish(img, (s // SS, s // SS))


def _pl(d, pts, c, lw, u, close=False) -> None:
    """Đường gấp khúc nét tròn đầu (toạ độ theo lưới 24)."""
    p = [(x * u, y * u) for x, y in pts] + ([(pts[0][0] * u, pts[0][1] * u)] if close else [])
    d.line(p, fill=c, width=lw, joint="curve")
    for x, y in p:
        d.ellipse((x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2), fill=c)


def _rr(d, box, r, c, lw, u) -> None:
    d.rounded_rectangle([v * u for v in box], radius=r * u, outline=c, width=lw)


def _circ(d, cx, cy, r, c, lw, u, fill=False) -> None:
    box = ((cx - r) * u, (cy - r) * u, (cx + r) * u, (cy + r) * u)
    d.ellipse(box, fill=c) if fill else d.ellipse(box, outline=c, width=lw)


def _i_dot(d, u, c, lw):
    _circ(d, 12, 12, 3, c, lw, u, True)


def _i_catalogue(d, u, c, lw):
    for x, y in ((3, 3), (13, 3), (3, 13), (13, 13)):
        _rr(d, (x, y, x + 8, y + 8), 2, c, lw, u)


def _i_cart(d, u, c, lw):
    _pl(d, [(2, 4), (5, 4), (7.5, 15), (18, 15), (20.5, 7.5), (6.2, 7.5)], c, lw, u)
    _circ(d, 9, 19.5, 1.6, c, lw, u, True)
    _circ(d, 17, 19.5, 1.6, c, lw, u, True)


def _i_orders(d, u, c, lw):
    _pl(d, [(5, 2.5), (19, 2.5), (19, 21.5), (16.5, 20), (14, 21.5), (12, 20), (10, 21.5), (7.5, 20), (5, 21.5)], c, lw, u, True)
    for y in (8, 12, 16):
        _pl(d, [(8.5, y), (15.5, y)], c, lw, u)


def _i_profile(d, u, c, lw):
    _circ(d, 12, 8, 4, c, lw, u)
    d.arc((4 * u, 13 * u, 20 * u, 29 * u), 200, 340, fill=c, width=lw)


def _i_logout(d, u, c, lw):
    _pl(d, [(13, 3), (5, 3), (5, 21), (13, 21)], c, lw, u)
    _pl(d, [(10, 12), (21, 12)], c, lw, u)
    _pl(d, [(17, 8), (21, 12), (17, 16)], c, lw, u)


def _i_accounts(d, u, c, lw):
    _circ(d, 9, 8, 3.5, c, lw, u)
    d.arc((2 * u, 13 * u, 16 * u, 27 * u), 200, 340, fill=c, width=lw)
    _circ(d, 17, 7, 2.8, c, lw, u)
    d.arc((13 * u, 12 * u, 23 * u, 22 * u), 230, 340, fill=c, width=lw)


def _i_product(d, u, c, lw):
    _pl(d, [(8.5, 3), (3, 6), (4.5, 11), (7, 10), (7, 21), (17, 21), (17, 10), (19.5, 11), (21, 6), (15.5, 3),
            (14, 5), (10, 5)], c, lw, u, True)


def _i_review(d, u, c, lw):
    pts = []
    for k in range(10):
        r = 9.5 if k % 2 == 0 else 4.2
        a = math.pi / 2 + k * math.pi / 5
        pts.append((12 + r * math.cos(a), 12.8 - r * math.sin(a)))
    _pl(d, pts, c, lw, u, True)


def _i_audit(d, u, c, lw):
    _circ(d, 12, 12, 9, c, lw, u)
    _pl(d, [(12, 7), (12, 12), (15.5, 14.5)], c, lw, u)


def _i_order(d, u, c, lw):
    _pl(d, [(12, 2.5), (20.5, 7), (20.5, 17), (12, 21.5), (3.5, 17), (3.5, 7)], c, lw, u, True)
    _pl(d, [(3.5, 7), (12, 11.5), (20.5, 7)], c, lw, u)
    _pl(d, [(12, 11.5), (12, 21.5)], c, lw, u)


def _i_report(d, u, c, lw):
    _pl(d, [(3, 3), (3, 21), (21, 21)], c, lw, u)
    for x, top in ((8, 13), (13, 8), (18, 11)):
        d.rounded_rectangle(((x - 1.6) * u, top * u, (x + 1.6) * u, 18 * u), radius=u, fill=c)


def _i_promotion(d, u, c, lw):
    _pl(d, [(3, 3), (11, 3), (21, 13), (13, 21), (3, 11)], c, lw, u, True)
    _circ(d, 7.5, 7.5, 1.7, c, lw, u, True)


def _i_return(d, u, c, lw):
    _pl(d, [(8, 5), (4, 9), (8, 13)], c, lw, u)
    d.arc((8 * u, 9 * u, 20 * u, 21 * u), 270, 90, fill=c, width=lw)
    _pl(d, [(4, 9), (14, 9)], c, lw, u)
    _pl(d, [(14, 21), (8, 21)], c, lw, u)


def _i_inspect(d, u, c, lw):
    _rr(d, (4.5, 4, 19.5, 22), 2, c, lw, u)
    _rr(d, (8.5, 2, 15.5, 6), 1.5, c, lw, u)
    _pl(d, [(8, 14), (11, 17), (16.5, 11)], c, lw, u)


def _i_stock(d, u, c, lw):
    _rr(d, (3, 12, 11, 20), 1.5, c, lw, u)
    _rr(d, (13, 12, 21, 20), 1.5, c, lw, u)
    _rr(d, (8, 4, 16, 12), 1.5, c, lw, u)


def _i_restock(d, u, c, lw):
    _pl(d, [(2, 6), (14, 6), (14, 17), (2, 17)], c, lw, u, True)
    _pl(d, [(14, 9), (18.5, 9), (21.5, 13), (21.5, 17), (14, 17)], c, lw, u)
    _circ(d, 6.5, 18.5, 2, c, lw, u)
    _circ(d, 17.5, 18.5, 2, c, lw, u)


def _i_search(d, u, c, lw):
    _circ(d, 10.5, 10.5, 6.5, c, lw, u)
    _pl(d, [(15.5, 15.5), (21, 21)], c, lw, u)


def _i_camera(d, u, c, lw):
    _pl(d, [(3, 8), (7, 8), (9, 5), (15, 5), (17, 8), (21, 8), (21, 19), (3, 19)], c, lw, u, True)
    _circ(d, 12, 13, 3.6, c, lw, u)


def _i_image(d, u, c, lw):
    _rr(d, (3, 4, 21, 20), 2.5, c, lw, u)
    _circ(d, 8.5, 9.5, 1.8, c, lw, u)
    _pl(d, [(3.5, 18), (9, 13), (13, 16.5), (16, 13), (20.5, 17)], c, lw, u)


def _i_play(d, u, c, lw):
    d.polygon([(7 * u, 4.5 * u), (7 * u, 19.5 * u), (19.5 * u, 12 * u)], fill=c)


def _i_mic(d, u, c, lw):
    _rr(d, (9, 3, 15, 15), 3, c, lw, u)
    d.arc((5.5 * u, 6 * u, 18.5 * u, 18 * u), 0, 180, fill=c, width=lw)
    _pl(d, [(12, 18), (12, 21.5)], c, lw, u)


def _i_supplier(d, u, c, lw):
    _pl(d, [(3, 21), (3, 10), (9, 13), (9, 10), (15, 13), (15, 4), (20, 4), (20, 21)], c, lw, u, True)
    for x in (6, 12):
        _pl(d, [(x, 17), (x + 1.5, 17)], c, lw, u)


ICONS = {"catalogue": _i_catalogue, "cart": _i_cart, "orders": _i_orders, "profile": _i_profile, "logout": _i_logout,
         "accounts": _i_accounts, "product": _i_product, "review": _i_review, "audit": _i_audit, "order": _i_order,
         "report": _i_report, "promotion": _i_promotion, "return": _i_return, "inspect": _i_inspect, "stock": _i_stock,
         "restock": _i_restock, "search": _i_search, "camera": _i_camera, "image": _i_image, "play": _i_play, "mic": _i_mic, "supplier": _i_supplier}


# ---------------------------------------------------------------- ảnh 9 lát cho nút / ô nhập
def frame_image(fill: str, border: str | None, radius: float, scale: float = 1.0, size: int = 28,
                border_w: float = 1.0) -> Image.Image:
    """Hình chữ nhật bo góc dùng làm phần tử ttk (giãn theo `border` = radius + 2)."""
    s = _px(size, scale) * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw = round(border_w * scale * SS) if border else 0
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=radius * scale * SS, fill=rgb(fill),
                        outline=rgb(border) if border else None, width=bw)
    return _finish(img, (s // SS, s // SS))
