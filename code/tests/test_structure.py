"""Cấu trúc: 119 module import được, 0 vi phạm layer MVC, số lớp khớp mô hình; mã khớp project.xml (mục 12, 14.2)."""
import os

import pytest

import check_gen
import vp2py
from conftest import CODE_DIR

PROJECT_XML = os.path.join(os.path.dirname(CODE_DIR), "vp_export", "project.xml")
needs_model = pytest.mark.skipif(not os.path.exists(PROJECT_XML), reason="không có vp_export/project.xml")


def test_check_gen_passes(capsys):
    assert check_gen.main(CODE_DIR) == 0
    out = capsys.readouterr().out
    assert "imported modules: 119 / layer violations: 0" in out


def test_views_do_not_touch_control_layer():
    """MVC: view (desktop và web) chỉ đi qua controller; không import DAO / gateway / psycopg."""
    files = {**check_gen.module_files(CODE_DIR), **check_gen.web_files(CODE_DIR)}
    for module, path in files.items():
        if "." in module and check_gen.layer_of(module) in ("view", "web"):
            assert not [n for n in check_gen.imports_of(path, module)
                        if n.startswith("abc_fashion.control.") or n.split(".")[0] == "psycopg"], module


@needs_model
def test_code_matches_vp_model(capsys):
    assert vp2py.main([PROJECT_XML, "--check", CODE_DIR]) == 0
    assert "lệch mô hình: 0" in capsys.readouterr().out


@needs_model
def test_generated_skeleton_is_valid(tmp_path, capsys):
    assert vp2py.main([PROJECT_XML, str(tmp_path)]) == 0
    assert "generated modules: 119" in capsys.readouterr().out
    import subprocess
    import sys
    # chạy check_gen ở tiến trình riêng: bộ khung sinh ra cũng tên gói abc_fashion
    r = subprocess.run([sys.executable, os.path.join(CODE_DIR, "check_gen.py"), str(tmp_path)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
