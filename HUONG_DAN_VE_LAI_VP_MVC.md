# Hướng dẫn vẽ lại mô hình Visual Paradigm sau khi chuyển sang MVC

Tài liệu này liệt kê **chính xác** những gì phải sửa trong file `.vpp` để mô hình khớp với mã sau đợt tái cấu trúc MVC (2026-10-30). Các bảng ở phụ lục được sinh tự động từ mã, nên tên lớp, tên hàm và thứ tự tham số đúng như `vp2py.py --check` sẽ so.

## 0. Tóm tắt

| | Trước | Sau | Ghi chú |
|---|---|---|---|
| Lớp Frm (`view`) | 53 | 53 | **không đổi** tên, thuộc tính widget / dữ liệu, operation `on_*` |
| Lớp controller (`controller`) | 0 | **15** | package mới |
| DAO / gateway (`control`) | 34 / 5 | 34 / 5 | không đổi |
| Entity / enum (`model`) | 41 / 34 | 41 / 34 | không đổi |
| Tổng số lớp | 167 | **182** | |
| Operation | 329 | **459** | +130 operation của controller |
| Association Frm → DAO / gateway | 134 | **0** | xoá hết |
| Association Frm → controller | 0 | **46** | thêm |
| Association controller → DAO / gateway | 0 | **102** | thêm |
| Module (`check_gen.py`) | 104 | **119** | |

Những phần **không phải vẽ lại**: toàn bộ package `model` (entity, enum, kế thừa, association giữa entity), toàn bộ package `control` (DAO, gateway), các association Frm → Frm ("Opens"), các thuộc tính và operation của 53 Frm. Mình đã đối chiếu thuộc tính của từng Frm trước / sau khi sửa: không Frm nào mất hay thêm thuộc tính, chỉ đổi association.

## 1. Kiến trúc mới

```
                ┌──────────────────────────── View ────────────────────────────┐
                │  abc_fashion.view (53 XxxFrm, tkinter)   abc_fashion_web (web) │
                └───────────────────────────────┬──────────────────────────────┘
                                                │ chỉ gọi controller
                ┌──────────────────────── Controller ──────────────────────────┐
                │  abc_fashion.controller (15 XxxController)                    │
                └───────────────┬─────────────────────────────┬────────────────┘
                                │                             │
        ┌─────────────── Model (dữ liệu + truy cập) ───────────────────────────┐
        │  abc_fashion.control.dao (34 DAO)   abc_fashion.control.gateway (5)    │
        │  abc_fashion.model (41 entity, 34 enum, quy tắc thuần)                 │
        └────────────────────────────────────────────────────────────────────────┘
```

Ánh xạ sang MVC:
- **Model** = `model` (entity + quy tắc nghiệp vụ thuần) + `control.dao` (truy cập CSDL) + `control.gateway` (dịch vụ ngoài). Tên package `control` giữ nguyên để không phải vẽ lại 39 lớp; trong báo cáo ghi rõ đây là tầng truy cập dữ liệu / tích hợp, thuộc phần Model.
- **View** = 53 Frm (desktop) và ứng dụng web khách hàng `abc_fashion_web` (template HTML). View chỉ đọc input, gọi controller, hiển thị kết quả. View không import DAO / gateway / psycopg.
- **Controller** = 15 lớp mới. Mỗi lớp gom các ca sử dụng của một nhóm nghiệp vụ: kiểm tra dữ liệu, transaction nhiều DAO, gọi gateway ngoài transaction (mục 11), thông báo. Controller không biết tkinter / Flask, nên desktop và web dùng chung.

Quy tắc phụ thuộc (được `check_gen.py` kiểm tra tự động, 0 vi phạm):

| Layer | Được import |
|---|---|
| `view` | `view`, `controller`, `model` |
| `abc_fashion_web` | `controller`, `model`, `view._format` |
| `controller` | `controller`, `control.dao`, `control.gateway`, `model` (không tkinter, không Flask) |
| `control.dao` | `control.dao`, `model` |
| `control.gateway` | `control.gateway`, `model` |
| `model` | chỉ `model` |

## 2. Các bước sửa trong Visual Paradigm

### Bước 1 — Tạo package `controller`
Trong package gốc `abc_fashion`, tạo package **`controller`** ngang hàng với `model`, `control`, `view`. Tên phải viết đúng như vậy: `vp2py.py` lấy tên package cấp 1 làm layer và sinh module `abc_fashion.controller.<tên_lớp_snake>`.

### Bước 2 — Thêm 15 lớp controller (Phụ lục A)
Với mỗi lớp trong Phụ lục A:
1. Tạo class trong package `controller` (có thể gắn stereotype «control» cho đẹp; `vp2py` không dựa vào stereotype).
2. Thêm các operation **đúng tên và thứ tự tham số** như bảng. Không cần thêm tham số `self`.
3. Kiểu tham số / kiểu trả về: chọn lớp của model khi có (`Customer`, `Order`…). Kiểu dạng `X | None` thì đặt kiểu `X` (tuỳ chọn ghi multiplicity 0..1). Kiểu `list[X]` thì đặt `list` + type modifier `[X]`. `--check` chỉ so **tên và thứ tự tham số** của operation, không so kiểu.
4. Operation ghi «static» trong bảng: tick *Static* trong VP.
5. **Không** vẽ `__init__` cho controller. `vp2py` tự sinh `__init__` tạo các DAO / gateway theo association (giống DAO con).
6. **Không** cần thuộc tính `xxx_dao`. Quan hệ dùng DAO / gateway được thể hiện bằng association ở Bước 4.

### Bước 3 — Xoá 134 association Frm → DAO / gateway (Phụ lục B, cột "Cũ")
Xoá mọi association đi **từ** một Frm **tới** một lớp trong `control.dao` hoặc `control.gateway`. Mẹo trong VP: mở từng class diagram của package `view`, chọn connector → *Delete from Model* (không chỉ *Delete from View*). Nếu chỉ xoá khỏi diagram thì association vẫn còn trong model, và `--check` sẽ bắt Frm phải tạo DAO.

### Bước 4 — Thêm association mới
- **46 association Frm → controller** (Phụ lục B, cột "Mới"). Hướng: từ Frm tới controller (navigable phía controller). Gần như mỗi Frm dùng đúng một controller; riêng `StyleDetailFrm` dùng hai (`CatalogueController`, `CartController`). Tám màn hình chỉ điều hướng (7 trang chủ và `SelectReportFrm`, cột "Mới" ghi —) không dùng controller nào.
- **102 association controller → DAO / gateway** (Phụ lục A, cột "Dùng"). Hướng: từ controller tới DAO / gateway.

