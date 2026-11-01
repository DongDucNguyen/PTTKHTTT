# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.dao) -- do not edit the signatures.
from __future__ import annotations

import psycopg

DSN = "dbname=abc_fashion_v2 user=postgres host=localhost port=5432"


class DAO:
    """DAO -- layer abc_fashion.control.dao."""

    def __init__(self):
        self.con = psycopg.connect(DSN)
