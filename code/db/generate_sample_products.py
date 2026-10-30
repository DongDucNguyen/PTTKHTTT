"""Sinh thêm sản phẩm mẫu (style + biến thể + vật liệu + bảng cỡ + ảnh + tồn kho) để có dữ liệu phong phú hơn
cho danh mục, không đụng tới 4 style gốc của báo cáo.

    python db/generate_sample_products.py                 # thêm 100 sản phẩm vào CSDL theo ABC_FASHION_DSN
    python db/generate_sample_products.py --count 50
    python db/generate_sample_products.py --dsn "dbname=abc_fashion_test user=postgres ..."

Dùng lại 2 nhà cung cấp, 2 bộ sưu tập, 2 kho và 4 danh mục lá (Shirts, Jeans, Dresses, Tops) đã có trong CSDL;
không tạo thêm danh mục / nhà cung cấp / kho mới. Mỗi style được gán ngẫu nhiên (seed cố định để chạy lại ra
cùng dữ liệu) 2–3 màu x 2–3 cỡ, vật liệu tổng 100%, bảng cỡ theo từng cỡ, một ảnh (khung màu, sinh bằng
`setup_db.build_media_and_index`), tồn kho kèm `StockMovement` lý do `restock` để Σ sổ kho vẫn khớp `on_hand`
(mục 13 #RG, như PROGRESS.md đã ghi cho 4 sản phẩm gốc).
"""
from __future__ import annotations

import argparse
import os
import random
import sys

import psycopg

for _s in (sys.stdout, sys.stderr):          # console Windows mặc định cp1252 không in được tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DSN = os.environ.get("ABC_FASHION_DSN", "dbname=abc_fashion_v2 user=postgres host=localhost port=5432")

# Tên danh mục lá khác nhau giữa CSDL thật đã migrate (tiếng Anh) và db/seed.sql (tiếng Việt, cho abc_fashion_test).
CATEGORY_NAME_CANDIDATES = {
    "Shirts": ["Shirts", "Áo nam"],
    "Jeans": ["Jeans", "Quần nam"],
    "Dresses": ["Dresses", "Váy"],
    "Tops": ["Tops", "Áo nữ"],
}

