"""ReportController — báo cáo doanh số / trả hàng theo sản phẩm (UC16, UC24)."""
from __future__ import annotations

import csv
from datetime import date

from abc_fashion.control.dao.category_dao import CategoryDAO
from abc_fashion.control.dao.collection_dao import CollectionDAO
from abc_fashion.control.dao.order_item_dao import OrderItemDAO
from abc_fashion.control.dao.return_item_dao import ReturnItemDAO
from abc_fashion.control.dao.return_stat_dao import ReturnStatDAO
from abc_fashion.control.dao.style_stat_dao import StyleStatDAO
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.catalogue import Category, Collection
from abc_fashion.model.returns import ReturnReason, ReturnItem
from abc_fashion.model.sales import OrderItem
from abc_fashion.model.stat import ReturnStat, StyleStat


def _check_period(start: date, end: date) -> None:
    if start > end:
        raise BusinessError("Ngày bắt đầu phải trước ngày kết thúc")


class ReportController:
    def __init__(self):
        self.style_stat_dao = StyleStatDAO()
        self.return_stat_dao = ReturnStatDAO()
        self.order_item_dao = OrderItemDAO()
        self.return_item_dao = ReturnItemDAO()
        self.category_dao = CategoryDAO()
        self.collection_dao = CollectionDAO()

    def get_categories(self) -> list[Category]:
        return self.category_dao.get_all_category()

    def get_collections(self) -> list[Collection]:
        return self.collection_dao.get_all_collection()

    def get_sales_report(self, start: date, end: date, category: Category | None,
                         collection: Collection | None) -> list[StyleStat]:
        _check_period(start, end)
        return self.style_stat_dao.get_style_stat(start, end, category, collection)

    def get_sales_detail(self, style_stat: StyleStat, start: date, end: date) -> list[OrderItem]:
        return self.order_item_dao.get_order_item_by_style(style_stat, start, end)

    def export_sales_csv(self, stats: list[StyleStat], path: str) -> int:
        """Ghi báo cáo doanh số ra CSV (BOM để Excel đọc đúng tiếng Việt); trả số dòng."""
        if not stats:
            raise BusinessError("Không có dữ liệu để xuất")
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["Mã", "Sản phẩm", "Số lượng bán", "Doanh thu (đ)", "Số đơn"])
            for s in stats:
                w.writerow([s.code, s.name, s.quantity_sold, s.revenue, s.order_count])
        return len(stats)

    def get_return_report(self, start: date, end: date, reason: ReturnReason | None) -> list[ReturnStat]:
        _check_period(start, end)
        return self.return_stat_dao.get_return_stat(start, end, reason)

    def get_return_detail(self, return_stat: ReturnStat, start: date, end: date) -> list[ReturnItem]:
        return self.return_item_dao.get_return_item_by_style(return_stat, start, end)
