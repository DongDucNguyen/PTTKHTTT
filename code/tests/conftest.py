"""Cấu hình pytest. Kiểm thử CSDL chạy trên CSDL riêng đặt ở ABC_FASHION_TEST_DSN (vd. dbname=abc_fashion_test ...).

Không đặt biến này thì các test cần CSDL bị bỏ qua (skip); test thuần vẫn chạy.
"""
from __future__ import annotations

import os
import sys

import pytest

CODE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, CODE_DIR)
sys.path.insert(0, os.path.join(CODE_DIR, "db"))

TEST_DSN = os.environ.get("ABC_FASHION_TEST_DSN")


@pytest.fixture(scope="session")
def test_dsn():
    if not TEST_DSN:
        pytest.skip("Đặt ABC_FASHION_TEST_DSN để chạy kiểm thử CSDL")
    if "abc_fashion_v2" in TEST_DSN:
        pytest.exit("ABC_FASHION_TEST_DSN không được trỏ vào CSDL thật abc_fashion_v2")
    import setup_db
    setup_db.setup(TEST_DSN, reset=True, seed=False)
    return TEST_DSN


@pytest.fixture()
def db(test_dsn):
    """CSDL thử sạch cho mỗi test: tạo lại schema + seed; DAO dùng kết nối tới CSDL thử."""
    import psycopg
    import setup_db
    from abc_fashion.control.dao import dao

    if dao.DAO._shared is not None and not dao.DAO._shared.closed:
        dao.DAO._shared.close()
    dao.DAO._shared = None
    with psycopg.connect(test_dsn, autocommit=True) as con:
        con.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    setup_db.run_script(test_dsn, "schema.sql")
    setup_db.run_script(test_dsn, "seed.sql")
    dao.DSN = test_dsn
    yield dao.DAO().con
    if dao.DAO._shared is not None:
        dao.DAO._shared.close()
    dao.DAO._shared = None


@pytest.fixture(scope="session")
def tk_root():
    """Một Tk cho cả phiên: tạo Tcl interpreter lần hai trên Windows đôi khi lỗi 'Can't find a usable init.tcl'."""
    import tkinter as tk
    try:
        root = tk.Tk()
    except tk.TclError as e:
        pytest.skip(f"Không có màn hình cho tkinter: {e}")
    from abc_fashion.view._util import apply_theme
    apply_theme(root)                       # chạy màn hình với theme thật (uiux-design.md)
    root.withdraw()
    yield root
    root.destroy()
