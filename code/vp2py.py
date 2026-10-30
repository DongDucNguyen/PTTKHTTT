"""Sinh mã Python từ mô hình Visual Paradigm (mục 12.1 của HUONG_DAN_CODE.md).

    # trong Visual Paradigm: Project > Export > XML  → project.xml
    python vp2py.py project.xml out_dir            # sinh bộ khung abc_fashion/ vào out_dir (ghi đè)
    python vp2py.py project.xml --check .          # so mô hình với mã đã lập trình trong ./abc_fashion
    STATS=1 python vp2py.py project.xml out_dir    # in thêm số quan hệ theo layer / package

Sinh lại sẽ ghi đè file: luôn sinh vào thư mục tạm rồi so sánh (mục 12.3). `--check` không ghi gì; nó báo
các chỗ mã lệch mô hình (lớp, kế thừa, chữ ký hàm, trường entity và kiểu, literal enum, thuộc tính Frm,
DAO / gateway Frm dùng). Sai khác đã được duyệt nằm trong KNOWN_DEVIATIONS và được liệt kê riêng.
"""
from __future__ import annotations

import collections
import dataclasses
import importlib
import inspect
import os
import re
import sys
import typing
import xml.etree.ElementTree as ET

for _s in (sys.stdout, sys.stderr):          # console Windows mặc định cp1252 không in được tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Thuộc tính bị VP liệt kê dưới hai lớp (đã gặp: quantity_sold, revenue dưới cả Review và StyleStat)
OWNER_FIX = {"Review": {"quantity_sold", "revenue", "order_count"}}

# Sai khác đã duyệt giữa mã và mô hình (ghi trong PROGRESS.md). Hiện không còn: 4 thuộc tính ship_* /
# replacementVariantId đã được thêm vào mô hình bằng db/vp_add_attributes.py.
KNOWN_DEVIATIONS: dict[tuple[str, str, str], str] = {}

GATEWAYS = {"AssistantEngine", "NotificationGateway", "PaymentGateway", "SearchEngine", "ShippingGateway"}
PY_TYPES = {"int", "str", "bool", "float", "date", "datetime", "bytes", "dict", "tuple", "None", "list"}
DATE_TYPES = {"date", "datetime"}