`--check` kiểm tra cả hai chiều: Frm phải có dòng `self.<tên_snake> = <Controller>()`, controller phải có `self.<tên_snake> = <DAO>()`.

### Bước 5 — Biểu đồ lớp tham gia (VOPC) của từng use case
Mỗi biểu đồ VOPC trước đây vẽ «boundary» Frm nối thẳng tới DAO. Nay vẽ: Frm («boundary») → Controller («control») → các DAO / gateway mà controller đó dùng → entity. Danh sách lớp lấy từ Phụ lục A + B.

### Bước 6 — Biểu đồ tuần tự / giao tiếp (Phụ lục C)
Thêm một lifeline controller giữa Frm và DAO / gateway. Thông điệp từ Frm chỉ còn **một lời gọi controller** cho mỗi thao tác của người dùng; mọi lời gọi DAO / gateway chuyển sang xuất phát từ controller. Phụ lục C liệt kê chuỗi thông điệp mới của các use case chính.

Lỗi nghiệp vụ (vd. sai mật khẩu, voucher hết lượt) nay được controller **ném ngoại lệ** `BusinessError` kèm thông báo. View bắt và hiển thị. Trên biểu đồ tuần tự, vẽ bằng fragment `alt [dữ liệu không hợp lệ]` với thông điệp trả về `BusinessError(message)` từ controller về Frm.

### Bước 7 — Biểu đồ gói / thành phần / triển khai
- Biểu đồ gói: thêm package `controller` và các phụ thuộc như mục 1.
- Bản web: thêm một **component** (hoặc package) `abc_fashion_web` (Flask: `routes` + `templates`), phụ thuộc vào `controller`. Biểu đồ triển khai: *Trình duyệt khách* —HTTP→ *Web server (Flask, cổng 8000)* → *PostgreSQL*; *Máy nhân viên (ứng dụng desktop)* → *PostgreSQL*; cả hai → các dịch vụ ngoài (8101–8104).
- **Không** thêm lớp của `abc_fashion_web` vào mô hình lớp. Đây là một view thứ hai gồm hàm route và template, không phải lớp; số lớp mà `check_gen.py` so chỉ tính `abc_fashion`.

### Bước 8 — Những thứ KHÔNG vẽ (module riêng tư, tên bắt đầu `_`)
`controller/_errors.py` (`BusinessError`, `AccessDenied`, `ServiceUnavailable`), `controller/_flows.py` (luồng dùng chung: thanh toán, hoàn tiền, huỷ đơn, thông báo), `controller/_media.py`, `controller/_connection.py`, `view/_format.py`, thuộc tính `DAO._per_thread`. Muốn nhắc tới trong báo cáo thì dùng *Note*. Đừng tạo class `BusinessError` trong package `controller`: `vp2py --check` sẽ đi tìm module `abc_fashion.controller.business_error` và báo thiếu lớp.

Hàm thuần mới trong model (`EMAIL_RE`, `PHONE_RE`, `password_problem` trong `model/user.py`, chuyển từ `RegisterFrm` sang) là hàm cấp module, không phải lớp, nên cũng không vẽ.

### Bước 9 — Kiểm tra sau khi vẽ
```bash
# trong VP: Project > Export > XML → vp_export/project.xml
cd code
../.venv/Scripts/python.exe vp2py.py ../vp_export/project.xml --check .     # phải báo: lệch mô hình: 0
../.venv/Scripts/python.exe vp2py.py ../vp_export/project.xml <thư_mục_tạm> # phải báo: generated modules: 119, operations: 459
../.venv/Scripts/python.exe check_gen.py .                                   # imported modules: 119 / layer violations: 0
../.venv/Scripts/python.exe -m pytest -q tests/test_structure.py            # 2 test đối chiếu VP hết bị bỏ qua và phải đạt
```
Nếu `--check` báo `X: không tạo self.y_dao = YDAO() (association Uses)` với X là Frm, nghĩa là còn sót association Frm → DAO (Bước 3). Nếu báo `XController.op: tham số [...] ≠ mô hình [...]`, sửa tên / thứ tự tham số theo Phụ lục A.

---

## Phụ lục A — 15 lớp controller

Cột "Dùng" = các association controller → DAO / gateway cần vẽ. Kiểu viết theo cú pháp Python (`X | None` = có thể rỗng).

### AccountAdminController  ·  `controller/account_admin_controller.py`  ·  8 operation

- **Dùng** (association → DAO / gateway): UserDAO, StaffMemberDAO, AuditLogEntryDAO
- **Được dùng bởi** (association Frm →): AuditLogFrm, EditAccountFrm, SearchAccountFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `search_user` | `key: str, user_type: str, status: AccountStatus \| None` | `list[User]` |  |
| `get_staff_member` | `user: User` | `StaffMember \| None` | Hồ sơ nhân viên của tài khoản (None nếu không phải nhân viên). |
| `get_all_staff` | — | `list[StaffMember]` |  |
| `suspend_account` | `staff: StaffMember, user: User` | `bool` |  |
| `activate_account` | `staff: StaffMember, user: User` | `bool` |  |
| `reset_password` | `staff: StaffMember, user: User` | `str \| None` | Đặt mật khẩu tạm ngẫu nhiên; trả mật khẩu tạm (chỉ hiện một lần) hoặc None nếu không đặt được. |
| `change_role` | `staff: StaffMember, staff_member: StaffMember, role: StaffRole` | `bool` | Đổi vai trò nhân viên; trả False nếu vai trò không đổi. |
| `search_audit_log` | `start: date, end: date, staff: StaffMember \| None, action: AuditAction \| None` | `list[AuditLogEntry]` |  |

### AuthController  ·  `controller/auth_controller.py`  ·  2 operation

- **Dùng** (association → DAO / gateway): UserDAO, CustomerDAO, StaffMemberDAO, SupplierDAO
- **Được dùng bởi** (association Frm →): LoginFrm, RegisterFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `login` | `email: str, password: str` | `Customer \| Supplier \| StaffMember` | Trả tác nhân của tài khoản (khách / nhà cung cấp / nhân viên); sai thông tin → BusinessError. |
| `register` | `customer: Customer, confirm_password: str` | `bool` | UC01: kiểm tra dữ liệu (E1 e-mail trùng, E2 mật khẩu không khớp) rồi tạo tài khoản khách. |

### CartController  ·  `controller/cart_controller.py`  ·  5 operation

