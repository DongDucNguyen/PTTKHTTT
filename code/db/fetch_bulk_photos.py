"""Tải ảnh thật (Unsplash License, miễn phí) cho các sản phẩm do `generate_sample_products.py` sinh ra —
thay khung màu bằng ảnh thật, mỗi sản phẩm một ảnh tương ứng.

    python db/fetch_bulk_photos.py                      # dùng ABC_FASHION_DSN
    python db/fetch_bulk_photos.py --dsn "dbname=... "

Chỉ cập nhật dòng `tblProductMedia` có `url` dạng `media/products/<mã>.png` (khung màu do
`generate_sample_products.py` + `setup_db.py --index` sinh ra) — không đụng 4 ảnh thật gốc của báo cáo
(`.jpg`). Mỗi danh mục (Shirts/Jeans/Dresses/Tops) có một bộ ảnh thật được chọn tay (POOLS dưới đây), gán
xoay vòng cho các sản phẩm cùng danh mục theo thứ tự id — ảnh dùng lại giữa nhiều sản phẩm cùng danh mục vì
không đủ ảnh miễn phí phù hợp riêng cho từng tên sản phẩm; mọi ảnh đều Unsplash License (miễn phí, không cần
ghi nguồn, nhưng vẫn ghi vào MEDIA_CREDITS.md theo quy ước của dự án). File khung màu cũ không còn được
tham chiếu nhưng không bị xoá (vô hại, có thể dọn tay sau).
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import urllib.request

import psycopg
from PIL import Image

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DSN = os.environ.get("ABC_FASHION_DSN", "dbname=abc_fashion_v2 user=postgres host=localhost port=5432")
UA = {"User-Agent": "ABCFashionStudentProject/1.0 (course project)"}
CREDITS_PATH = os.path.join(CODE_DIR, "MEDIA_CREDITS.md")

CATEGORY_NAME_CANDIDATES = {
    "Shirts": ["Shirts", "Áo nam"],
    "Jeans": ["Jeans", "Quần nam"],
    "Dresses": ["Dresses", "Váy"],
    "Tops": ["Tops", "Áo nữ"],
}

# mỗi mục: (photo id trên images.unsplash.com, tác giả (@handle), trang gốc, mô tả tiếng Việt)
POOLS: dict[str, list[tuple[str, str, str, str]]] = {
    "Shirts": [
        ("photo-1564859228273-274232fdb516", "Sincerely Media (@sincerelymedia)",
         "https://unsplash.com/photos/mens-white-crew-neck-shirt-9ShY-Tq70Mc", "Áo sơ mi trắng cổ tròn nam"),
        ("photo-1716951984700-64ea15a06f13", "TuanAnh Blue (@blueeyeaa)",
         "https://unsplash.com/photos/a-close-up-of-a-shirt-on-a-white-surface-h3pWzS3MWkI",
         "Cận cảnh áo sơ mi gấp trên mặt bàn trắng"),
        ("photo-1565503117139-7fd9677544e9", "Nitin Mendekar (@nitin_mendekar)",
         "https://unsplash.com/photos/mens-gray-striped-collared-shirt-FD59Y8viCyU", "Áo sơ mi kẻ sọc xám nam"),
        ("photo-1603252109612-24fa03d145c8", "Nimble Made (@nimblemade)",
         "https://unsplash.com/photos/man-in-white-button-up-shirt-GDebkNryTd4", "Người mặc áo sơ mi trắng cài nút"),
        ("photo-1441035844538-e2ce7dba066b", "Angelina Litvin (@linalitvina)",
         "https://unsplash.com/photos/flat-lay-photography-of-button-up-shirt-camera-keys-cigarettes-and-pair-of-brown-leather-boat-shoes-YL7Y9uZ5O98",
         "Bố cục áo sơ mi cài nút cùng phụ kiện"),
        ("photo-1737748612418-e39bcd6503a2", "Bernd Dittrich (@hdbernd)",
         "https://unsplash.com/photos/a-bunch-of-shirts-are-hanging-on-a-rack-94Tvp4AhlUU",
         "Dãy áo sơ mi nhiều màu treo trên móc"),
        ("photo-1416339698674-4f118dd3388b", "Jeff Sheldon (@ugmonk)",
         "https://unsplash.com/photos/assorted-color-hanged-shirts-with-hangers-Lj1S1_KD61k",
         "Áo sơ mi nhiều màu treo trên móc gỗ"),
    ],
    "Jeans": [
        ("photo-1624378440847-4a64ee1a889d", "Matthew Moloney (@mattmoloney)",
         "https://unsplash.com/photos/blue-denim-jeans-on-white-textile-ytQeX4iQ7Uk",
         "Quần jeans xanh đặt trên nền vải trắng"),
        ("photo-1578798221387-80d19283bd4d", "Joshua Gandara (@joshgand)",
         "https://unsplash.com/photos/womens-blue-denim-jeans-xxn48oa73sM", "Quần jeans denim xanh"),
        ("photo-1583126664259-a6a52fd1855d", "Morgan Lane (@themorganlane)",
         "https://unsplash.com/photos/person-in-blue-denim-jeans-and-white-sneakers-standing-on-gray-concrete-floor-bEmaNARq2iw",
         "Người mặc quần jeans xanh và giày sneaker trắng"),
        ("photo-1599428021675-90f8f8dbc377", "Vlah Dumitru (@vlahdumitru)",
         "https://unsplash.com/photos/woman-in-black-tank-top-and-blue-denim-jeans-wearing-sunglasses-standing-on-road-during-daytime-PzQOXn2AJjg",
         "Người mặc quần jeans xanh, áo sát nách đen"),
        ("photo-1616003471864-9abfeee24576", "Henry Tuchez (@henrytuchez)",
         "https://unsplash.com/photos/woman-in-black-long-sleeve-shirt-and-blue-denim-jeans-standing-on-green-grass-field-during-Ve49Nc0EoDA",
         "Người mặc quần jeans xanh trên bãi cỏ"),
    ],
    "Dresses": [
        ("photo-1571924848943-25c2c95bbb4b", "Yogendra Singh (@yogendras31)",
         "https://unsplash.com/photos/womens-white-sleeveless-dress-_c56tTiztfA", "Đầm trắng không tay nữ"),
        ("photo-1550951195-2cbd9ca5e0d5", "Catalin Apostol (@catlyn05)",
         "https://unsplash.com/photos/assorted-color-dress-hanged-on-brown-hangers-N2CiCNWba-Y",
         "Nhiều đầm màu sắc treo trên móc gỗ"),
        ("photo-1589136371962-abcdf83feb57", "Anthony Ievlev (@onmywayhome)",
         "https://unsplash.com/photos/woman-in-orange-and-blue-floral-dress-standing-on-yellow-flower-field-during-daytime-hmHThiqDaBk",
         "Người mặc đầm hoạ tiết hoa cam xanh"),
        ("photo-1602058746258-e012b1c1197c", "Abraham Eli (@abrahamrayeli)",
         "https://unsplash.com/photos/woman-in-white-floral-dress-leaning-on-wall-1CDf5OKfDSM",
         "Người mặc đầm hoạ tiết hoa trắng"),
        ("photo-1564263306152-5e1207dbd0ad", "Naganath Chiluveru (@naganath)",
         "https://unsplash.com/photos/woman-wearing-red-dress-ggnMQYNytXc", "Người mặc đầm đỏ"),
    ],
    "Tops": [
        ("photo-1510074229140-bdfc2ff28550", "Gardie Design & Social Media Marketing (@gardiept)",
         "https://unsplash.com/photos/woman-wearing-white-long-sleeved-blouse-i2jbuqO0YfM",
         "Người mặc áo cổ cao trắng dài tay"),
        ("photo-1567849840003-3883199f7efa", "Napat Saeng (@napats)",
         "https://unsplash.com/photos/woman-in-white-top-and-red-2-piece-suit-1w7Z_BzML2Y", "Người mặc áo trắng"),
        ("photo-1758537698215-af1e35acb911", "Adrien Olichon (@adrienolichon)",
         "https://unsplash.com/photos/colorful-folded-knit-sweaters-with-cable-patterns-displayed-JSyMOOsk0K8",
         "Áo len dệt kim gấp nhiều màu"),
        ("photo-1484342878342-14169ec7e3af", "Maxx Miller (@_maxxmiller)",
         "https://unsplash.com/photos/photo-of-woman-wearing-white-off-shoulder-crop-top-standing-beside-concrete-building-under-clear-blue-sky-fjwBfnHYNBM",
         "Người mặc áo croptop trắng trễ vai"),
        ("photo-1599817878414-43ef36677cf0", "El S (@evucrn)",
         "https://unsplash.com/photos/woman-in-white-tank-top-gUPznplBsLI", "Người mặc áo ba lỗ trắng"),
        ("photo-1602414225466-f4bd3fe7ced0", "Alex Shaw (@matt909)",
         "https://unsplash.com/photos/woman-in-black-and-white-tank-top-WPFirDXYDKM",
         "Người mặc áo ba lỗ đen trắng"),
    ],
}


def download(photo_id: str, width: int = 800) -> Image.Image:
    url = f"https://images.unsplash.com/{photo_id}?fm=jpg&q=85&w={width}&fit=max"
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
    return Image.open(io.BytesIO(data)).convert("RGB")


def fetch_pool_images(out_dir: str) -> dict[str, dict[str, str]]:
    """Tải (nếu chưa có) mỗi ảnh trong POOLS; trả `{danh_mục: {photo_id: đường_dẫn_tương_đối}}`."""
    os.makedirs(out_dir, exist_ok=True)
    rel: dict[str, dict[str, str]] = {}
    for category, items in POOLS.items():
        rel[category] = {}
        for photo_id, author, _url, _desc in items:
            slug = re.sub(r"[^a-z0-9]+", "-", photo_id.lower()).strip("-")
            filename = f"stock-{category.lower()}-{slug}.jpg"
            path = os.path.join(out_dir, filename)
            rel_path = f"media/products/{filename}"
            if not os.path.exists(path):
                print(f"Đang tải {photo_id} ({author}) cho {category}…")
                download(photo_id).save(path, quality=88)
            rel[category][photo_id] = rel_path
    return rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dsn", default=DEFAULT_DSN)
    args = ap.parse_args()

    out_dir = os.path.join(CODE_DIR, "media", "products")
    rel_paths = fetch_pool_images(out_dir)

    con = psycopg.connect(args.dsn, autocommit=True, row_factory=psycopg.rows.dict_row)
    by_name = {r["name"]: r["id"] for r in con.execute('SELECT "id","name" FROM "tblCategory"').fetchall()}
    cat_id_to_key = {}
    for key, candidates in CATEGORY_NAME_CANDIDATES.items():
        found = next((by_name[c] for c in candidates if c in by_name), None)
        if found is not None:
            cat_id_to_key[found] = key

    rows = con.execute(
        'SELECT m."id" AS "mediaId", s."id" AS "styleId", s."code", s."categoryId" '
        'FROM "tblProductMedia" m JOIN "tblStyle" s ON s."id" = m."styleId" '
        'WHERE m."url" LIKE \'media/products/%.png\' ORDER BY s."id"').fetchall()
    if not rows:
        print("Không có sản phẩm nào đang dùng ảnh khung màu (media/products/*.png) — không có gì để thay.")
        return 0

    counters = {k: 0 for k in POOLS}
    credit_rows = []
    for r in rows:
        key = cat_id_to_key.get(r["categoryId"])
        if key is None:
            print(f"  ✗ {r['code']}: danh mục không khớp Shirts/Jeans/Dresses/Tops, bỏ qua")
            continue
        photo_id, author, url, desc = POOLS[key][counters[key] % len(POOLS[key])]
        counters[key] += 1
        new_url = rel_paths[key][photo_id]
        con.execute('UPDATE "tblProductMedia" SET "url" = %s WHERE "id" = %s', (new_url, r["mediaId"]))
        credit_rows.append((r["code"], desc, author, url))

    with open(CREDITS_PATH, encoding="utf-8") as f:
        text = f.read()
    marker = "\n# Font giao diện"
    new_lines = "\n".join(f"| {code} | {desc} | {author} | {url} |" for code, desc, author, url in credit_rows)
    text = text.replace(marker, "\n" + new_lines + "\n" + marker, 1)
    with open(CREDITS_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Đã cập nhật {len(credit_rows)} ảnh sản phẩm sang ảnh thật (Unsplash License) và ghi nguồn vào "
          f"{os.path.basename(CREDITS_PATH)}.")
    print("Chạy tiếp để cập nhật chỉ mục tìm kiếm theo màu ảnh thật:")
    print(f'  ..\\.venv\\Scripts\\python.exe db\\setup_db.py --dsn "{args.dsn}" --index')
    return 0


if __name__ == "__main__":
    sys.exit(main())
