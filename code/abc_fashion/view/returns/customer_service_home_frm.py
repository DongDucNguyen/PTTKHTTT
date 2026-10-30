"""CustomerServiceHomeFrm — Trang chủ chăm sóc khách hàng."""
from __future__ import annotations

import tkinter as tk

from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import guarded, home_window, logout
from abc_fashion.view.report.select_report_frm import SelectReportFrm
from abc_fashion.view.returns.search_return_request_frm import SearchReturnRequestFrm
from abc_fashion.view.review.manage_review_frm import ManageReviewFrm


class CustomerServiceHomeFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        home_window(self, "Chăm sóc khách hàng", f"Xin chào {staff.full_name} (CSKH)", [
            ("btn_process_return", "Xử lý trả / đổi hàng", self.on_process_return),
            ("btn_manage_review", "Duyệt đánh giá", self.on_manage_review),
            ("btn_view_report", "Báo cáo", self.on_view_report),
            ("btn_logout", "Đăng xuất", self.on_logout)])

    @guarded
    def on_process_return(self) -> None:
        SearchReturnRequestFrm(self.staff)

    @guarded
    def on_manage_review(self) -> None:
        ManageReviewFrm(self.staff)

    @guarded
    def on_view_report(self) -> None:
        SelectReportFrm(self.staff)

    def on_logout(self) -> None:
        logout(self)