# ---------------------------------------------------------------- dữ liệu theo danh mục
# mỗi mục: tiền tố mã, khoảng giá (đ, bội số 10.000), mẫu tên, cỡ dùng, màu dùng, vật liệu
CATEGORIES = {
    "Shirts": dict(
        prefix="SH", price=(320_000, 620_000),
        patterns=["Oxford", "Checked", "Striped", "Denim", "Flannel", "Poplin", "Chambray", "Twill",
                  "Seersucker", "Corduroy", "Herringbone", "Gingham"],
        fits=["Slim", "Regular", "Relaxed", "Oversized"], suffix="Shirt",
        sizes=["XS", "S", "M", "L", "XL"],
        colours=["White", "Blue", "Grey", "Navy", "Khaki", "Beige", "Black", "Charcoal"],
        materials=[[("Cotton", 100)], [("Linen", 100)], [("Cotton", 80), ("Polyester", 20)],
                   [("Cotton", 97), ("Elastane", 3)], [("Cotton", 70), ("Linen", 30)]],
        measures=["chest", "length", "sleeve"],
    ),
    "Jeans": dict(
        prefix="JN", price=(450_000, 850_000),
        patterns=["Light Wash", "Dark Wash", "Stonewash", "Raw Denim", "Distressed", "Acid Wash",
                   "Black Wash", "Mid Wash", "Vintage Wash", "Selvedge"],
        fits=["Slim", "Regular", "Relaxed", "Skinny", "Straight", "Bootcut"], suffix="Jeans",
        sizes=["28", "29", "30", "31", "32", "33", "34"],
        colours=["Indigo", "Black", "Grey", "Navy", "Khaki", "Blue"],
        materials=[[("Cotton", 98), ("Elastane", 2)], [("Cotton", 100)],
                   [("Cotton", 80), ("Polyester", 18), ("Elastane", 2)], [("Cotton", 92), ("Elastane", 8)]],
        measures=["waist", "hip", "inseam"],
    ),
    "Dresses": dict(
        prefix="DR", price=(390_000, 990_000),
        patterns=["Floral", "Polka Dot", "Satin", "Wrap", "A-Line", "Pleated", "Tiered", "Shirt",
                   "Slip", "Knit", "Linen", "Velvet"],
        fits=["Midi", "Maxi", "Mini"], suffix="Dress",
        sizes=["XS", "S", "M", "L", "XL"],
        colours=["Floral", "Red", "Pink", "Black", "Navy", "Beige", "Mustard", "Maroon"],
        materials=[[("Viscose", 100)], [("Polyester", 100)], [("Viscose", 95), ("Elastane", 5)],
                   [("Cotton", 60), ("Viscose", 40)], [("Satin Polyester", 100)]],
        measures=["chest", "waist", "hip", "length"],
    ),
    "Tops": dict(
        prefix="TS", price=(220_000, 480_000),
        patterns=["Ruffle Sleeve", "Cropped Knit", "Silk Camisole", "Puff Sleeve", "Off-Shoulder",
                   "Peplum", "Wrap", "Button-Down", "Lace Trim", "Turtleneck", "Basic Cotton", "Rib Knit"],
        fits=["", "Relaxed", "Fitted"], suffix="Top",
        sizes=["XS", "S", "M", "L", "XL"],
        colours=["White", "Pink", "Beige", "Black", "Cream", "Yellow", "Teal", "Grey"],
        materials=[[("Cotton", 100)], [("Modal", 95), ("Elastane", 5)], [("Cotton", 92), ("Elastane", 8)],
                   [("Silk", 100)], [("Viscose", 100)]],
        measures=["chest", "length"],
    ),
}

COLOUR_ABBR = {"White": "WHT", "Black": "BLK", "Red": "RED", "Blue": "BLU", "Navy": "NVY", "Grey": "GRY",
               "Beige": "BEI", "Pink": "PNK", "Khaki": "KHK", "Indigo": "IND", "Floral": "FLO",
               "Mustard": "MUS", "Maroon": "MRN", "Cream": "CRM", "Yellow": "YLW", "Teal": "TEA",
               "Charcoal": "CHR"}

# cm cơ sở theo cỡ chữ (áo / đầm) — tăng dần theo cỡ
LETTER_SIZE_BASE = {
    "XS": {"chest": 82, "waist": 62, "hip": 86, "length": 58, "sleeve": 58},
    "S":  {"chest": 88, "waist": 66, "hip": 92, "length": 60, "sleeve": 60},
    "M":  {"chest": 94, "waist": 70, "hip": 98, "length": 62, "sleeve": 62},
    "L":  {"chest": 100, "waist": 76, "hip": 104, "length": 64, "sleeve": 64},
    "XL": {"chest": 106, "waist": 82, "hip": 110, "length": 66, "sleeve": 66},
}


def size_value_cm(category: str, size: str, measure: str) -> float:
    """Số đo (cm) của một cỡ; quần jeans tính theo số đo vòng eo (inch), áo / đầm theo bảng cỡ chữ."""
    if category == "Jeans":
        waist = 54.0 + int(size) * 2.5          # vòng eo tăng ~2,5 cm mỗi cỡ số (khớp dữ liệu mẫu JN-SLM-02)
        return {"waist": waist, "hip": waist + 22.0, "inseam": 78.0}[measure]
    return float(LETTER_SIZE_BASE[size][measure])


def make_style_name(rng: random.Random, cfg: dict, used: set[str]) -> tuple[str, str]:
    """Trả (pattern, tên đầy đủ) chưa dùng cho danh mục này."""
    for _ in range(200):
        pattern, fit = rng.choice(cfg["patterns"]), rng.choice(cfg["fits"])
        name = f"{pattern} {fit} {cfg['suffix']}".replace("  ", " ").strip()
        if name not in used:
            used.add(name)
            return pattern, name
    raise RuntimeError("hết tổ hợp tên cho danh mục " + cfg["suffix"])


