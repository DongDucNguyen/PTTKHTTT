"""Xuất các phần tử đồ hoạ của giao diện (uiux-design.md mục 5) ra media/ui/ ở độ phân giải 2× để xem / đưa vào báo cáo.

Ứng dụng tự vẽ lại các phần tử này theo DPI thật khi chạy (view/_art.py), nên file ở đây chỉ để tham khảo.
Chạy:  cd code && python make_ui_assets.py
"""
from __future__ import annotations

import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abc_fashion.view import _art  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media", "ui")
SCALE = 2.0


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(OUT, "icons"), exist_ok=True)
    items = {"logo.png": _art.logo(64, SCALE), "banner.png": _art.banner(1200, 64, SCALE),
             "hero_banner.png": _art.hero(900, 132, SCALE), "login_art.png": _art.login_art(360, 460, SCALE)}
    for name, img in items.items():
        img.save(os.path.join(OUT, name))
    icons = [(n, _art.icon(n, 24, SCALE)) for n in _art.ICONS]
    for n, img in icons:
        img.save(os.path.join(OUT, "icons", n + ".png"))
    sheet = Image.new("RGBA", (len(icons) * 64 + 16, 80), _art.rgb(_art.INK_900))     # bảng xem nhanh biểu tượng
    for k, (_, img) in enumerate(icons):
        sheet.alpha_composite(img, (16 + k * 64, 16))
    sheet.save(os.path.join(OUT, "icons_sheet.png"))
    print(f"Đã xuất {len(items) + len(icons) + 1} file vào {OUT}")


if __name__ == "__main__":
    main()
