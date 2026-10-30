"""EditStyleFrm — Thêm / sửa style với vật liệu, bảng cỡ, media, biến thể (UC21)."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, ttk

from abc_fashion.controller.product_controller import ProductController
from abc_fashion.model.catalogue import (FitType, Measure, StyleStatus, Category, Collection, MaterialComponent,
                                         ProductMedia, ProductVariant, SizeChartEntry, Style)
from abc_fashion.model.user import StaffMember, Supplier
from abc_fashion.view._util import (ERROR_FG, OK_FG, ChoiceBox, body, confirm, entry_set, enum_choices, fill_table, guarded,
                                    info, label, make_table, message_label, modal, money, read_file, selected, show,
                                    text_get, text_set, to_float, warn)
from abc_fashion.view.product.edit_variant_frm import EditVariantFrm


class EditStyleFrm(tk.Toplevel):
    def __init__(self, staff: StaffMember, style: Style | None):
        super().__init__()
        self.staff = staff
        self.product_controller = ProductController()
        self.list_category: list[Category] = self.product_controller.get_categories()
        self.list_supplier: list[Supplier] = self.product_controller.get_suppliers()
        self.list_collection: list[Collection] = self.product_controller.get_collections()
        self.style = style or Style(status=StyleStatus.DRAFT)
        self.list_material: list[MaterialComponent] = []
        self.list_size_entry: list[SizeChartEntry] = []
        self.list_media: list[ProductMedia] = []
        self.list_variant: list[ProductVariant] = []
        self._build()
        self.on_reset()

    # ---------- giao diện ----------
    def _build(self) -> None:
        f = body(self, "Sản phẩm")
        nb = ttk.Notebook(f)
        nb.pack(fill="both", expand=True)
        g = ttk.Frame(nb, padding=8)
        nb.add(g, text="Thông tin")
        self.txt_code, self.txt_name, self.txt_brand = ttk.Entry(g, width=40), ttk.Entry(g, width=40), ttk.Entry(g, width=40)
        self.txa_description = tk.Text(g, height=4, width=52, wrap="word")
        self.cbo_fit_type = ChoiceBox(g, [("—", None)] + enum_choices(FitType))
        self.txt_care_instructions, self.txt_features = ttk.Entry(g, width=52), ttk.Entry(g, width=52)
        self.txt_model_info = ttk.Entry(g, width=52)
        self.cbo_status = ChoiceBox(g, enum_choices(StyleStatus))
        self.cbo_category = ChoiceBox(g, [(c.name, c) for c in self.list_category])
        self.cbo_supplier = ChoiceBox(g, [(s.name, s) for s in self.list_supplier], width=30)
        self.cbo_collection = ChoiceBox(g, [("—", None)] + [(c.name, c) for c in self.list_collection])
        for r, (t, w) in enumerate([("Mã", self.txt_code), ("Tên", self.txt_name), ("Mô tả", self.txa_description),
                                    ("Thương hiệu", self.txt_brand), ("Dáng", self.cbo_fit_type),
                                    ("Bảo quản", self.txt_care_instructions), ("Đặc điểm", self.txt_features),
                                    ("Thông tin người mẫu", self.txt_model_info), ("Trạng thái", self.cbo_status),
                                    ("Danh mục", self.cbo_category), ("Nhà cung cấp", self.cbo_supplier),
                                    ("Bộ sưu tập", self.cbo_collection)]):
            ttk.Label(g, text=t).grid(row=r, column=0, sticky="nw", pady=2, padx=(0, 6))
            w.grid(row=r, column=1, sticky="w", pady=2)

        m = ttk.Frame(nb, padding=8)
        nb.add(m, text="Vật liệu")
        self.tbl_material = make_table(m, [("material", "Vật liệu", 200), ("pct", "%", 60)], height=6)
        self.tbl_material.box.grid(row=0, column=0, columnspan=5, sticky="nsew")
        self.txt_material = ttk.Entry(m, width=20)
        self.txt_material.grid(row=1, column=0, pady=4)
        self.spn_percent = ttk.Spinbox(m, from_=1, to=100, width=5)
        self.spn_percent.set(100)
        self.spn_percent.grid(row=1, column=1)
        self.btn_add_material = ttk.Button(m, text="Thêm", command=self.on_add_material)
        self.btn_add_material.grid(row=1, column=2, padx=3)
        ttk.Button(m, text="Xoá dòng", command=lambda: self._remove(self.tbl_material, self.list_material)).grid(row=1, column=3)
        self.lbl_material_total = ttk.Label(m)
        self.lbl_material_total.grid(row=1, column=4, padx=8)

        s = ttk.Frame(nb, padding=8)
        nb.add(s, text="Bảng cỡ")
        self.tbl_size_chart = make_table(s, [("size", "Cỡ", 80), ("measure", "Số đo", 120), ("cm", "cm", 70)], height=6)
        self.tbl_size_chart.box.grid(row=0, column=0, columnspan=5, sticky="nsew")
        self.txt_size_label = ttk.Entry(s, width=8)
        self.txt_size_label.grid(row=1, column=0, pady=4)
        self.cbo_measure = ChoiceBox(s, [(x.value, x) for x in Measure], width=12)
        self.cbo_measure.grid(row=1, column=1, padx=3)
        self.txt_value_cm = ttk.Entry(s, width=8)
        self.txt_value_cm.grid(row=1, column=2)
        self.btn_add_size_entry = ttk.Button(s, text="Thêm", command=self.on_add_size_entry)
        self.btn_add_size_entry.grid(row=1, column=3, padx=3)
        ttk.Button(s, text="Xoá dòng", command=lambda: self._remove(self.tbl_size_chart, self.list_size_entry)).grid(row=1, column=4)

        md = ttk.Frame(nb, padding=8)
        nb.add(md, text="Ảnh / video")
        self.tbl_media = make_table(md, [("order", "#", 40), ("url", "Đường dẫn", 300), ("type", "Loại", 70),
                                         ("colour", "Màu", 80)], height=6)
        self.tbl_media.box.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.btn_upload_media = ttk.Button(md, text="Tải lên…", command=self.on_upload_media)
        self.btn_upload_media.grid(row=1, column=0, sticky="w", pady=4)
        ttk.Button(md, text="Xoá", command=self._delete_media).grid(row=1, column=1, sticky="w")

        v = ttk.Frame(nb, padding=8)
        nb.add(v, text="Biến thể")
        self.tbl_variant = make_table(v, [("sku", "SKU", 120), ("colour", "Màu", 80), ("size", "Cỡ", 60),
                                          ("price", "Giá", 90), ("status", "Trạng thái", 90), ("loc", "Kho", 110),
                                          ("avail", "Có thể bán", 80)], height=6)
        self.tbl_variant.box.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.tbl_variant.bind("<Double-1>", lambda e: self.on_edit_variant())
        self.btn_add_variant = ttk.Button(v, text="Thêm biến thể", command=self.on_add_variant)
        self.btn_add_variant.grid(row=1, column=0, sticky="w", pady=4)
        self.btn_edit_variant = ttk.Button(v, text="Sửa biến thể", command=self.on_edit_variant)
        self.btn_edit_variant.grid(row=1, column=1, sticky="w")

        self.lbl_message = message_label(f)
        self.lbl_message.pack(anchor="w")
        bar = ttk.Frame(f)
        bar.pack(anchor="e", pady=4)
        self.btn_reset = ttk.Button(bar, text="Khôi phục", command=self.on_reset)
        self.btn_reset.pack(side="left", padx=3)
        self.btn_save = ttk.Button(bar, text="Lưu", command=self.on_save)
        self.btn_save.pack(side="left")

    def _refresh_tables(self) -> None:
        fill_table(self.tbl_material, [(k, (x.material, x.percent)) for k, x in enumerate(self.list_material)])
        total = sum(x.percent for x in self.list_material)
        self.lbl_material_total.config(text=f"Tổng {total}%", foreground=OK_FG if total == 100 else ERROR_FG)
        fill_table(self.tbl_size_chart, [(k, (x.size_label, x.measure.value, f"{x.value_cm:g}"))
                                         for k, x in enumerate(self.list_size_entry)])
        fill_table(self.tbl_media, [(x.id, (x.sort_order, x.url, label(x.media_type), x.colour or ""))
                                    for x in self.list_media])
        fill_table(self.tbl_variant, [(x.id, (x.sku, x.colour, x.size_label, money(x.price), label(x.status),
                                              getattr(x, "location_name", "") or "", getattr(x, "available", "")))
                                      for x in self.list_variant])

    def _remove(self, tree: ttk.Treeview, items: list) -> None:
        sel = tree.selection()
        if sel:
            del items[int(sel[0])]
            self._refresh_tables()

    # ---------- handler ----------
    @guarded
    def on_add_material(self) -> None:
        try:
            pct = int(self.spn_percent.get())
        except ValueError:
            pct = 0
        material = self.product_controller.make_material(self.txt_material.get(), pct)
        if sum(x.percent for x in self.list_material) + pct > 100:
            warn(self, "Tổng thành phần vượt 100%")
        self.list_material.append(material)
        self.txt_material.delete(0, "end")
        self._refresh_tables()

    @guarded
    def on_add_size_entry(self) -> None:
        entry = self.product_controller.make_size_entry(self.txt_size_label.get(), self.cbo_measure.value(),
                                                        to_float(self.txt_value_cm.get()))
        self.list_size_entry = [e for e in self.list_size_entry
                                if not (e.size_label == entry.size_label and e.measure == entry.measure)] + [entry]
        self.txt_value_cm.delete(0, "end")
        self._refresh_tables()

    @guarded
    def on_upload_media(self) -> None:
        if not self.style.id:
            return warn(self, "Lưu sản phẩm trước khi tải ảnh lên")
        path = filedialog.askopenfilename(parent=self, filetypes=[("Ảnh / video", "*.jpg *.jpeg *.png *.mp4"),
                                                                  ("Tất cả", "*.*")])
        if not path:
            return
        self.product_controller.upload_media(self.style, os.path.basename(path), read_file(path))
        self.list_media = self.product_controller.get_media(self.style)
        self._refresh_tables()

    def _delete_media(self) -> None:
        media = selected(self.tbl_media, self.list_media)
        if media is None or not confirm(self, "Xoá ảnh / video này?"):
            return
        self.product_controller.delete_media(media)
        self.list_media = self.product_controller.get_media(self.style)
        self._refresh_tables()

    @guarded
    def on_add_variant(self) -> None:
        if not self.style.id:
            return warn(self, "Lưu sản phẩm trước khi thêm biến thể")
        modal(EditVariantFrm(self.staff, self.style, None), self)
        self.list_variant = self.product_controller.get_variants(self.style)
        self._refresh_tables()

    @guarded
    def on_edit_variant(self) -> None:
        v = selected(self.tbl_variant, self.list_variant)
        if v is None:
            return warn(self, "Chọn một biến thể")
        modal(EditVariantFrm(self.staff, self.style, v), self)
        self.list_variant = self.product_controller.get_variants(self.style)
        self._refresh_tables()

    @guarded
    def on_save(self) -> None:
        cat, sup, col = self.cbo_category.value(), self.cbo_supplier.value(), self.cbo_collection.value()
        draft = Style(code=self.txt_code.get().strip(), name=self.txt_name.get().strip(),
                      description=text_get(self.txa_description) or None, brand=self.txt_brand.get().strip() or None,
                      fit_type=self.cbo_fit_type.value(),
                      care_instructions=self.txt_care_instructions.get().strip() or None,
                      features=self.txt_features.get().strip() or None,
                      model_info=self.txt_model_info.get().strip() or None, status=self.cbo_status.value(),
                      categoryId=cat.id if cat else None, supplierId=sup.id if sup else None,
                      collectionId=col.id if col else None)
        is_new = self.style.id is None
        self.product_controller.save_style(self.staff, self.style, draft, self.list_material, self.list_size_entry)
        show(self.lbl_message, "Đã lưu", ok=True)
        if is_new:
            info(self, "Đã tạo sản phẩm ở trạng thái nháp. Hãy thêm biến thể rồi chuyển sang Đang bán.")
        self.on_reset()

    def on_reset(self) -> None:
        self.style = s = self.product_controller.get_style_for_edit(self.style)
        self.list_material, self.list_size_entry = list(s.materials), list(s.size_chart)
        self.list_media, self.list_variant = list(s.media), list(s.variants)
        for w, value in ((self.txt_code, s.code), (self.txt_name, s.name), (self.txt_brand, s.brand),
                         (self.txt_care_instructions, s.care_instructions), (self.txt_features, s.features),
                         (self.txt_model_info, s.model_info)):
            entry_set(w, value)
        text_set(self.txa_description, s.description or "")
        self.cbo_fit_type.select_value(s.fit_type)
        self.cbo_status.select_value(s.status)
        by_id = lambda x: x.id if hasattr(x, "id") else x                                    # noqa: E731
        self.cbo_category.select_value(s.categoryId, key=by_id)
        self.cbo_supplier.select_value(s.supplierId, key=by_id)
        self.cbo_collection.select_value(s.collectionId, key=by_id)
        self.txt_code.config(state="disabled" if s.id else "normal")
        self.title(f"ABC Fashion — Sản phẩm {s.code or '(mới)'}")
        self._refresh_tables()
