"""AdminHomeFrm — Trang chủ quản trị viên."""
from __future__ import annotations

import tkinter as tk

from abc_fashion.model.user import StaffMember
from abc_fashion.view._util import guarded, home_window, logout
from abc_fashion.view.account.audit_log_frm import AuditLogFrm
from abc_fashion.view.account.search_account_frm import SearchAccountFrm
from abc_fashion.view.product.manage_style_frm import ManageStyleFrm
from abc_fashion.view.review.manage_review_frm import ManageReviewFrm


class AdminHomeFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember):
        super().__init__()
        self.staff = staff
        home_window(self, "Quản trị viên", f"Xin chào {staff.full_name} (quản trị viên)", [
            ("btn_manage_account", "Quản lý tài khoản", self.on_manage_account),
            ("btn_manage_product", "Quản lý sản phẩm", self.on_manage_product),
            ("btn_manage_review", "Duyệt đánh giá", self.on_manage_review),
            ("btn_view_audit_log", "Nhật ký thay đổi", self.on_view_audit_log),
            ("btn_logout", "Đăng xuất", self.on_logout)])

    @guarded
    def on_manage_account(self) -> None:
        SearchAccountFrm(self.staff)

    @guarded
    def on_manage_product(self) -> None:
        ManageStyleFrm(self.staff)

    @guarded
    def on_manage_review(self) -> None:
        ManageReviewFrm(self.staff)

    @guarded
    def on_view_audit_log(self) -> None:
        AuditLogFrm(self.staff)

    def on_logout(self) -> None:
        logout(self)
