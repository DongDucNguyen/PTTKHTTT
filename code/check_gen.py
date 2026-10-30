"""Kiểm tra mã abc_fashion (mục 12.2 của HUONG_DAN_CODE.md).

    python check_gen.py <thư mục chứa abc_fashion>      (mặc định: thư mục của file này)

1. Import mọi module (bắt lỗi cú pháp, import sai, vòng import). Không cần CSDL, không cần màn hình.
2. Đọc câu lệnh import bằng `ast`, kiểm tra quy tắc layer MVC (mục 2.2):
   view → controller → control (dao, gateway) → model. View không import control; psycopg chỉ trong control.dao;
   tkinter chỉ trong view (và main); không có câu SQL trong view / controller.
   Ứng dụng web khách hàng (`abc_fashion_web/`, cạnh `abc_fashion/`) cũng là một view: chỉ import controller + model.
3. Đếm lớp theo layer, enum, operation để so với mô hình (53 Frm / 15 controller / 34 DAO / 5 gateway / 41 entity /
   34 enum / operation).
Thoát mã 1 nếu có vi phạm hoặc số lớp lệch mô hình.
"""
from __future__ import annotations

import ast
import dataclasses
import enum
import importlib
import inspect
import os
import re
import sys
import types

for _s in (sys.stdout, sys.stderr):          # console Windows mặc định cp1252 không in được tiếng Việt
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

EXPECTED = {"view": 53, "controller": 15, "dao": 34, "gateway": 5, "entity": 41, "enum": 34, "operation": 459}
EXPECTED_MODULES = 119

# layer → tiền tố import được phép trong abc_fashion; và thư viện ngoài bị cấm
ALLOWED = {
    "model": ("abc_fashion.model",),
    "control.dao": ("abc_fashion.control.dao", "abc_fashion.model"),
    "control.gateway": ("abc_fashion.control.gateway", "abc_fashion.model"),
    "controller": ("abc_fashion.controller", "abc_fashion.control.dao", "abc_fashion.control.gateway",
                   "abc_fashion.model"),
    "view": ("abc_fashion.view", "abc_fashion.controller", "abc_fashion.model"),
    "web": ("abc_fashion_web", "abc_fashion.controller", "abc_fashion.model", "abc_fashion.view._format"),
    "main": ("abc_fashion.",),
}
FORBIDDEN_EXTERNAL = {
    "model": ("psycopg", "tkinter", "tkcalendar", "PIL", "requests"),
    "control.dao": ("tkinter", "tkcalendar"),
    "control.gateway": ("psycopg", "tkinter", "tkcalendar"),
    "controller": ("psycopg", "tkinter", "tkcalendar", "flask"),
    "view": ("psycopg",),
    "web": ("psycopg", "tkinter", "tkcalendar"),
    "main": ("psycopg",),
}
NO_SQL = ("view", "controller", "web")
SQL_RE = re.compile(r"\b(SELECT\s.+\sFROM|INSERT\s+INTO|UPDATE\s+\"|DELETE\s+FROM)\b", re.I | re.S)


def layer_of(module: str) -> str:
    parts = module.split(".")
    if parts[0] == "abc_fashion_web":
        return "web"
    if module == "abc_fashion.main":
        return "main"
    if parts[1] == "control":
        return "control." + parts[2] if len(parts) > 2 else "control"
    return parts[1]


def web_files(root: str) -> dict[str, str]:
    """Module của ứng dụng web (nếu có) — chỉ kiểm tra quy tắc layer, không tính vào số lớp của mô hình."""
    out = {}
    for dirpath, _, files in os.walk(os.path.join(root, "abc_fashion_web")):
        for name in files:
            if name.endswith(".py"):
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root)[:-3].replace(os.sep, ".")
                out[rel.removesuffix(".__init__")] = path
    return dict(sorted(out.items()))


def module_files(root: str) -> dict[str, str]:
    out = {}
    base = os.path.join(root, "abc_fashion")
    for dirpath, _, files in os.walk(base):
        for name in files:
            if name.endswith(".py"):
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, root)[:-3].replace(os.sep, ".")
                out[rel.removesuffix(".__init__")] = path
    return dict(sorted(out.items()))


