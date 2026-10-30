"""ProfileFrm — Hồ sơ khách: thông tin, sổ địa chỉ, phương thức thanh toán, cỡ đã lưu (UC03)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.controller._errors import BusinessError
from abc_fashion.controller.profile_controller import ProfileController
from abc_fashion.model.customer_data import Address, PaymentMethod, SavedSize
from abc_fashion.model.user import Customer
from abc_fashion.view._util import (ChoiceBox, body, confirm, entry_set, fill_table, form_rows, guarded, info, label,
                                    make_table, message_label, modal, selected, show, warn)
from abc_fashion.view.account.edit_address_frm import EditAddressFrm
from abc_fashion.view.account.link_payment_method_frm import LinkPaymentMethodFrm


class ProfileFrm(tk.Toplevel):
    def __init__(self, customer: Customer):
        super().__init__()
        self.customer = customer
        self.profile_controller = ProfileController()
        self.list_address: list[Address] = []
        self.list_payment_method: list[PaymentMethod] = []
        self.list_saved_size: list[SavedSize] = []
        self._build()
        entry_set(self.txt_full_name, customer.full_name)
        entry_set(self.txt_phone, customer.phone)
        entry_set(self.txt_preferred_colours, ", ".join(customer.preferred_colours or []))
        self.var_marketing_consent.set(bool(customer.marketing_consent))
        self.cbo_category.set_choices([(c.name, c) for c in self.profile_controller.get_categories()])
        self._reload()

    def _build(self) -> None:
        f = body(self, "Hồ sơ")
        nb = ttk.Notebook(f)
        nb.pack(fill="both", expand=True)

        info_tab = ttk.Frame(nb, padding=10)
        nb.add(info_tab, text="Thông tin")
        self.txt_full_name = ttk.Entry(info_tab, width=34)
        self.txt_phone = ttk.Entry(info_tab, width=34)
        self.txt_preferred_colours = ttk.Entry(info_tab, width=34)
        self.var_marketing_consent = tk.BooleanVar()
        self.chk_marketing_consent = ttk.Checkbutton(info_tab, text="Nhận tin khuyến mãi",
                                                     variable=self.var_marketing_consent)
        r = form_rows(info_tab, [("E-mail", ttk.Label(info_tab, text=self.customer.email)),
                                 ("Họ tên", self.txt_full_name), ("Điện thoại", self.txt_phone),
                                 ("Màu yêu thích (phẩy)", self.txt_preferred_colours), ("", self.chk_marketing_consent)])
        self.lbl_message = message_label(info_tab)
        self.lbl_message.grid(row=r, column=0, columnspan=2, sticky="w")
        self.btn_save = ttk.Button(info_tab, text="Lưu thông tin", command=self.on_save)
        self.btn_save.grid(row=r + 1, column=1, sticky="e", pady=6)

        addr_tab = ttk.Frame(nb, padding=10)
        nb.add(addr_tab, text="Sổ địa chỉ")
        self.tbl_address = make_table(addr_tab, [("name", "Người nhận", 140), ("phone", "Điện thoại", 100),
                                                 ("addr", "Địa chỉ", 340), ("def", "Mặc định", 70)])
        self.tbl_address.box.pack(fill="both", expand=True)
        bar = ttk.Frame(addr_tab)
        bar.pack(anchor="e", pady=6)
        self.btn_add_address = ttk.Button(bar, text="Thêm", command=self.on_add_address)
        self.btn_edit_address = ttk.Button(bar, text="Sửa", command=self.on_edit_address)
        self.btn_delete_address = ttk.Button(bar, text="Xoá", command=self.on_delete_address)
        for b in (self.btn_add_address, self.btn_edit_address, self.btn_delete_address):
            b.pack(side="left", padx=3)

        pay_tab = ttk.Frame(nb, padding=10)
        nb.add(pay_tab, text="Thanh toán")
        self.tbl_payment_method = make_table(pay_tab, [("type", "Loại", 120), ("provider", "Nhà cung cấp", 140),
                                                       ("number", "Số", 120), ("def", "Mặc định", 70)])
        self.tbl_payment_method.box.pack(fill="both", expand=True)
        bar = ttk.Frame(pay_tab)
        bar.pack(anchor="e", pady=6)
        self.btn_link_payment_method = ttk.Button(bar, text="Liên kết mới", command=self.on_link_payment_method)
        self.btn_remove_payment_method = ttk.Button(bar, text="Gỡ liên kết", command=self.on_remove_payment_method)
        self.btn_link_payment_method.pack(side="left", padx=3)
        self.btn_remove_payment_method.pack(side="left", padx=3)

        size_tab = ttk.Frame(nb, padding=10)
        nb.add(size_tab, text="Cỡ đã lưu")
        self.tbl_saved_size = make_table(size_tab, [("cat", "Danh mục", 200), ("size", "Cỡ", 100)], height=6)
        self.tbl_saved_size.box.pack(fill="both", expand=True)
        bar = ttk.Frame(size_tab)
        bar.pack(anchor="e", pady=6)
        self.cbo_category = ChoiceBox(bar, width=18)
        self.cbo_category.pack(side="left")
        self.txt_size_label = ttk.Entry(bar, width=8)
        self.txt_size_label.pack(side="left", padx=4)
        self.btn_save_size = ttk.Button(bar, text="Lưu cỡ", command=self.on_save_size)
        self.btn_save_size.pack(side="left")

    def _reload(self) -> None:
        self.list_address = self.profile_controller.get_addresses(self.customer)
        self.list_payment_method = self.profile_controller.get_payment_methods(self.customer)
        self.list_saved_size = self.profile_controller.get_saved_sizes(self.customer)
        fill_table(self.tbl_address, [(a.id, (a.recipient_name, a.phone, a.one_line(), "✓" if a.is_default else ""))
                                      for a in self.list_address])
        fill_table(self.tbl_payment_method, [(m.id, (label(m.method_type), m.provider, m.masked_number,
                                                     "✓" if m.is_default else "")) for m in self.list_payment_method])
        fill_table(self.tbl_saved_size, [(s.id, (getattr(s, "category_name", ""), s.size_label))
                                         for s in self.list_saved_size])

    @guarded
    def on_save(self) -> None:
        if self.profile_controller.update_profile(self.customer, self.txt_full_name.get(), self.txt_phone.get(),
                                                  self.txt_preferred_colours.get().split(","),
                                                  self.var_marketing_consent.get()):
            show(self.lbl_message, "Đã lưu", ok=True)

    @guarded
    def on_add_address(self) -> None:
        modal(EditAddressFrm(self.customer, None), self)
        self._reload()

    @guarded
    def on_edit_address(self) -> None:
        a = selected(self.tbl_address, self.list_address)
        if a is None:
            return warn(self, "Chọn một địa chỉ")
        modal(EditAddressFrm(self.customer, a), self)
        self._reload()

    @guarded
    def on_delete_address(self) -> None:
        a = selected(self.tbl_address, self.list_address)
        if a is None:
            return warn(self, "Chọn một địa chỉ")
        if not confirm(self, "Xoá địa chỉ này?"):
            return
        try:
            self.profile_controller.delete_address(a)
        except BusinessError as e:
            warn(self, str(e))
        self._reload()

    @guarded
    def on_link_payment_method(self) -> None:
        modal(LinkPaymentMethodFrm(self.customer), self)
        self._reload()

    @guarded
    def on_remove_payment_method(self) -> None:
        m = selected(self.tbl_payment_method, self.list_payment_method)
        if m is None:
            return warn(self, "Chọn một phương thức")
        if not confirm(self, f"Gỡ liên kết {m.provider} {m.masked_number}?"):
            return
        try:
            self.profile_controller.remove_payment_method(m)
        except BusinessError as e:
            warn(self, str(e))
        self._reload()

    @guarded
    def on_save_size(self) -> None:
        try:
            self.profile_controller.save_size(self.customer, self.cbo_category.value(), self.txt_size_label.get())
        except BusinessError as e:
            return warn(self, str(e))
        self._reload()
        info(self, "Đã lưu cỡ")
