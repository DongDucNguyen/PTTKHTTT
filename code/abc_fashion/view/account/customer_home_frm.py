"""CustomerHomeFrm — Trang chủ của khách: tìm kiếm và đi tới các chức năng."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from abc_fashion.model.user import Customer
from abc_fashion.view import _theme
from abc_fashion.view._util import body, guarded, logout
from abc_fashion.view.account.profile_frm import ProfileFrm
from abc_fashion.view.catalogue.browse_style_frm import BrowseStyleFrm
from abc_fashion.view.catalogue.search_style_frm import SearchStyleFrm
from abc_fashion.view.checkout.cart_frm import CartFrm
from abc_fashion.view.order.order_list_frm import OrderListFrm


class CustomerHomeFrm(tk.Toplevel):
    def __init__(self, customer: Customer):
        super().__init__()
        self.customer = customer
        self._build()

    def _build(self) -> None:
        """uiux-design.md 7.2: header lớn có lời chào, thanh tìm kiếm, lưới ô chức năng."""
        f = body(self, "Trang chủ", padding=24, header=False)
        hero = _theme.header(self, f"Xin chào {self.customer.full_name}", "Hôm nay bạn muốn tìm gì?", tall=True)
        hero.pack_forget()
        hero.pack(side="top", fill="x", before=f)
        bar = ttk.Frame(f)
        bar.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, _theme.px(self, 18)))
        self.txt_keyword = ttk.Entry(bar, width=36)
        self.txt_keyword.pack(side="left", fill="x", expand=True, ipady=_theme.px(self, 2))
        self.txt_keyword.bind("<Return>", lambda e: self.on_search())
        self.btn_search = ttk.Button(bar, text="Tìm", command=self.on_search, style="Primary.TButton",
                                     image=_theme.icon(self, "search", 18, "#FFFFFF"), compound="left")
        self.btn_search.pack(side="left", padx=(_theme.px(self, 8), 0))
        self.btn_search_by_image = ttk.Button(bar, text="Tìm bằng ảnh", command=self.on_search_by_image,
                                              image=_theme.icon(self, "image", 18), compound="left")
        self.btn_search_by_image.pack(side="left", padx=(_theme.px(self, 8), 0))
        tiles = [("btn_browse", "Duyệt danh mục", self.on_browse), ("btn_cart", "Giỏ hàng", self.on_cart),
                 ("btn_orders", "Đơn hàng của tôi", self.on_orders), ("btn_profile", "Hồ sơ", self.on_profile)]
        for i, (attr, text, cmd) in enumerate(tiles):
            btn = ttk.Button(f, text=text, command=cmd, style="Tile.TButton", compound="left", width=22,
                             image=_theme.icon(self, _theme.ICON_FOR[attr]))
            btn.grid(row=1 + i // 2, column=i % 2, sticky="we", padx=_theme.px(self, 6), pady=_theme.px(self, 6))
            setattr(self, attr, btn)
        self.btn_logout = ttk.Button(f, text="Đăng xuất", command=self.on_logout, style="Link.TButton",
                                     image=_theme.icon(self, "logout", 18), compound="left")
        self.btn_logout.grid(row=3, column=1, sticky="e", pady=(_theme.px(self, 12), 0))
        f.columnconfigure((0, 1), weight=1, uniform="tile")
        self.resizable(False, False)

    @guarded
    def on_search(self) -> None:
        SearchStyleFrm(self.customer, self.txt_keyword.get().strip())

    @guarded
    def on_search_by_image(self) -> None:
        frm = SearchStyleFrm(self.customer, "")
        frm.on_search_by_image()

    @guarded
    def on_browse(self) -> None:
        BrowseStyleFrm(self.customer)

    @guarded
    def on_cart(self) -> None:
        CartFrm(self.customer)

    @guarded
    def on_orders(self) -> None:
        OrderListFrm(self.customer)

    @guarded
    def on_profile(self) -> None:
        ProfileFrm(self.customer)

    def on_logout(self) -> None:
        logout(self)