# ====================================================================== đọc XML
class Model:
    """Toàn bộ mô hình đã đọc: lớp, kế thừa, association."""

    def __init__(self, path: str):
        self.root = ET.parse(path).getroot()
        for el in self.root.iter():                       # chấp nhận cả file có namespace (dạng nhập vào VP)
            if isinstance(el.tag, str) and el.tag.startswith("{"):
                el.tag = el.tag.split("}", 1)[1]
        self.byid = {m.get("id"): m for m in self.root.iter("Model")}
        self.classes: dict[str, dict] = {}
        top = next(m for m in self.root.find("Models") if m.get("name") == "abc_fashion")
        self.walk(top, [])
        self.supers: dict[str, str] = {}
        self.assocs: list[dict] = []
        self._relationships()

    # ---------- truy cập thuộc tính của một phần tử ----------
    @staticmethod
    def props(m) -> dict:
        mp = m.find("ModelProperties")
        return {p.get("name"): p for p in mp} if mp is not None else {}

    def prop(self, m, name):
        return self.props(m).get(name)

    def sval(self, m, name) -> str | None:
        p = self.prop(m, name)
        return None if p is None else p.get("value")

    def tval(self, m, name: str = "type") -> str | None:
        """Kiểu: StringValue hoặc tham chiếu ModelRef tới một lớp / kiểu dữ liệu."""
        p = self.prop(m, name)
        if p is None:
            return None
        for c in p:
            if c.tag == "StringValue":
                return c.get("value")
            if c.tag == "ModelRef":
                target = self.byid.get(c.get("id"))
                return target.get("name") if target is not None else None
        return p.get("value")

    def ftype(self, m) -> str:
        """Kiểu kèm typeModifier: `list` + `[Address]` → `list[Address]`."""
        t = (self.tval(m) or "").strip()
        mod = (self.sval(m, "typeModifier") or "").strip()
        return f"{t}{mod}" if mod else t

    @staticmethod
    def kids(m, t: str | None = None) -> list:
        ch = m.find("ChildModels")
        return [c for c in (ch if ch is not None else []) if c.tag == "Model" and (t is None or c.get("modelType") == t)]

    def stereos(self, m) -> list[str]:
        p = self.prop(m, "stereotypes")
        return [self.byid[r.get("id")].get("name") for r in p if r.get("id") in self.byid] if p is not None else []

    def doc_of(self, m) -> str:
        p = self.prop(m, "documentation")
        return (p.get("plainTextValue") or "").strip() if p is not None else ""

    # ---------- cây package ----------
    def walk(self, pkg, path: list[str]) -> None:
        for c in self.kids(pkg):
            if c.get("modelType") == "Package":
                self.walk(c, path + [c.get("name")])
            elif c.get("modelType") == "Class":
                name = c.get("name")
                attrs = [(a.get("name"), self.ftype(a)) for a in self.kids(c, "Attribute")
                         if a.get("name") not in OWNER_FIX.get(name, ())]
                ops = [(o.get("name"), [(p.get("name"), self.ftype(p), self.sval(p, "defaultValue"))
                                        for p in self.kids(o, "Parameter") if p.get("name") != "self"])
                       for o in self.kids(c, "Operation")]
                self.classes[name] = {"name": name, "path": path, "stereotypes": self.stereos(c), "attrs": attrs,
                                      "ops": ops, "literals": [l.get("name").strip() for l in self.kids(c, "EnumerationLiteral")],
                                      "doc": self.doc_of(c)}

    def is_enum(self, c: dict) -> bool:
        return bool(c["literals"]) or "enumeration" in c["stereotypes"]

    # ---------- quan hệ ----------
    def _relationships(self) -> None:
        for m in self.root.iter("Model"):
            kind = m.get("modelType")
            if kind == "Generalization":                      # from = lớp cha
                parent, child = self.tval(m, "from"), self.tval(m, "to")
                if child in self.classes:
                    self.supers[child] = parent
            elif kind == "Association":
                ends = []
                for tag in ("FromEnd", "ToEnd"):
                    e = m.find(tag)
                    em = e.find("Model") if e is not None else None
                    if em is None:
                        break
                    ends.append({"cls": self.tval(em, "EndModelElement") or self.tval(em, "type"),
                                 "agg": self.sval(em, "aggregationKind"), "mult": self.sval(em, "multiplicity")})
                if len(ends) == 2 and ends[0]["cls"] in self.classes and ends[1]["cls"] in self.classes:
                    self.assocs.append({"name": m.get("name") or "", "from": ends[0], "to": ends[1]})

    # ---------- tra cứu ----------
    def layer(self, name: str) -> str:
        return self.classes[name]["path"][0]

    def entity_name(self, n: str) -> str:
        """Tên kiểu trong mô hình → tên lớp entity (trùng nhau; giữ hàm để chỗ gọi không đổi)."""
        return n

    def fix_type(self, t: str) -> str:
        t = (t or "").replace(" ", "")
        if not t:
            return ""
        t = re.sub(r"\b([A-Za-z_]\w*)\b", lambda m: self.entity_name(m.group(1)), t)
        return t.replace("|", " | ")

    def uses(self, name: str) -> list[str]:
        """Lớp mà Frm / controller dùng (association): Frm → controller, controller → DAO / gateway."""
        return sorted({a["to"]["cls"] for a in self.assocs if a["from"]["cls"] == name
                       and self.layer(a["to"]["cls"]) in ("control", "controller")})

    def opens(self, name: str) -> list[str]:
        return sorted({a["to"]["cls"] for a in self.assocs if a["from"]["cls"] == name
                       and self.layer(a["to"]["cls"]) == "view"})

    def relationships_of(self, name: str) -> list[str]:
        kinds = {"Composited": "composition", "Shared": "aggregation"}
        out = []
        for a in self.assocs:
            if a["from"]["cls"] == name and self.layer(a["to"]["cls"]) == "model" and self.layer(name) == "model":
                out.append(f"{a['to']['cls']} ({kinds.get(a['from']['agg'], 'association')}, {a['to']['mult']})")
        return out


# ====================================================================== tiện ích tên / import
def snake(n: str) -> str:
    """`CheckoutFrm` → `checkout_frm`; `OrderDAO` → `order_dao`."""
    n = n.replace("DAO", "Dao")
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", n).lower()