- **Dùng** (association → DAO / gateway): CartDAO, StockLevelDAO
- **Được dùng bởi** (association Frm →): CartFrm, StyleDetailFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_cart` | `customer: Customer` | `Cart` | Giỏ của khách, gắn `cart.items` và `cart.subtotal`. |
| `add_to_cart` | `customer: Customer \| None, variant: ProductVariant \| None, quantity: int` | `bool` |  |
| `update_quantity` | `item: CartItem, quantity: int` | `bool` | Đổi số lượng một dòng; 0 = xoá dòng. |
| `remove_item` | `item: CartItem` | `bool` |  |
| `check_availability` | `cart: Cart` | `list[CartItem]` | UC29: các dòng không đủ hàng (gắn `available`); giỏ trống → BusinessError. |

### CatalogueController  ·  `controller/catalogue_controller.py`  ·  15 operation

- **Dùng** (association → DAO / gateway): CategoryDAO, StyleDAO, ProductVariantDAO, ProductMediaDAO, MaterialComponentDAO, SizeChartEntryDAO, ReviewDAO, StockLevelDAO, PromotionDAO, AssistantTurnDAO, SearchEngine, AssistantEngine
- **Được dùng bởi** (association Frm →): AssistantFrm, BrowseStyleFrm, SearchStyleFrm, StyleDetailFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_categories` | — | `list[Category]` |  |
| `browse_style` | `category: Category \| None, size: str, colour: str, fit_type: FitType \| None, min_price: int, max_price: int, sort: str` | `list[Style]` | UC04: lọc theo danh mục (gồm danh mục con), cỡ, màu, dáng, khoảng giá; `max_price = 0` là không giới hạn. |
| `search_style` | `key: str` | `list[Style]` | UC05 tìm bằng chữ; chỉ trả sản phẩm đang bán. |
| `find_style_ids_by_image` | `image: bytes` | `list[int]` | UC05 tìm bằng ảnh (CLIP). An toàn ở luồng phụ. Dịch vụ AI không phản hồi → ServiceUnavailable. |
| `find_style_ids_by_voice` | `audio: bytes` | `list[int]` | UC05 tìm bằng giọng nói (Whisper + LLM). An toàn ở luồng phụ. |
| `get_active_styles` | `ids: list[int]` | `list[Style]` | Sản phẩm đang bán theo đúng thứ tự `ids` (kết quả tìm bằng ảnh / giọng nói). |
| `get_cover_images` | `styles: list[Style]` | `dict[int, str]` | Ảnh đầu tiên (file cục bộ, bỏ URL CDN không tải được) của mỗi style — cho danh sách dạng lưới. |
| `get_style_detail` | `style: Style` | `Style` | Style đầy đủ, gắn động: `variants` (đang bán), `media`, `images`, `materials`, `size_chart`, `reviews` |
| «static» `auto_promotion` | `style: Style` | `Promotion \| None` | Khuyến mãi tự giảm trên trang sản phẩm (chương trình không có mã giảm giá). |
| `get_final_price` | `style: Style, variant: ProductVariant` | `int` |  |
| `get_stock_level` | `variant: ProductVariant` | `StockLevel \| None` |  |
| `summarise_reviews` | `style: Style` | `str` | UC33: tóm tắt đánh giá; AI lỗi thì trả chuỗi rỗng (trang vẫn hiện bình thường). |
| `get_assistant_history` | `customer: Customer \| None, style: Style` | `list[AssistantTurn]` |  |
| `ask_assistant` | `question: str, style: Style` | `dict` | UC32: hỏi trợ lý (style đã gắn ngữ cảnh bởi get_style_detail). An toàn ở luồng phụ. |
| `save_assistant_turn` | `customer: Customer \| None, style: Style, result: dict, latency_ms: int` | `AssistantTurn` | Ghi một lượt hỏi đáp (kèm dữ liệu đã dùng để trả lời) sau khi ask_assistant xong. |

### CheckoutController  ·  `controller/checkout_controller.py`  ·  9 operation

- **Dùng** (association → DAO / gateway): AddressDAO, PaymentMethodDAO, VoucherDAO, OrderDAO, PaymentDAO, NotificationDAO, PromotionDAO, PaymentGateway, NotificationGateway
- **Được dùng bởi** (association Frm →): CheckoutFrm, ConfirmOrderFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `start_checkout` | `customer: Customer, cart: Cart` | `Order` | Đơn nháp từ giỏ: giá đã trừ khuyến mãi tự động (UC31), `order.vouchers` rỗng, tổng đã tính. |
| `recalc` | `order: Order` | `Order` | UC26 + UC30: phân bổ lại giảm giá của mọi voucher đã áp, rồi tính phí ship và tổng. |
| `get_addresses` | `customer: Customer` | `list[Address]` |  |
| `get_payment_options` | `customer: Customer, method_type: PaymentMethodType` | `list[PaymentMethod \| None]` | Phương thức đã liên kết dùng được cho `method_type`; ví điện tử còn có lựa chọn None (trả trên ví). |
| `apply_voucher` | `order: Order, code: str` | `Voucher` |  |
| `place_order` | `customer: Customer, order: Order, address: Address \| None, method_type: PaymentMethodType, method: PaymentMethod \| None, note: str` | `bool` | UC08: (1) giữ hàng + ghi đơn, (2) thu tiền, (3) xác nhận + thông báo. Trả True nếu đơn đã xác nhận, |
| `get_order` | `customer: Customer, order: Order` | `Order` |  |
| `get_retry_options` | `customer: Customer` | `list[tuple[PaymentMethodType, PaymentMethod \| None]]` | Các cách thanh toán lại: thẻ / ví đã liên kết, chuyển khoản, COD. |
| `retry_payment` | `customer: Customer, order: Order, method_type: PaymentMethodType, method: PaymentMethod \| None` | `bool` |  |

### InventoryController  ·  `controller/inventory_controller.py`  ·  14 operation