def build_rows(rng: random.Random, count: int, categories: dict[str, int]) -> list[dict]:
    """Sinh dữ liệu đầy đủ (chưa ghi CSDL) cho `count` style, chia đều cho các danh mục."""
    names_used: dict[str, set[str]] = {k: set() for k in CATEGORIES}
    counters = {k: 11 for k in CATEGORIES}        # 01–10 đã dùng ở seed gốc / dữ liệu báo cáo
    order = [list(CATEGORIES)[i % len(CATEGORIES)] for i in range(count)]      # chia đều, không lệch danh mục
    rows = []
    for name_key in order[:count]:
        cfg = CATEGORIES[name_key]
        pattern, full_name = make_style_name(rng, cfg, names_used[name_key])
        num = counters[name_key]
        counters[name_key] += 1
        abbr = "".join(ch for ch in pattern.upper() if ch.isalpha())[:3] or "GEN"
        code = f"{cfg['prefix']}-{abbr}-{num:02d}"
        price = rng.randrange(cfg["price"][0], cfg["price"][1] + 1, 10_000)
        sizes = sorted(rng.sample(cfg["sizes"], k=min(rng.randint(2, 3), len(cfg["sizes"]))),
                       key=cfg["sizes"].index)
        colours = rng.sample(cfg["colours"], k=min(rng.randint(2, 3), len(cfg["colours"])))
        materials = rng.choice(cfg["materials"])
        rows.append(dict(
            category=name_key, code=code, name=full_name, price=price, sizes=sizes, colours=colours,
            materials=materials, measures=cfg["measures"],
            brand=rng.choice(["ABC Basics", "ABC Denim", "ABC Atelier", "ABC Studio"]),
            fit_type=rng.choice(["slim", "regular", "relaxed", "oversized"]),
            care=rng.choice(["Giặt máy ở 30°C, không tẩy, phơi trong bóng râm.",
                             "Giặt tay nước lạnh, không vắt mạnh, ủi nhiệt độ thấp.",
                             "Giặt khô hoặc giặt máy nhẹ, treo khô, tránh ánh nắng trực tiếp."]),
            features=rng.choice(["Vải thoáng khí, thấm hút tốt.", "Co giãn 4 chiều, thoải mái vận động.",
                                 "Form dáng chuẩn, dễ phối đồ.", "Chất liệu bền màu, ít nhăn."]),
            model_info=f"Người mẫu cao 1,7{rng.randint(0,5)}m mặc cỡ {sizes[len(sizes)//2]}.",
        ))
    return rows


