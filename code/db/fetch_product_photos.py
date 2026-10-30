"""Tải ảnh sản phẩm miễn phí bản quyền (Unsplash License) về code/media/products/ và đổi tblProductMedia.url
sang đường dẫn cục bộ. Ghi nguồn từng ảnh vào code/MEDIA_CREDITS.md.

    python db/fetch_product_photos.py                      # dùng ABC_FASHION_DSN
    python db/fetch_product_photos.py --dsn "dbname=... "  # CSDL khác
    python db/fetch_product_photos.py --no-db              # chỉ tải ảnh + ghi nguồn

Chỉ cập nhật dòng ảnh đầu tiên (`sort_order` nhỏ nhất, `media_type = image`) của mỗi style; dòng video và các
style không có trong bảng PHOTOS được giữ nguyên. Sau khi chạy, nên chạy `setup_db.py --index` để chỉ mục tìm
kiếm ảnh dùng màu thật của ảnh mới.
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import urllib.request

import psycopg
from PIL import Image

for _s in (sys.stdout, sys.stderr):          # console Windows mặc định cp1252 không in được tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DSN = os.environ.get("ABC_FASHION_DSN", "dbname=abc_fashion_v2 user=postgres host=localhost port=5432")
UA = {"User-Agent": "ABCFashionStudentProject/1.0 (course project)"}
LICENSE = "Unsplash License (https://unsplash.com/license) — miễn phí cho mục đích thương mại, không bắt buộc ghi nguồn"

# mã style → (photo id trên images.unsplash.com, trang gốc, tác giả, mô tả)
PHOTOS = {
    "SH-LIN-01": ("photo-1713881587420-113c1c43e28a", "https://unsplash.com/photos/a-white-shirt-hanging-on-a-clothes-line-S4f4apZd-hA",
                  "tian dayong (@tonnnyj)", "Áo linen cổ trụ trên móc gỗ"),
    "JN-SLM-02": ("photo-1714143136372-ddaf8b606da7", "https://unsplash.com/photos/a-pair-of-blue-jeans-on-a-white-background-9yoXrG6Er_g",
                  "TuanAnh Blue (@blueeyeaa)", "Quần jeans xanh đậm gập phẳng"),
    "DR-MID-03": ("photo-1762154057377-cc9d3dd6900c", "https://unsplash.com/photos/cRpcTf0VfuE",
                  "Sanskrutihomes (@sanskrutihomes)", "Váy midi hoạ tiết hoa"),
    "TS-BAS-04": ("photo-1583743814966-8936f5b7be1a", "https://unsplash.com/photos/Wr0TpKqf26s",
                  "Faith & Yarn (@faithandyarn_)", "Áo thun đen cổ tròn trên móc"),
}


def download(photo_id: str, width: int = 800) -> Image.Image:
    url = f"https://images.unsplash.com/{photo_id}?fm=jpg&q=85&w={width}&fit=max"
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
    return Image.open(io.BytesIO(data)).convert("RGB")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dsn", default=DEFAULT_DSN)
    ap.add_argument("--no-db", action="store_true")
    args = ap.parse_args()
    out_dir = os.path.join(CODE_DIR, "media", "products")
    os.makedirs(out_dir, exist_ok=True)
    rel = {}
    for code, (pid, page, author, desc) in PHOTOS.items():
        im = download(pid)
        name = code.lower() + ".jpg"
        im.save(os.path.join(out_dir, name), quality=85)
        rel[code] = f"media/products/{name}"
        print(f"{code}: {im.size[0]}x{im.size[1]} → {rel[code]}")
    lines = ["# Nguồn ảnh sản phẩm", "", f"Giấy phép chung: {LICENSE}.", "",
             "| Mã style | Ảnh | Tác giả | Trang gốc |", "|---|---|---|---|"]
    lines += [f"| {c} | {desc} | {a} | {p} |" for c, (_, p, a, desc) in PHOTOS.items()]
    with open(os.path.join(CODE_DIR, "MEDIA_CREDITS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    if args.no_db:
        return 0
    with psycopg.connect(args.dsn) as con:
        with con.transaction():
            for code, url in rel.items():
                row = con.execute(
                    'SELECT m."id" FROM "tblProductMedia" m JOIN "tblStyle" s ON s."id" = m."styleId" '
                    'WHERE s."code" = %s AND m."media_type" = \'image\' ORDER BY m."sort_order", m."id" LIMIT 1', (code,)).fetchone()
                if row is None:
                    print(f"{code}: không có dòng ảnh trong tblProductMedia — bỏ qua")
                    continue
                con.execute('UPDATE "tblProductMedia" SET "url" = %s WHERE "id" = %s', (url, row[0]))
                print(f"{code}: tblProductMedia#{row[0]} → {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