def imports_of(path: str, module: str) -> list[str]:
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:                               # import tương đối
                pkg = module.rsplit(".", node.level)[0]
                names.append(f"{pkg}.{node.module}" if node.module else pkg)
            else:
                names.append(node.module)
    return names


def check_layers(files: dict[str, str]) -> list[str]:
    errors = []
    for module, path in files.items():
        if module == "abc_fashion" or module.count(".") < 1:
            continue
        layer = layer_of(module)
        if layer not in ALLOWED:
            continue
        for name in imports_of(path, module):
            top = name.split(".")[0]
            if top in ("abc_fashion", "abc_fashion_web"):
                if not name.startswith(ALLOWED[layer]) and name not in ("abc_fashion", "abc_fashion_web"):
                    errors.append(f"{module}: layer {layer} không được import {name}")
            elif top in FORBIDDEN_EXTERNAL[layer]:
                errors.append(f"{module}: layer {layer} không được import {top}")
        if layer in NO_SQL:
            tree = ast.parse(open(path, encoding="utf-8").read(), path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and SQL_RE.search(node.value):
                    errors.append(f"{module}:{node.lineno}: câu SQL trong {layer}")
    return errors


def count_classes(modules: list[types.ModuleType]) -> dict[str, int]:
    seen = {}
    for m in modules:
        for name, obj in vars(m).items():
            if inspect.isclass(obj) and obj.__module__ == m.__name__:
                seen[obj.__qualname__ + "@" + m.__name__] = (m.__name__, obj)
    c = dict.fromkeys(("view", "controller", "dao", "gateway", "entity", "enum", "operation"), 0)
    for module, cls in seen.values():
        layer = layer_of(module)
        if layer == "view" and cls.__name__.endswith("Frm"):
            c["view"] += 1
        elif layer == "controller" and cls.__name__.endswith("Controller"):
            c["controller"] += 1
        elif layer == "control.dao" and cls.__name__.endswith("DAO"):
            c["dao"] += 1
        elif layer == "control.gateway":
            if module.rsplit(".", 1)[-1].startswith("_"):     # module hỗ trợ (vd. _http) không phải một gateway
                continue
            c["gateway"] += 1
        elif layer == "model" and issubclass(cls, enum.Enum):
            c["enum"] += 1
            continue
        elif layer == "model" and dataclasses.is_dataclass(cls):
            c["entity"] += 1
            continue
        else:
            continue
        # operation của mô hình = hàm công khai (kể cả staticmethod) + constructor của Frm và của lớp gốc DAO
        has_init = cls.__name__.endswith("Frm") or cls.__name__ == "DAO"
        c["operation"] += sum(1 for n, f in vars(cls).items()
                              if (inspect.isfunction(f) or isinstance(f, staticmethod))
                              and (not n.startswith("_") or (n == "__init__" and has_init)))
    return c


def main(root: str) -> int:
    root = os.path.abspath(root)
    sys.path.insert(0, root)
    files = module_files(root)
    design = [m for m in files if not m.rsplit(".", 1)[-1].startswith("_") and m != "abc_fashion"
              and not os.path.basename(files[m]) == "__init__.py"]
    modules, import_errors = [], []
    for name in files:
        try:
            modules.append(importlib.import_module(name))
        except Exception as e:                            # noqa: BLE001
            import_errors.append(f"{name}: {type(e).__name__}: {e}")
    layer_errors = check_layers(files) + check_layers(web_files(root))
    counts = count_classes(modules)
    print(f"imported modules: {len(design)} / layer violations: {len(layer_errors)} / {counts}")
    for e in import_errors + layer_errors:
        print("  ✗", e)
    mismatch = {k: (counts[k], v) for k, v in EXPECTED.items() if counts[k] != v}
    if len(design) != EXPECTED_MODULES:
        mismatch["modules"] = (len(design), EXPECTED_MODULES)
    for k, (got, want) in mismatch.items():
        print(f"  ✗ {k}: {got} (mô hình: {want})")
    return 1 if (import_errors or layer_errors or mismatch) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))))
