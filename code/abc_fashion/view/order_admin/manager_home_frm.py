"""ManagerHomeFrm — Trang chủ quản lý."""
from __future__ import annotations

import tkinter as tk

from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import guarded, home_window, logout
from abc_fashion.view.order_admin.search_order_frm import SearchOrderFrm
from abc_fashion.view.product.manage_style_frm import ManageStyleFrm
from abc_fashion.view.report.select_report_frm import SelectReportFrm
from abc_fashion.view.returns.search_return_request_frm import SearchReturnRequestFrm


class ManagerHomeFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        home_window(self, "Quản lý", f"Xin chào {staff.full_name} (quản lý)", [
            ("btn_manage_order", "Quản lý đơn hàng", self.on_manage_order),
            ("btn_manage_product", "Quản lý sản phẩm", self.on_manage_product),
            ("btn_process_return", "Xử lý trả / đổi hàng", self.on_process_return),
            ("btn_view_report", "Báo cáo", self.on_view_report),
            ("btn_logout", "Đăng xuất", self.on_logout)])

    @guarded
    def on_manage_order(self) -> None:
        SearchOrderFrm(self.staff)

    @guarded
    def on_manage_product(self) -> None:
        ManageStyleFrm(self.staff)

    @guarded
    def on_process_return(self) -> None:
        SearchReturnRequestFrm(self.staff)

    @guarded
    def on_view_report(self) -> None:
        SelectReportFrm(self.staff)

    def on_logout(self) -> None:
        logout(self)