- **Dùng** (association → DAO / gateway): StockLevelDAO, StockLocationDAO, StockMovementDAO, ProductVariantDAO, RestockRequestDAO, SupplierDAO, AuditLogEntryDAO, NotificationGateway
- **Được dùng bởi** (association Frm →): AdjustStockFrm, ConfirmRestockFrm, EditRestockRequestFrm, ManageRestockFrm, SelectVariantFrm, StockLevelFrm, StockMovementFrm, SupplierHomeFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_stock_locations` | — | `list[StockLocation]` |  |
| `search_stock_level` | `location: StockLocation \| None, key: str, below_reorder_point: bool` | `list[StockLevel]` |  |
| `adjust_stock` | `staff: StaffMember, stock_level: StockLevel, change: int, reference: str, note: str` | `int` | FR23: điều chỉnh tồn có tham chiếu + lý do; tồn + sổ kho + nhật ký trong một transaction. |
| `get_movements` | `variant: ProductVariant, start: date, end: date, reason: MovementReason \| None` | `list[StockMovement]` |  |
| `search_variant` | `key: str` | `list[ProductVariant]` |  |
| `get_suppliers` | — | `list[Supplier]` |  |
| `search_restock_request` | `status: RestockStatus \| None, supplier: Supplier \| None` | `list[RestockRequest]` |  |
| `get_restock_request_detail` | `restock_request: RestockRequest \| None` | `RestockRequest` | Phiếu đầy đủ (kèm `items`); None → phiếu nháp mới. |
| «static» `add_restock_item` | `restock_request: RestockRequest, variant: ProductVariant, quantity: int, location: StockLocation \| None` | `RestockRequest` | Thêm (cộng dồn) một biến thể vào phiếu chưa lưu; mỗi biến thể chỉ nhập vào kho của nó. |
| `save_restock_request` | `staff: StaffMember, restock_request: RestockRequest, supplier: Supplier \| None, location: StockLocation \| None, expected_date: date, send: bool` | `bool` | Lưu nháp (`send=False`) hoặc gửi nhà cung cấp (`send=True`, kèm e-mail báo phiếu chờ xác nhận). |
| `receive_restock` | `staff: StaffMember, restock_request: RestockRequest` | `int` | Nhận đủ hàng của phiếu đã được nhà cung cấp xác nhận: cộng tồn + sổ kho. Trả tổng số sản phẩm. |
| `get_supplier_restock` | `supplier: Supplier, restock_request: RestockRequest` | `RestockRequest` |  |
| `confirm_restock` | `supplier: Supplier, restock_request: RestockRequest, expected_date: date, note: str` | `bool` |  |
| `refuse_restock` | `supplier: Supplier, restock_request: RestockRequest, note: str` | `bool` |  |

### OrderAdminController  ·  `controller/order_admin_controller.py`  ·  6 operation

- **Dùng** (association → DAO / gateway): OrderDAO, ShipmentDAO, PaymentDAO, NotificationDAO, AuditLogEntryDAO, PaymentGateway, ShippingGateway, NotificationGateway
- **Được dùng bởi** (association Frm →): ManageOrderFrm, SearchOrderFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `search_order` | `key: str, status: OrderStatus \| None, start: date, end: date` | `list[Order]` |  |
| `get_order_detail` | `order: Order` | `Order` | Đơn đầy đủ, gắn động: `next_statuses` (theo ORDER_NEXT, trừ huỷ), `can_cancel`, `cancel_requested`, |
| `get_order_signature` | `order: Order` | `tuple` |  |
| `update_status` | `staff: StaffMember, order: Order, new_status: OrderStatus, shipments: list[Shipment]` | `OrderStatus` | Chuyển đơn sang `new_status`. Giao (một phần) thì bàn giao các kiện chờ lấy hàng — `shipments` là kiện được |
| `cancel_order` | `staff: StaffMember, order: Order, reason: str` | `str \| None` | UC23 / duyệt yêu cầu huỷ của khách: huỷ, trả hàng về kho, hoàn tiền, ghi nhật ký. |
| `refund` | `staff: StaffMember, order: Order, amount: int` | `int` | Hoàn tiền thủ công (vd. lần hoàn khi huỷ bị lỗi ngân hàng); trả số đã hoàn. |

### OrderController  ·  `controller/order_controller.py`  ·  9 operation

- **Dùng** (association → DAO / gateway): OrderDAO, PaymentDAO, ShipmentDAO, ReturnRequestDAO, ReviewDAO, NotificationDAO, PaymentGateway, ShippingGateway, NotificationGateway
- **Được dùng bởi** (association Frm →): CancelRequestFrm, OrderDetailFrm, OrderListFrm, TrackShipmentFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_orders` | `customer: Customer, status: OrderStatus \| None` | `list[Order]` |  |
| `get_order_detail` | `customer: Customer, order: Order` | `Order` | Đơn đầy đủ của chính khách (NFR03, khác → AccessDenied), gắn động: `return_request`, `delivered_at`, |
| `get_order_signature` | `order: Order` | `tuple` | Dấu hiệu thay đổi (trạng thái đơn và các kiện) để màn hình tự nạp lại khi vận chuyển tiến triển. |
| `cancel_order` | `order: Order, reason: str` | `tuple[str, str \| None]` | UC10: đơn chưa đóng gói → huỷ ngay và hoàn tiền; đơn đang đóng gói → gửi yêu cầu huỷ cho quản lý. |
| `confirm_received` | `order: Order` | `bool` | UC12: khách xác nhận đã nhận đủ hàng → hoàn tất. |
| `get_shipment` | `shipment: Shipment` | `Shipment` | Kiện mới nhất trong CSDL (kèm `records`). |
| `get_shipment_events` | `shipment: Shipment` | `list[ShipmentEvent]` |  |
| `get_shipment_signature` | `shipment: Shipment` | `tuple` |  |
| `refresh_tracking` | `shipment: Shipment` | `int` | Hỏi hãng vận chuyển, ghi sự kiện mới; trả số sự kiện mới. |

### ProductController  ·  `controller/product_controller.py`  ·  15 operation

