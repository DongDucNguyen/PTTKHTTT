"""Tạo CSDL abc_fashion_v2 (hoặc CSDL thử), chạy schema + seed, sinh ảnh mẫu và chỉ mục tìm kiếm sandbox.

    python db/setup_db.py                 # tạo CSDL theo ABC_FASHION_DSN nếu chưa có, rồi schema + seed
    python db/setup_db.py --reset         # XOÁ và tạo lại CSDL (mất dữ liệu)
    python db/setup_db.py --index         # chỉ sinh lại ảnh mẫu + media/search_index.json
    python db/setup_db.py --dsn "dbname=abc_fashion_test user=postgres password=..." --reset

CSDL đã có bảng (tạo từ báo cáo) thì script dừng lại: dùng migrate_v2.sql thay vì tạo mới.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

for _s in (sys.stdout, sys.stderr):          # console Windows mặc định cp1252 không in được tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(HERE)
DEFAULT_DSN = os.environ.get("ABC_FASHION_DSN", "dbname=abc_fashion_v2 user=postgres host=localhost port=5432")

COLOURS = {"trắng": (240, 238, 232), "đen": (35, 35, 38), "đỏ": (196, 40, 52), "xanh": (42, 82, 168),
           "xám": (128, 128, 128), "be": (222, 203, 170), "hồng": (232, 150, 170), "vàng": (230, 196, 60),
           "nâu": (120, 80, 50), "white": (240, 238, 232), "black": (35, 35, 38), "red": (196, 40, 52),
           "blue": (42, 82, 168), "indigo": (40, 50, 110), "navy": (30, 40, 80), "grey": (128, 128, 128),
           "gray": (128, 128, 128), "beige": (222, 203, 170), "pink": (232, 150, 170), "floral": (214, 120, 140)}


def _rgb(name: str | None) -> tuple[int, int, int]:
    return COLOURS.get((name or "").strip().lower(), (180, 180, 180))


def create_database(dsn: str, reset: bool) -> bool:
    """Tạo CSDL nếu chưa có. Trả `True` nếu CSDL rỗng (cần chạy schema)."""
    params = conninfo_to_dict(dsn)
    dbname = params.get("dbname", "abc_fashion_v2")
    admin = make_conninfo(**{**params, "dbname": "postgres"})
    with psycopg.connect(admin, autocommit=True) as con:
        exists = con.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)).fetchone()
        if exists and reset:
            con.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(dbname)))
            exists = None
        if not exists:
            con.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0").format(sql.Identifier(dbname)))
            print(f"Đã tạo CSDL {dbname}")
            return True
    with psycopg.connect(dsn) as con:
        n = con.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'").fetchone()[0]
    if n:
        print(f"CSDL {dbname} đã có {n} bảng. Không ghi đè: dùng --reset để tạo lại, "
              f"hoặc chạy db/migrate_v2.sql cho CSDL tạo từ báo cáo.")
        return False
    return True


def run_script(dsn: str, filename: str) -> None:
    with open(os.path.join(HERE, filename), encoding="utf-8") as f:
        script = f.read()
    with psycopg.connect(dsn, autocommit=True) as con:
        con.execute(script)
    print(f"Đã chạy {filename}")


def build_media_and_index(dsn: str) -> None:
    """Ảnh mẫu một màu cho mỗi tblProductMedia (nếu chưa có file) + chỉ mục cho SearchEngine sandbox."""
    from PIL import Image, ImageDraw

    with psycopg.connect(dsn) as con:
        media = con.execute('SELECT m."url", m."colour", s."code", s."name" FROM "tblProductMedia" m '
                            'JOIN "tblStyle" s ON s."id" = m."styleId"').fetchall()
        styles = con.execute(
            'SELECT s."id", s."code", s."name", s."brand", s."description", c."name", '
            '  array_agg(DISTINCT v."colour"), array_remove(array_agg(DISTINCT m."url"), NULL) '
            'FROM "tblStyle" s JOIN "tblCategory" c ON c."id" = s."categoryId" '
            'LEFT JOIN "tblProductVariant" v ON v."styleId" = s."id" '
            'LEFT JOIN "tblProductMedia" m ON m."styleId" = s."id" AND m."media_type" = \'image\' '
            'WHERE s."status" = \'active\' GROUP BY s."id", c."name" ORDER BY s."id"').fetchall()
    made = 0
    for url, colour, code, name in media:
        if "://" in url:                                   # ảnh trên CDN: không sinh file cục bộ
            continue
        path = os.path.join(CODE_DIR, url)
        if os.path.exists(path) or not url.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im = Image.new("RGB", (400, 480), _rgb(colour))
        d = ImageDraw.Draw(im)
        fg = (255, 255, 255) if sum(_rgb(colour)) < 380 else (40, 40, 40)
        d.text((20, 20), f"{code}\n{name}\n{colour or ''}", fill=fg)
        im.save(path)
        made += 1
    index = []
    for sid, code, name, brand, desc, cat, colours, urls in styles:
        rgbs = []
        for u in urls:
            p = os.path.join(CODE_DIR, u)
            if "://" not in u and os.path.exists(p):
                with Image.open(p) as im:
                    rgbs.append(list(im.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))))
        rgbs += [list(_rgb(c)) for c in colours if c]
        index.append({"id": sid, "colours": rgbs,
                      "keywords": [w for w in (code, name, brand, desc, cat, *colours) if w]})
    out = os.path.join(CODE_DIR, "media", "search_index.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"Đã sinh {made} ảnh mẫu mới và chỉ mục {len(index)} style → {out}")


def setup(dsn: str, reset: bool = False, seed: bool = True, index: bool = True) -> bool:
    if not create_database(dsn, reset):
        return False
    run_script(dsn, "schema.sql")
    if seed:
        run_script(dsn, "seed.sql")
        if index:
            build_media_and_index(dsn)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dsn", default=DEFAULT_DSN)
    ap.add_argument("--reset", action="store_true", help="xoá và tạo lại CSDL")
    ap.add_argument("--no-seed", action="store_true", help="chỉ tạo bảng, không nạp dữ liệu mẫu")
    ap.add_argument("--index", action="store_true", help="chỉ sinh lại ảnh mẫu và chỉ mục tìm kiếm")
    args = ap.parse_args()
    if args.index:
        build_media_and_index(args.dsn)
        return 0
    return 0 if setup(args.dsn, args.reset, not args.no_seed) else 1


if __name__ == "__main__":
    sys.exit(main())