def module_of(model: Model, name: str) -> str:
    c = model.classes[name]
    pkg = "abc_fashion." + ".".join(c["path"])
    return pkg if c["path"][0] == "model" else f"{pkg}.{snake(name)}"


def names_in(t: str) -> set[str]:
    return set(re.findall(r"\b[A-Za-z_]\w*\b", t or ""))


def imports_for(model: Model, module: str, types: list[str]) -> list[str]:
    """`from … import …` cho các lớp được dùng trong kiểu (theo package dependency)."""
    need: dict[str, set[str]] = collections.defaultdict(set)
    for t in types:
        for n in map(model.entity_name, names_in(t)):
            if n in model.classes and module_of(model, n) != module:
                need[module_of(model, n)].add(n)
    return [f"from {m} import {', '.join(sorted(ns))}" for m, ns in sorted(need.items())]


def py_type(model: Model, t: str) -> str:
    t = model.fix_type(t)
    return t if t else "object"


def params(model: Model, op_params) -> str:
    return "".join(f", {p}: {py_type(model, t)}" + (f" = {d}" if d else "") for p, t, d in op_params)


def doc(model: Model, name: str, extra: list[str]) -> str:
    c = model.classes[name]
    lines = [c["doc"] or name]
    lines += [f"Stereotypes: {', '.join(c['stereotypes'])}."] if c["stereotypes"] else []
    lines += extra
    return '    """' + "\n\n    ".join(lines) + '\n    """\n'


# ====================================================================== sinh mã
def generate(model: Model) -> dict[str, str]:
    files: dict[str, str] = {}
    by_pkg: dict[str, list[str]] = collections.defaultdict(list)
    for name, c in model.classes.items():
        by_pkg[module_of(model, name)].append(name)

    # ---------- model layer: mỗi package một module; enum trước, entity sau, cha trước con ----------
    for module, names in sorted(by_pkg.items()):
        if not module.startswith("abc_fashion.model"):
            continue
        enums = [n for n in names if model.is_enum(model.classes[n])]
        ents = [n for n in names if n not in enums]
        ordered: list[str] = []
        while ents:
            for n in list(ents):
                if model.supers.get(n) not in ents:
                    ordered.append(n)
                    ents.remove(n)
        types = [t for n in ordered for _, t in model.classes[n]["attrs"]] + [model.supers.get(n, "") for n in ordered]
        flat = " ".join(types)
        out = [f'"""Model package {module.rsplit(".", 1)[1]}."""', "from __future__ import annotations", ""]
        out += ["from dataclasses import dataclass"] if ordered else []
        dts = sorted(DATE_TYPES & names_in(flat))
        out += [f"from datetime import {', '.join(dts)}"] if dts else []
        out += ["from enum import Enum"] if enums else []
        out += [""] + imports_for(model, module, types) if imports_for(model, module, types) else []
        for n in enums:
            out += ["", "", f"class {n}(Enum):"]
            out += [f'    {lit} = "{lit.lower()}"' for lit in model.classes[n]["literals"]] or ["    pass"]
        for n in ordered:
            sup = model.supers.get(n)
            rel = model.relationships_of(n)
            out += ["", "", "@dataclass(kw_only=True)", f"class {n}({sup})" + ":" if sup else f"class {n}:"]
            out.append(doc(model, n, [f"Relationships: {'; '.join(rel)}."] if rel else []).rstrip("\n"))
            out += [f"    {a}: {py_type(model, t)} | None = None" for a, t in model.classes[n]["attrs"]] or ["    pass"]
        files[module] = "\n".join(out) + "\n"

    # ---------- control & view: mỗi lớp một module ----------
    for name, c in sorted(model.classes.items()):
        layer = c["path"][0]
        if layer == "model":
            continue
        module = module_of(model, name)
        types = [t for _, ps in c["ops"] for _, t, _ in ps] + [t for _, t in c["attrs"]]
        out = [f'"""{name} — layer {".".join(["abc_fashion"] + c["path"])}."""', "from __future__ import annotations", ""]
        dts = sorted(DATE_TYPES & names_in(" ".join(types)))
        out += [f"from datetime import {', '.join(dts)}"] if dts else []
        if module.endswith(".dao.dao"):
            out += ["import os", "", "import psycopg", "",
                    'DSN = os.environ.get("ABC_FASHION_DSN", "dbname=abc_fashion_v2 user=postgres host=localhost port=5432")',
                    "", "", f"class {name}:", doc(model, name, []).rstrip("\n"),
                    "    def __init__(self):", "        self.con = psycopg.connect(DSN)"]
            files[module] = "\n".join(out) + "\n"
            continue
        extra_doc, base, init = [], "", []
        uses = model.uses(name) if layer in ("view", "controller") else []
        opens = model.opens(name) if layer == "view" else []
        if layer == "controller":
            extra_doc += [f"Uses: {', '.join(uses)}."] if uses else []
            out += [f"from {module_of(model, u)} import {u}" for u in uses]
        if layer == "view":
            out += ["import tkinter as tk", "from tkinter import ttk", ""]
            base = "tk.Toplevel"
            extra_doc += [f"Uses: {', '.join(uses)}."] if uses else []
            extra_doc += [f"Opens: {', '.join(opens)}."] if opens else []
            holds = [f"{a}: {py_type(model, t)}" for a, t in c["attrs"] if not re.match(r"(ttk|tk)\.", t or "")]
            widgets = [a for a, t in c["attrs"] if re.match(r"(ttk|tk)\.", t or "")]
            extra_doc += [f"Holds: {', '.join(holds)}."] if holds else []
            extra_doc += [f"Widgets: {', '.join(widgets)}."] if widgets else []
            out += [f"from {module_of(model, u)} import {u}" for u in uses]
        elif module.startswith("abc_fashion.control.dao"):
            out += ["from abc_fashion.control.dao.dao import DAO"]
            base = "DAO"
        out += imports_for(model, module, types)
        out += ["", "", f"class {name}({base}):" if base else f"class {name}:", doc(model, name, extra_doc).rstrip("\n")]
        if layer == "controller" and "__init__" not in [o for o, _ in c["ops"]]:
            out += ["    def __init__(self):"] + [f"        self.{snake(u)} = {u}()" for u in uses] + \
                   (["        pass"] if not uses else []) + [""]
        for op, ps in c["ops"]:
            out.append(f"    def {op}(self{params(model, ps)}):")
            if op == "__init__" and layer == "view":
                init = ["        super().__init__()"] + [f"        self.{p} = {p}" for p, _, _ in ps]
                init += [f"        self.{snake(u)} = {u}()" for u in uses]
                out += init
            else:
                out.append("        raise NotImplementedError")
            out.append("")
        if not c["ops"]:
            out.append("    pass")
        files[module] = "\n".join(out).rstrip() + "\n"

    files["abc_fashion.main"] = ('"""Điểm khởi động: mở LoginFrm."""\nfrom abc_fashion.view.account.login_frm import LoginFrm\n\n\n'
                                 'def main():\n    LoginFrm().mainloop()\n\n\nif __name__ == "__main__":\n    main()\n')
    return files