def insert_products(con: psycopg.Connection, rows: list[dict], categories: dict[str, int], suppliers: list[int],
                    collections: list[int], locations: list[int], staff_id: int | None) -> int:
    made = 0
    with con.transaction():
        for i, r in enumerate(rows):
            style_id = con.execute(
                'INSERT INTO "tblStyle"("code","name","description","brand","fit_type","care_instructions",'
                '"features","model_info","status","categoryId","supplierId","collectionId") '
                'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,\'active\',%s,%s,%s) RETURNING "id"',
                (r["code"], r["name"], f"{r['name']} — thiết kế {r['fit_type']}, chất liệu "
                 + "/".join(m for m, _ in r["materials"]) + ".", r["brand"], r["fit_type"], r["care"],
                 r["features"], r["model_info"], categories[r["category"]],
                 suppliers[i % len(suppliers)], collections[i % len(collections)])).fetchone()["id"]

            for material, percent in r["materials"]:
                con.execute('INSERT INTO "tblMaterialComponent"("material","percent","styleId") VALUES (%s,%s,%s)',
                           (material, percent, style_id))

            for size in r["sizes"]:
                for measure in r["measures"]:
                    con.execute('INSERT INTO "tblSizeChartEntry"("size_label","measure","value_cm","styleId") '
                               'VALUES (%s,%s,%s,%s)',
                               (size, measure, size_value_cm(r["category"], size, measure), style_id))

            cover_colour = r["colours"][0]
            rel_url = f"media/products/{r['code'].lower()}.png"
            con.execute('INSERT INTO "tblProductMedia"("url","media_type","colour","sort_order","styleId") '
                       'VALUES (%s,\'image\',%s,1,%s)', (rel_url, cover_colour, style_id))

            location_id = locations[i % len(locations)]
            for colour in r["colours"]:
                for size in r["sizes"]:
                    abbr = COLOUR_ABBR.get(colour, colour[:3].upper())
                    sku = f"{r['code']}-{abbr}-{size}"
                    variant_id = con.execute(
                        'INSERT INTO "tblProductVariant"("sku","size_label","colour","price","status","styleId") '
                        'VALUES (%s,%s,%s,%s,\'active\',%s) RETURNING "id"',
                       (sku, size, colour, r["price"], style_id)).fetchone()["id"]
                    on_hand = random.Random(variant_id).randint(12, 60)        # tái lập được theo id
                    reorder_point = max(5, on_hand // 5)
                    con.execute(
                        'INSERT INTO "tblStockLevel"("on_hand","reserved","reorder_point","available",'
                        '"productVariantId","stockLocationId") VALUES (%s,0,%s,%s,%s,%s)',
                        (on_hand, reorder_point, on_hand, variant_id, location_id))
                    con.execute(
                        'INSERT INTO "tblStockMovement"("quantity_change","reason","reference","note",'
                        '"productVariantId","stockLocationId","staffMemberId") '
                        "VALUES (%s,'restock',%s,'Nhập kho ban đầu — dữ liệu mẫu bổ sung',%s,%s,%s)",
                        (on_hand, "BULK-SEED", variant_id, location_id, staff_id))
            made += 1
    return made


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dsn", default=DEFAULT_DSN)
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()

    con = psycopg.connect(args.dsn, autocommit=True, row_factory=psycopg.rows.dict_row)
    by_name = {r["name"]: r["id"] for r in con.execute('SELECT "id","name" FROM "tblCategory"').fetchall()}
    categories, missing = {}, []
    for key, candidates in CATEGORY_NAME_CANDIDATES.items():
        found = next((by_name[c] for c in candidates if c in by_name), None)
        if found is None:
            missing.append(f"{key} ({'/'.join(candidates)})")
        else:
            categories[key] = found
    if missing:
        print(f"Thiếu danh mục trong CSDL: {missing} — chạy trên CSDL đã có schema + seed trước.")
        return 1
    suppliers = [r["id"] for r in con.execute('SELECT "id" FROM "tblSupplier" ORDER BY "id"').fetchall()]
    collections = [r["id"] for r in con.execute('SELECT "id" FROM "tblCollection" ORDER BY "id"').fetchall()]
    locations = [r["id"] for r in con.execute('SELECT "id" FROM "tblStockLocation" ORDER BY "id"').fetchall()]
    staff = con.execute('SELECT "id" FROM "tblStaffMember" WHERE "role" = \'warehouse\' LIMIT 1').fetchone()
    if not (suppliers and collections and locations):
        print("Thiếu nhà cung cấp / bộ sưu tập / kho — chạy trên CSDL đã có schema + seed trước.")
        return 1

    rng = random.Random(args.seed)
    rows = build_rows(rng, args.count, categories)
    made = insert_products(con, rows, categories, suppliers, collections, locations,
                           staff["id"] if staff else None)
    print(f"Đã thêm {made} sản phẩm ({sum(len(r['colours']) * len(r['sizes']) for r in rows)} biến thể).")
    print("Chạy tiếp để sinh ảnh khung màu + chỉ mục tìm kiếm:")
    print(f'  ..\\.venv\\Scripts\\python.exe db\\setup_db.py --dsn "{args.dsn}" --index')
    return 0


if __name__ == "__main__":
    sys.exit(main())
