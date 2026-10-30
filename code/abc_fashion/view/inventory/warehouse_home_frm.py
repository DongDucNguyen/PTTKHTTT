"""WarehouseHomeFrm — Trang chủ nhân viên kho."""
from __future__ import annotations

import tkinter as tk

from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import guarded, home_window, logout
from abc_fashion.view.inventory.manage_restock_frm import ManageRestockFrm
from abc_fashion.view.inventory.stock_level_frm import StockLevelFrm
from abc_fashion.view.returns.search_return_request_frm import SearchReturnRequestFrm


class WarehouseHomeFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        home_window(self, "Kho", f"Xin chào {staff.full_name} (kho)", [
            ("btn_view_stock", "Tồn kho", self.on_view_stock),
            ("btn_restock", "Phiếu nhập hàng", self.on_restock),
            ("btn_inspect_return", "Kiểm tra hàng trả về", self.on_inspect_return),
            ("btn_logout", "Đăng xuất", self.on_logout)])

    @guarded
    def on_view_stock(self) -> None:
        StockLevelFrm(self.staff)

    @guarded
    def on_restock(self) -> None:
        ManageRestockFrm(self.staff)

    @guarded
    def on_inspect_return(self) -> None:
        SearchReturnRequestFrm(self.staff)

    def on_logout(self) -> None:
        logout(self)
