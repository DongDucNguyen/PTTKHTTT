"""MerchandiserHomeFrm — Trang chủ merchandiser."""
from __future__ import annotations

import tkinter as tk

from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import guarded, home_window, logout
from abc_fashion.view.promotion.manage_promotion_frm import ManagePromotionFrm
from abc_fashion.view.report.select_report_frm import SelectReportFrm


class MerchandiserHomeFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        home_window(self, "Merchandiser", f"Xin chào {staff.full_name} (merchandiser)", [
            ("btn_manage_promotion", "Quản lý khuyến mãi", self.on_manage_promotion),
            ("btn_view_report", "Báo cáo", self.on_view_report),
            ("btn_logout", "Đăng xuất", self.on_logout)])

    @guarded
    def on_manage_promotion(self) -> None:
        ManagePromotionFrm(self.staff)

    @guarded
    def on_view_report(self) -> None:
        SelectReportFrm(self.staff)

    def on_logout(self) -> None:
        logout(self)
