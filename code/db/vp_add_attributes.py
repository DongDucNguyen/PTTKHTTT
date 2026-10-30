"""Thêm vào project.xml (xuất từ Visual Paradigm) các thuộc tính mà mã đã dùng nhưng mô hình chưa có (mục A1 của
HUONG_DAN_SUA_VP_VA_BAO_CAO.md):

    Order       .ship_recipient / ship_phone / ship_address : str   (sau cancel_reason, trước customerId)
    ReturnItem  .replacementVariantId                       : int   (sau orderItemId)

    python db/vp_add_attributes.py ../vp_export/project.xml

Chèn thẳng vào văn bản XML (nhân bản một thuộc tính có sẵn cùng kiểu, đổi id / tên), nên mọi byte khác giữ nguyên.
Ghi ra hai file cạnh project.xml:
    project.xml          bản đã thêm, định dạng giống file VP xuất (dùng cho vp2py.py)
    project_import.xml   cùng nội dung + khai báo namespace như các file nhập VP trước đây (import vào VP)
Bản gốc được lưu ở project.before_attrs.xml (chỉ tạo lần đầu). Chạy lại khi đã có thuộc tính thì không làm gì.
"""
from __future__ import annotations

import os
import random
import re
import shutil
import string
import sys
import time

for _s in (sys.stdout, sys.stderr):          # console Windows mặc định cp1252 không in được tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ID_ALPHABET = string.ascii_letters + string.digits + "_."
NS = ('<Project xmlns="http://www.visual-paradigm.com/product/vpuml/modelexporter" '
      'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ')

# (lớp, thuộc tính mẫu để nhân bản, danh sách thuộc tính mới sẽ chèn ngay SAU thuộc tính mẫu)
PLAN = [
    ("Order", "cancel_reason", ["ship_recipient", "ship_phone", "ship_address"]),   # mẫu kiểu str
    ("ReturnItem", "orderItemId", ["replacementVariantId"]),                        # mẫu kiểu int
]


def find_class_span(text: str, name: str) -> tuple[int, int]:
    m = re.search(r'<Model [^>]*modelType="Class"[^>]*name="%s"[^>]*>' % re.escape(name), text)
    if not m:
        raise SystemExit(f"Không thấy lớp {name}")
    # lớp chứa Model con lồng nhau: đếm <Model ... > / </Model> để tìm thẻ đóng tương ứng
    depth, pos = 0, m.start()
    for t in re.finditer(r"<Model\b[^>]*?(/?)>|</Model>", text[pos:]):
        if t.group(0) == "</Model>":
            depth -= 1
            if depth == 0:
                return pos, pos + t.end()
        elif not t.group(1):
            depth += 1
    raise SystemExit(f"Không thấy thẻ đóng của {name}")


def attribute_span(text: str, cls: tuple[int, int], attr: str) -> tuple[int, int, str]:
    a, b = cls
    m = re.search(r'([ \t]*)(<Model [^>]*modelType="Attribute"[^>]*name="%s"[^>]*>)' % re.escape(attr), text[a:b])
    if not m:
        raise SystemExit(f"Không thấy thuộc tính {attr}")
    start = a + m.start(2)
    end = text.index("</Model>", start) + len("</Model>")
    return start, end, m.group(1)


def new_id(used: set[str]) -> str:
    while True:
        i = "".join(random.choice(ID_ALPHABET) for _ in range(16))
        if i not in used and not i[0] in ".":
            used.add(i)
            return i


def clone(block: str, old: str, new: str, used: set[str]) -> str:
    out = re.sub(r'(<Model [^>]*?\bid=")[^"]+(")', lambda m: m.group(1) + new_id(used) + m.group(2), block, count=1)
    out = out.replace(f'"{old}"', f'"{new}"')                                   # name="…" và value="…"
    now = str(int(time.time() * 1000))
    return re.sub(r'(name="pm(?:CreateDateTime|LastModified)" value=")\d+(")', lambda m: m.group(1) + now + m.group(2), out)


def main(path: str) -> int:
    text = open(path, encoding="utf-8").read()
    used = set(re.findall(r'\bid="([^"]+)"', text))
    todo = [(c, s, [n for n in new if f'modelType="Attribute"' not in text or not re.search(
        r'<Model [^>]*modelType="Attribute"[^>]*name="%s"' % re.escape(n), text[slice(*find_class_span(text, c))])])
            for c, s, new in PLAN]
    if not any(names for _, _, names in todo):
        print("Mô hình đã có đủ thuộc tính — không làm gì.")
        return 0
    backup = os.path.join(os.path.dirname(path), "project.before_attrs.xml")
    if not os.path.exists(backup):
        shutil.copyfile(path, backup)
        print("đã sao lưu bản gốc →", backup)
    for cls_name, sample, names in todo:
        if not names:
            continue
        a, b = find_class_span(text, cls_name)
        s, e, indent = attribute_span(text, (a, b), sample)
        block = text[s:e]
        # thuộc tính mới chèn theo thứ tự, sau thuộc tính mẫu
        # (mẫu của replacementVariantId là orderItemId: cùng kiểu int, nên nhân bản đúng)
        pieces = "".join("\n" + indent + clone(block, sample, n, used) for n in names)
        text = text[:e] + pieces + text[e:]
        print(f"{cls_name}: thêm {', '.join(names)} (nhân bản từ {sample})")
    open(path, "w", encoding="utf-8", newline="").write(text)
    imp = os.path.join(os.path.dirname(path), "project_import.xml")
    head = text.index("<Project ")
    open(imp, "w", encoding="utf-8", newline="").write(text[:head] + NS + text[head + len("<Project "):])
    print("đã ghi", path, "và", imp)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]) if len(sys.argv) > 1 else print(__doc__) or 2)