- **Dùng** (association → DAO / gateway): StyleDAO, CategoryDAO, CollectionDAO, SupplierDAO, ProductMediaDAO, MaterialComponentDAO, SizeChartEntryDAO, ProductVariantDAO, StockLevelDAO, StockLocationDAO, AuditLogEntryDAO, SearchEngine
- **Được dùng bởi** (association Frm →): EditStyleFrm, EditVariantFrm, ManageStyleFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_categories` | — | `list[Category]` |  |
| `get_suppliers` | — | `list[Supplier]` |  |
| `get_collections` | — | `list[Collection]` |  |
| `get_stock_locations` | — | `list[StockLocation]` |  |
| `search_style` | `key: str, category: Category \| None, status: StyleStatus \| None` | `list[Style]` | Mọi trạng thái; lọc theo danh mục (gồm danh mục con) và trạng thái. |
| `deactivate_style` | `staff: StaffMember, style: Style` | `bool` | Ngừng bán style và mọi biến thể (cùng nhật ký trong một transaction). |
| `get_style_for_edit` | `style: Style` | `Style` | Style mới (chưa có id) giữ nguyên; style có sẵn được nạp lại, gắn động `materials`, `size_chart`, `media`, |
| «static» `make_material` | `material: str, percent: int` | `MaterialComponent` |  |
| «static» `make_size_entry` | `size_label: str, measure: Measure \| None, value_cm: float \| None` | `SizeChartEntry` |  |
| `save_style` | `staff: StaffMember, style: Style, draft: Style, materials: list[MaterialComponent], size_chart: list[SizeChartEntry]` | `bool` | Lưu style (các trường STYLE_FIELDS lấy từ `draft`) + vật liệu + bảng cỡ + nhật ký trong một transaction. |
| `upload_media` | `style: Style, file_name: str, data: bytes` | `ProductMedia` |  |
| `delete_media` | `media: ProductMedia` | `bool` |  |
| `get_media` | `style: Style` | `list[ProductMedia]` |  |
| `get_variants` | `style: Style` | `list[ProductVariant]` |  |
| `save_variant` | `style: Style, variant: ProductVariant, location: StockLocation \| None, reorder_point: int` | `bool` | Thêm (`variant.id` rỗng: cùng bản ghi tồn kho đầu tiên ở `location`, một transaction) hoặc sửa biến thể. |

### ProfileController  ·  `controller/profile_controller.py`  ·  11 operation

- **Dùng** (association → DAO / gateway): CustomerDAO, AddressDAO, PaymentMethodDAO, SavedSizeDAO, CategoryDAO, PaymentGateway
- **Được dùng bởi** (association Frm →): EditAddressFrm, LinkPaymentMethodFrm, ProfileFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `update_profile` | `customer: Customer, full_name: str, phone: str, preferred_colours: list[str], marketing_consent: bool` | `bool` |  |
| `get_addresses` | `customer: Customer` | `list[Address]` |  |
| `save_address` | `customer: Customer, address: Address` | `bool` | Thêm (`address.id` rỗng) hoặc sửa một địa chỉ của khách. |
| `delete_address` | `address: Address` | `bool` |  |
| `get_payment_methods` | `customer: Customer` | `list[PaymentMethod]` |  |
| `get_providers` | `method_type: LinkedMethodType \| None` | `list[str]` |  |
| `link_payment_method` | `customer: Customer, method_type: LinkedMethodType \| None, provider: str, is_default: bool` | `PaymentMethod` | Khách nhập số thẻ / tài khoản trên trang của cổng thanh toán; hệ thống chỉ lưu số đã che. |
| `remove_payment_method` | `method: PaymentMethod` | `bool` |  |
| `get_categories` | — | `list[Category]` |  |
| `get_saved_sizes` | `customer: Customer` | `list[SavedSize]` |  |
| `save_size` | `customer: Customer, category: Category \| None, size_label: str` | `bool` |  |

### PromotionController  ·  `controller/promotion_controller.py`  ·  7 operation

- **Dùng** (association → DAO / gateway): PromotionDAO, VoucherDAO, StyleDAO, CategoryDAO
- **Được dùng bởi** (association Frm →): EditPromotionFrm, ManagePromotionFrm, SelectStyleFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `search_promotion` | `key: str, status: PromotionStatus \| None` | `list[Promotion]` |  |
| `get_promotion_detail` | `promotion: Promotion` | `Promotion` | Chương trình đầy đủ, gắn động `styles` và `vouchers`. Chương trình mới (chưa có id) giữ nguyên. |
| `save_promotion` | `promotion: Promotion, name: str, promo_type: PromoType, discount_type: DiscountType, discount_value: int \| None, min_order_value: int \| None, start: date, end: date, status: PromotionStatus, styles: list[Style]` | `bool` | Thêm / sửa chương trình; kết thúc tính đến hết ngày `end`. |
| `end_promotion` | `promotion: Promotion` | `bool` | Kết thúc sớm; chương trình đã kết thúc thì trả False. |
| `add_voucher` | `promotion: Promotion, code: str, usage_limit: int` | `list[Voucher]` | Thêm mã giảm giá; trả danh sách mã của chương trình. |
| `get_categories` | — | `list[Category]` |  |
| `search_style` | `key: str, category: Category \| None` | `list[Style]` |  |

### ReportController  ·  `controller/report_controller.py`  ·  7 operation

- **Dùng** (association → DAO / gateway): StyleStatDAO, ReturnStatDAO, OrderItemDAO, ReturnItemDAO, CategoryDAO, CollectionDAO
- **Được dùng bởi** (association Frm →): ReturnDetailFrm, ReturnReportFrm, SalesDetailFrm, SalesReportFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_categories` | — | `list[Category]` |  |
| `get_collections` | — | `list[Collection]` |  |
| `get_sales_report` | `start: date, end: date, category: Category \| None, collection: Collection \| None` | `list[StyleStat]` |  |
| `get_sales_detail` | `style_stat: StyleStat, start: date, end: date` | `list[OrderItem]` |  |
| `export_sales_csv` | `stats: list[StyleStat], path: str` | `int` | Ghi báo cáo doanh số ra CSV (BOM để Excel đọc đúng tiếng Việt); trả số dòng. |
| `get_return_report` | `start: date, end: date, reason: ReturnReason \| None` | `list[ReturnStat]` |  |
| `get_return_detail` | `return_stat: ReturnStat, start: date, end: date` | `list[ReturnItem]` |  |

### ReturnController  ·  `controller/return_controller.py`  ·  14 operation

