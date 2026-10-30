"""MarketingHomeFrm — Trang chủ marketing (cũng dùng tạm cho vai trò SALES — mục 13 #7)."""
from __future__ import annotations

import tkinter as tk

from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import guarded, home_window, label, logout
from abc_fashion.view.report.select_report_frm import SelectReportFrm


class MarketingHomeFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        home_window(self, label(staff.role), f"Xin chào {staff.full_name} ({label(staff.role).lower()})", [
            ("btn_view_report", "Báo cáo", self.on_view_report),
            ("btn_logout", "Đăng xuất", self.on_logout)])

    @guarded
    def on_view_report(self) -> None:
        SelectReportFrm(self.staff)

    def on_logout(self) -> None:
        logout(self)