def write(files: dict[str, str], out_dir: str) -> int:
    pkgs = set()
    for module, text in files.items():
        parts = module.split(".")
        path = os.path.join(out_dir, *parts) + ".py"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        for i in range(1, len(parts)):
            pkgs.add(os.path.join(out_dir, *parts[:i]))
    for p in pkgs:
        init = os.path.join(p, "__init__.py")
        if not os.path.exists(init):
            open(init, "w").close()
    return sum(t.count("\n") for t in files.values())


def stats(model: Model) -> None:
    by_layer = collections.Counter(model.layer(n) for n in model.classes)
    print("classes by layer:", dict(by_layer))
    pairs = collections.Counter((model.layer(a["from"]["cls"]), model.layer(a["to"]["cls"])) for a in model.assocs)
    print("associations by layer:", dict(pairs))
    pk = collections.Counter(".".join(model.classes[n]["path"]) for n in model.classes)
    print("classes by package:", dict(sorted(pk.items())))
    print("generalizations:", len(model.supers))


# ====================================================================== so với mã đã lập trình
def _norm(t: str) -> str:
    t = re.sub(r"\s+", "", t or "")
    t = re.sub(r"\|None$", "", t)
    return t


def check(model: Model, code_dir: str) -> int:
    sys.path.insert(0, os.path.abspath(code_dir))
    issues, known = [], []

    def report(cls, kind, what, text):
        (known if (cls, kind, what) in KNOWN_DEVIATIONS else issues).append(
            f"{cls}: {text}" + (f"  [{KNOWN_DEVIATIONS[(cls, kind, what)]}]" if (cls, kind, what) in KNOWN_DEVIATIONS else ""))

    for name, c in sorted(model.classes.items()):
        module = module_of(model, name)
        try:
            mod = importlib.import_module(module)
            cls = getattr(mod, name)
        except Exception as e:                                       # noqa: BLE001
            issues.append(f"{name}: thiếu lớp ({module}: {e})")
            continue
        if name in model.supers and cls.__mro__[1].__name__ != model.supers[name]:
            issues.append(f"{name}: kế thừa {cls.__mro__[1].__name__}, mô hình {model.supers[name]}")
        if model.is_enum(c):
            if [m.name for m in cls] != c["literals"]:
                issues.append(f"{name}: literal {[m.name for m in cls]} ≠ mô hình {c['literals']}")
            continue
        if c["path"][0] == "model":
            hints = typing.get_type_hints(cls)
            own = [a for a, _ in c["attrs"]]
            declared = list(cls.__dict__.get("__annotations__", {}))
            fields = {f.name for f in dataclasses.fields(cls)}
            for a, t in c["attrs"]:
                if a not in fields:
                    issues.append(f"{name}: thiếu trường {a}")
                    continue
                want = _norm(model.fix_type(t))
                got = _norm(re.sub(r"\b(?:\w+\.)+(\w+)", r"\1", str(hints[a]).replace("<class '", "").replace("'>", "")))
                if want and got != want:
                    issues.append(f"{name}.{a}: kiểu {got} ≠ mô hình {want}")
            for f in declared:
                if f not in own:
                    report(name, "field", f, f"trường thêm {f}")
            continue
        model_ops = [o for o, _ in c["ops"]]
        for op, ps in c["ops"]:
            fn = cls.__dict__.get(op)
            if fn is None:
                issues.append(f"{name}.{op}: thiếu hàm")
                continue
            got = [p for p in inspect.signature(inspect.unwrap(fn)).parameters if p != "self"]
            if got != [p for p, _, _ in ps]:
                issues.append(f"{name}.{op}: tham số {got} ≠ mô hình {[p for p, _, _ in ps]}")
        for n, f in cls.__dict__.items():
            if (inspect.isfunction(f) or isinstance(f, staticmethod)) and not n.startswith("_") and n not in model_ops:
                report(name, "method", n, f"hàm công khai thêm {n}")
        if c["path"][0] == "view":
            src = inspect.getsource(mod)
            assigned = set(re.findall(r"self\.(\w+)\s*(?::[^=\n]+)?=(?!=)", src))
            for m in re.finditer(r"self\.\w+(?:\s*,\s*self\.\w+)+\s*=", src):
                assigned |= set(re.findall(r"self\.(\w+)", m.group(0)))
            assigned |= set(re.findall(r'\("(\w+)",', src))           # home_window: setattr theo tên
            for a, _ in c["attrs"]:
                if a not in assigned:
                    issues.append(f"{name}: không gán thuộc tính {a}")
        if c["path"][0] in ("view", "controller"):
            src = inspect.getsource(mod)
            for u in model.uses(name):
                if f"self.{snake(u)} = {u}()" not in src:
                    issues.append(f"{name}: không tạo self.{snake(u)} = {u}() (association Uses)")

    print(f"model: {len(model.classes)} lớp · {sum(len(c['ops']) for c in model.classes.values())} operation · "
          f"{len(model.supers)} kế thừa · {len(model.assocs)} association")
    for line in known:
        print("  ~ (đã duyệt)", line)
    for line in issues:
        print("  ✗", line)
    print(f"lệch mô hình: {len(issues)} · sai khác đã duyệt: {len(known)}")
    return 1 if issues else 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    model = Model(argv[0])
    if argv[1] == "--check":
        return check(model, argv[2] if len(argv) > 2 else os.path.dirname(os.path.abspath(__file__)))
    files = generate(model)
    lines = write(files, argv[1])
    kinds = collections.Counter(model.layer(n) for n in model.classes)
    print(f"generated modules: {len(files)} / lines: {lines} / classes: {dict(kinds)} / "
          f"enums: {sum(model.is_enum(c) for c in model.classes.values())} / "
          f"operations: {sum(len(c['ops']) for c in model.classes.values())}")
    if os.environ.get("STATS") == "1":
        stats(model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