- **Dùng** (association → DAO / gateway): ReturnRequestDAO, ProductVariantDAO, ShipmentDAO, PaymentDAO, StockLevelDAO, NotificationDAO, PaymentGateway, ShippingGateway, NotificationGateway
- **Được dùng bởi** (association Frm →): InspectReturnFrm, ProcessReturnFrm, ReturnRequestFrm, SearchReturnRequestFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_replacement_options` | `order_item: OrderItem` | `list[ProductVariant]` | Biến thể cùng style (đang bán, khác biến thể đã mua) để đổi sang; gắn `available`. |
| `make_return_item` | `order_item: OrderItem, quantity: int, return_type: ReturnType, replacement: ProductVariant \| None` | `ReturnItem` | Một dòng của yêu cầu (chưa lưu). Đổi hàng thì bắt buộc chọn biến thể thay thế. |
| `store_evidence` | `file_name: str, data: bytes` | `ReturnEvidence` | Lưu ảnh / video bằng chứng vào media/returns; trả ReturnEvidence chưa gắn vào yêu cầu. |
| `submit_return_request` | `customer: Customer, order: Order, return_request: ReturnRequest, evidence: list[ReturnEvidence]` | `ReturnRequest` | Gửi yêu cầu (`items`, `return_type`, `desired_resolution`, `reason_code`, `reason_detail` đã đặt). |
| `search_return_request` | `key: str, status: ReturnStatus \| None` | `list[ReturnRequest]` |  |
| `get_return_request_detail` | `return_request: ReturnRequest` | `ReturnRequest` | Yêu cầu đầy đủ (items, evidence, shipments) — gắn động `can_authorise`, `can_reject`, `can_create_pickup`, |
| `authorise` | `staff: StaffMember, return_request: ReturnRequest, note: str` | `bool` | Duyệt yêu cầu. Quá hạn trả hàng (UC18 E2) → tự từ chối và trả False. |
| `reject` | `staff: StaffMember, return_request: ReturnRequest, note: str` | `bool` |  |
| `create_pickup` | `staff: StaffMember, return_request: ReturnRequest` | `Shipment` | Tạo kiện lấy hàng và bàn giao cho hãng. Lần trước hãng không phản hồi → dùng lại kiện đã tạo. |
| `refund` | `staff: StaffMember, return_request: ReturnRequest, note: str` | `int` | Hoàn tiền các dòng đạt kiểm tra (`refund_amount`); không dòng nào đạt → đánh dấu đã xử lý, hoàn 0 đ. |
| `ship_replacement` | `staff: StaffMember, return_request: ReturnRequest, note: str` | `list[Shipment]` | Trừ kho biến thể thay thế + tạo kiện đổi (một transaction), rồi bàn giao cho hãng. Lần trước hãng không |
| `close` | `staff: StaffMember, return_request: ReturnRequest, note: str` | `bool` |  |
| `save_inspection` | `item: ReturnItem, result: InspectionResult, note: str` | `bool` |  |
| `finish_inspection` | `staff: StaffMember, return_request: ReturnRequest` | `int` | Nhập lại kho các dòng đạt (FR29), chuyển yêu cầu sang inspected, đánh dấu kiện lấy hàng đã về kho — |

### ReviewController  ·  `controller/review_controller.py`  ·  3 operation

- **Dùng** (association → DAO / gateway): ReviewDAO, AssistantEngine
- **Được dùng bởi** (association Frm →): ManageReviewFrm, ReviewFrm

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `submit_review` | `order_item: OrderItem, rating: int, body: str, size_purchased: str, fit_vote: FitVote` | `Review` | Trả đánh giá đã lưu: `status` approved nếu qua kiểm duyệt tự động, pending (kèm `moderation_note`) nếu không. |
| `search_review` | `key: str, status: ReviewStatus \| None, rating: int \| None` | `list[Review]` |  |
| `moderate_review` | `staff: StaffMember, review: Review, status: ReviewStatus, note: str` | `bool` |  |

### SyncController  ·  `controller/sync_controller.py`  ·  5 operation

- **Dùng** (association → DAO / gateway): OrderDAO, ShipmentDAO, PaymentDAO, NotificationDAO, StyleDAO, ShippingGateway, NotificationGateway, SearchEngine
- **Được dùng bởi** (association Frm →): — (ứng dụng nền / web)

| Operation | Tham số | Trả về | Ý nghĩa |
|---|---|---|---|
| `release_expired_orders` | — | `int` | Mục 9.5: huỷ đơn chờ thanh toán quá hạn để nhả hàng; trả số đơn đã huỷ. |
| `get_open_shipments` | — | `list[Shipment]` | Kiện đã có vận đơn và chưa kết thúc. |
| `fetch_tracking` | `shipments: list[Shipment]` | `list[tuple[Shipment, list[ShipmentEvent]]]` | Hỏi hãng vận chuyển từng kiện (bỏ qua kiện hãng không trả lời). An toàn ở luồng phụ. |
| `apply_tracking` | `results: list[tuple[Shipment, list[ShipmentEvent]]]` | `set[int]` | Ghi sự kiện mới; với mỗi đơn có kiện đổi trạng thái, suy ra trạng thái đơn từ các kiện và đi từng bước hợp |
| `push_search_index` | — | `None` | Đẩy danh mục sản phẩm lên dịch vụ AI (chỉ chế độ http; gửi ở luồng phụ). |

## Phụ lục B — Association của 53 Frm: cũ → mới

"Cũ" = association Frm → DAO / gateway cần **xoá**; "Mới" = association Frm → controller cần **thêm**.

| Frm | Cũ: association cần xoá (→ DAO / gateway) | Mới: association cần thêm (→ controller) |
|---|---|---|
| AdjustStockFrm | AuditLogEntryDAO, StockLevelDAO | InventoryController |
| AdminHomeFrm | — | — |
| AssistantFrm | AssistantEngine, AssistantTurnDAO | CatalogueController |
| AuditLogFrm | AuditLogEntryDAO, StaffMemberDAO | AccountAdminController |
| BrowseStyleFrm | CategoryDAO, StyleDAO | CatalogueController |
| CancelRequestFrm | NotificationDAO, NotificationGateway, OrderDAO, PaymentDAO, PaymentGateway | OrderController |
| CartFrm | CartDAO, StockLevelDAO | CartController |
| CheckoutFrm | AddressDAO, NotificationDAO, NotificationGateway, OrderDAO, PaymentDAO, PaymentGateway, PaymentMethodDAO, PromotionDAO, VoucherDAO | CheckoutController |
| ConfirmOrderFrm | NotificationDAO, NotificationGateway, OrderDAO, PaymentDAO, PaymentGateway, PaymentMethodDAO | CheckoutController |
| ConfirmRestockFrm | RestockRequestDAO | InventoryController |
| CustomerHomeFrm | — | — |
| CustomerServiceHomeFrm | — | — |
| EditAccountFrm | AuditLogEntryDAO, StaffMemberDAO, UserDAO | AccountAdminController |
| EditAddressFrm | AddressDAO | ProfileController |
| EditPromotionFrm | PromotionDAO, VoucherDAO | PromotionController |
| EditRestockRequestFrm | NotificationGateway, RestockRequestDAO, StockLocationDAO, SupplierDAO | InventoryController |
| EditStyleFrm | AuditLogEntryDAO, CategoryDAO, CollectionDAO, MaterialComponentDAO, ProductMediaDAO, ProductVariantDAO, SizeChartEntryDAO, StyleDAO, SupplierDAO | ProductController |
| EditVariantFrm | ProductVariantDAO, StockLevelDAO, StockLocationDAO | ProductController |
| InspectReturnFrm | ReturnRequestDAO, ShipmentDAO, StockLevelDAO, StockMovementDAO | ReturnController |
| LinkPaymentMethodFrm | PaymentGateway, PaymentMethodDAO | ProfileController |
| LoginFrm | CustomerDAO, StaffMemberDAO, SupplierDAO, UserDAO | AuthController |
| ManageOrderFrm | AuditLogEntryDAO, NotificationDAO, NotificationGateway, OrderDAO, PaymentDAO, PaymentGateway, ShipmentDAO, ShippingGateway, StockMovementDAO | OrderAdminController |
| ManagePromotionFrm | PromotionDAO | PromotionController |
| ManageRestockFrm | RestockRequestDAO, StockLevelDAO, StockMovementDAO, SupplierDAO | InventoryController |
| ManageReviewFrm | ReviewDAO | ReviewController |
| ManageStyleFrm | AuditLogEntryDAO, CategoryDAO, StyleDAO | ProductController |
| ManagerHomeFrm | — | — |
| MarketingHomeFrm | — | — |
| MerchandiserHomeFrm | — | — |
| OrderDetailFrm | OrderDAO, ReturnRequestDAO, ReviewDAO | OrderController |
| OrderListFrm | OrderDAO | OrderController |
| ProcessReturnFrm | NotificationDAO, NotificationGateway, PaymentDAO, PaymentGateway, ReturnRequestDAO, ShipmentDAO, ShippingGateway, StockLevelDAO | ReturnController |
| ProfileFrm | AddressDAO, CategoryDAO, CustomerDAO, PaymentMethodDAO, SavedSizeDAO | ProfileController |
| RegisterFrm | CustomerDAO, UserDAO | AuthController |
| ReturnDetailFrm | ReturnItemDAO | ReportController |
| ReturnReportFrm | ReturnStatDAO | ReportController |
| ReturnRequestFrm | ProductVariantDAO, ReturnRequestDAO | ReturnController |
| ReviewFrm | AssistantEngine, ReviewDAO | ReviewController |
| SalesDetailFrm | OrderItemDAO | ReportController |
| SalesReportFrm | CategoryDAO, CollectionDAO, StyleStatDAO | ReportController |
| SearchAccountFrm | UserDAO | AccountAdminController |
| SearchOrderFrm | OrderDAO | OrderAdminController |
| SearchReturnRequestFrm | ReturnRequestDAO | ReturnController |
| SearchStyleFrm | SearchEngine, StyleDAO | CatalogueController |
| SelectReportFrm | — | — |
| SelectStyleFrm | CategoryDAO, StyleDAO | PromotionController |
| SelectVariantFrm | ProductVariantDAO | InventoryController |
| StockLevelFrm | StockLevelDAO, StockLocationDAO | InventoryController |
| StockMovementFrm | StockMovementDAO | InventoryController |
| StyleDetailFrm | AssistantEngine, CartDAO, MaterialComponentDAO, ProductMediaDAO, ProductVariantDAO, PromotionDAO, ReviewDAO, SizeChartEntryDAO, StockLevelDAO, StyleDAO | CartController, CatalogueController |
| SupplierHomeFrm | RestockRequestDAO | InventoryController |
| TrackShipmentFrm | ShipmentDAO, ShippingGateway | OrderController |
| WarehouseHomeFrm | — | — |

## Phụ lục C — Chuỗi thông điệp mới cho biểu đồ tuần tự

Ký hiệu: `Frm.on_x → Controller.op → [DAO / gateway …]`. Thứ tự bên trong ngoặc là thứ tự gọi thật trong mã. "(tx)" = trong một transaction CSDL. "sau commit" = gọi gateway sau khi đã ghi CSDL (mục 11, quy tắc 2).

| UC | Thao tác | Chuỗi thông điệp |
|---|---|---|
| UC01 | Đăng ký | `RegisterFrm.on_register → AuthController.register → UserDAO.is_email_used → CustomerDAO.add_customer` |
| UC02 | Đăng nhập | `LoginFrm.on_login → AuthController.login → UserDAO.check_login → CustomerDAO.get_customer_by_user / SupplierDAO.get_supplier_by_user / StaffMemberDAO.get_staff_member_by_user`; Frm mở trang chủ theo loại tác nhân trả về |
| UC03 | Sửa hồ sơ, địa chỉ, liên kết thẻ | `ProfileFrm.on_save → ProfileController.update_profile → CustomerDAO.update_customer`; `EditAddressFrm.on_save → ProfileController.save_address → AddressDAO.add_address / update_address`; `LinkPaymentMethodFrm.on_link → ProfileController.link_payment_method → PaymentGateway.link_method → PaymentMethodDAO.add_payment_method` |
| UC04 | Duyệt danh mục | `BrowseStyleFrm.on_filter → CatalogueController.browse_style → StyleDAO.get_style_by_category` |
| UC05 | Tìm bằng chữ / ảnh / giọng nói | `SearchStyleFrm.on_search → CatalogueController.search_style → StyleDAO.search_style`; ảnh: `on_search_by_image → (luồng phụ) CatalogueController.find_style_ids_by_image → SearchEngine.search_by_image`, rồi `CatalogueController.get_active_styles → StyleDAO.search_style_by_ids` |
| UC06, UC33 | Xem chi tiết | `StyleDetailFrm.__init__ → CatalogueController.get_style_detail → StyleDAO.get_style_detail, ProductVariantDAO.get_variant_by_style, ProductMediaDAO.get_media_by_style, MaterialComponentDAO.get_material_by_style, SizeChartEntryDAO.get_size_chart_by_style, ReviewDAO.get_approved_review_by_style, PromotionDAO.get_active_promotion_by_style`; `CatalogueController.summarise_reviews → AssistantEngine.summarise_reviews`; `on_select_variant → CatalogueController.get_final_price, get_stock_level → StockLevelDAO.get_stock_level_by_variant` |
| UC07 | Thêm vào giỏ / sửa giỏ | `StyleDetailFrm.on_add_to_cart → CartController.add_to_cart → CartDAO.get_cart_by_customer, CartDAO.add_cart_item`; `CartFrm.on_update_quantity → CartController.update_quantity → CartDAO.update_cart_item / delete_cart_item` |
| UC29 | Kiểm tra tồn khi thanh toán | `CartFrm.on_checkout → CartController.check_availability → StockLevelDAO.check_availability` |
| UC08, UC26, UC30, UC31 | Thanh toán | `CheckoutFrm.__init__ → CheckoutController.start_checkout → PromotionDAO.get_active_promotion_by_style`; `on_apply_voucher → CheckoutController.apply_voucher → VoucherDAO.get_voucher_by_code, recalc`; `on_place_order → CheckoutController.place_order → OrderDAO.add_order (tx: giữ hàng, voucher, kiện) → sau commit PaymentGateway.charge → PaymentDAO.add_payment → OrderDAO.update_order_status → NotificationGateway.send → NotificationDAO.add_notification`; `alt [ngân hàng không phản hồi]`: ServiceUnavailable → Frm mở ConfirmOrderFrm để thanh toán lại |
| UC08 E2 | Thanh toán lại | `ConfirmOrderFrm.on_retry_payment → CheckoutController.retry_payment → PaymentGateway.charge → PaymentDAO.add_payment → OrderDAO.update_order_status → NotificationGateway.send` |
| UC09 | Xem đơn | `OrderListFrm.on_filter → OrderController.get_orders → OrderDAO.get_order_by_customer`; `OrderDetailFrm → OrderController.get_order_detail → OrderDAO.get_order_detail, ReturnRequestDAO.get_return_request_by_order, ReviewDAO.is_reviewed` (kiểm tra quyền NFR03 trong controller) |
| UC10 | Khách huỷ đơn | `CancelRequestFrm.on_send → OrderController.cancel_order → alt [chờ TT / đã xác nhận]: OrderDAO.cancel_order → PaymentDAO.get_payment_by_order → PaymentGateway.refund → PaymentDAO.add_payment → NotificationGateway.send; [đang xử lý]: OrderDAO._request_cancel` |
| UC11 | Theo dõi kiện | `TrackShipmentFrm.on_refresh → OrderController.refresh_tracking → ShippingGateway.get_tracking → ShipmentDAO.add_shipment_event` |
| UC12 | Xác nhận đã nhận | `OrderDetailFrm.on_confirm_received → OrderController.confirm_received → OrderDAO.update_order_status` |
| UC13, UC34 | Đánh giá | `ReviewFrm.on_submit → ReviewController.submit_review → ReviewDAO.is_reviewed → AssistantEngine.moderate → ReviewDAO.add_review` |
| UC14 | Yêu cầu trả / đổi | `ReturnRequestFrm.on_select_item → ReturnController.make_return_item`; `on_add_evidence → ReturnController.store_evidence`; `on_submit → ReturnController.submit_return_request → ReturnRequestDAO.add_return_request` |
| UC15, UC27 | Khuyến mãi, voucher | `EditPromotionFrm.on_save → PromotionController.save_promotion → PromotionDAO.add_promotion / update_promotion`; `on_add_voucher → PromotionController.add_voucher → VoucherDAO.add_voucher, get_voucher_by_promotion` |
| UC16, UC24 | Báo cáo | `SalesReportFrm.on_view → ReportController.get_sales_report → StyleStatDAO.get_style_stat`; `ReturnReportFrm.on_view → ReportController.get_return_report → ReturnStatDAO.get_return_stat` |
| UC17 | Nhập hàng, điều chỉnh tồn | `EditRestockRequestFrm.on_send → InventoryController.save_restock_request → RestockRequestDAO.add_restock_request / update_restock_request → NotificationGateway.send`; `ConfirmRestockFrm.on_confirm → InventoryController.confirm_restock → RestockRequestDAO.update_restock_request`; `ManageRestockFrm.on_mark_received → InventoryController.receive_restock → RestockRequestDAO.receive_restock_request`; `AdjustStockFrm.on_save → InventoryController.adjust_stock → (tx) StockLevelDAO.adjust_stock, AuditLogEntryDAO.add_audit_log_entry` |
| UC18 | Xử lý trả / đổi | `ProcessReturnFrm.on_authorise → ReturnController.authorise → ReturnRequestDAO.update_return_request → NotificationGateway.send`; `on_create_pickup → ReturnController.create_pickup → ShipmentDAO.add_shipment → sau commit ShippingGateway.create_shipment → ShipmentDAO.update_shipment → ReturnRequestDAO.update_return_request`; `on_refund → ReturnController.refund → PaymentGateway.refund → PaymentDAO.add_payment → ReturnRequestDAO.update_return_request`; `on_ship_replacement → ReturnController.ship_replacement → (tx) StockLevelDAO.adjust_stock, ShipmentDAO.add_shipment → sau commit ShippingGateway.create_shipment`; `InspectReturnFrm.on_finish → ReturnController.finish_inspection → (tx) StockLevelDAO.adjust_stock, ReturnRequestDAO.update_return_request, ShipmentDAO.update_shipment` |
| UC19 | Duyệt đánh giá | `ManageReviewFrm.on_approve / on_reject → ReviewController.moderate_review → ReviewDAO.update_review` |
| UC20 | Quản trị tài khoản | `EditAccountFrm.on_suspend → AccountAdminController.suspend_account → UserDAO.update_user_status → AuditLogEntryDAO.add_audit_log_entry`; `on_reset_password → AccountAdminController.reset_password → UserDAO.reset_password → AuditLogEntryDAO.add_audit_log_entry`; `AuditLogFrm.on_view → AccountAdminController.search_audit_log → AuditLogEntryDAO.search_audit_log_entry` |
| UC21 | Quản lý sản phẩm | `EditStyleFrm.on_save → ProductController.save_style → (tx) StyleDAO.add_style / update_style, MaterialComponentDAO.save_material, SizeChartEntryDAO.save_size_chart, AuditLogEntryDAO.add_audit_log_entry`; `EditVariantFrm.on_save → ProductController.save_variant → (tx) ProductVariantDAO.add_variant, StockLevelDAO.add_stock_level`; `ManageStyleFrm.on_deactivate → ProductController.deactivate_style → (tx) StyleDAO.deactivate_style, AuditLogEntryDAO.add_audit_log_entry` |
| UC22, UC23 | Xử lý đơn (quản lý) | `ManageOrderFrm.on_update_status → OrderAdminController.update_status → ShippingGateway.create_shipment → ShipmentDAO.update_shipment, add_shipment_event → OrderDAO.update_order_status → NotificationGateway.send`; `on_cancel_order → OrderAdminController.cancel_order → OrderDAO.cancel_order → PaymentGateway.refund → PaymentDAO.add_payment → NotificationGateway.send → AuditLogEntryDAO.add_audit_log_entry`; `on_refund → OrderAdminController.refund → PaymentGateway.refund → PaymentDAO.add_payment` |
| UC32 | Trợ lý AI | `AssistantFrm.on_ask → (luồng phụ) CatalogueController.ask_assistant → AssistantEngine.ask`, rồi `CatalogueController.save_assistant_turn → AssistantTurnDAO.add_assistant_turn` |
| (nền) | Đồng bộ vận chuyển | `ShipmentSync (view/_sync) → SyncController.get_open_shipments → ShipmentDAO._get_open_shipments → (luồng phụ) SyncController.fetch_tracking → ShippingGateway.get_tracking → SyncController.apply_tracking → ShipmentDAO.add_shipment_event, OrderDAO.update_order_status, NotificationGateway.send` |

Web: các use case của khách (UC01–UC14, UC26–UC34) có **cùng chuỗi thông điệp**. Chỉ thay lifeline đầu: thay Frm bằng `:Browser → :abc_fashion_web.routes` (ví dụ `POST /checkout → routes.checkout → CheckoutController.place_order → …`).
