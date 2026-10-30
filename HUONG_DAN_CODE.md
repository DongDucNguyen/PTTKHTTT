# Hướng dẫn lập trình dự án ABC Fashion E-Commerce Information System

> Tài liệu đi kèm bài `design_03_10_DongDucNguyen` (Chương 4 — Design). Mô tả **từng file, từng lớp, từng hàm và từng luồng** của package Python `abc_fashion` được sinh từ mô hình Visual Paradigm, và cách lập trình phần thân các hàm để có một ứng dụng desktop chạy được trên PostgreSQL.

## Mục lục

1. [Giới thiệu](#1-giới-thiệu)
2. [Kiến trúc tổng thể](#2-kiến-trúc-tổng-thể)
3. [Môi trường và cách chạy](#3-môi-trường-và-cách-chạy)
4. [Cấu trúc thư mục — từng file](#4-cấu-trúc-thư-mục--từng-file)
5. [Quy ước lập trình](#5-quy-ước-lập-trình)
6. [Model layer — lớp thực thể và enum](#6-model-layer--lớp-thực-thể-và-enum)
7. [Control layer — DAO và gateway](#7-control-layer--dao-và-gateway)
8. [View layer — các màn hình Frm](#8-view-layer--các-màn-hình-frm)
9. [Luồng nghiệp vụ chi tiết](#9-luồng-nghiệp-vụ-chi-tiết)
10. [Máy trạng thái](#10-máy-trạng-thái)
11. [Transaction và xử lý đồng thời](#11-transaction-và-xử-lý-đồng-thời)
12. [Công cụ sinh mã và kiểm tra](#12-công-cụ-sinh-mã-và-kiểm-tra)
13. [Các điểm thiết kế cần bổ sung khi lập trình](#13-các-điểm-thiết-kế-cần-bổ-sung-khi-lập-trình)
14. [Lộ trình triển khai và kiểm thử](#14-lộ-trình-triển-khai-và-kiểm-thử)
15. [Phụ lục — Use case → màn hình → DAO](#15-phụ-lục--use-case--màn-hình--dao)

---

## 1. Giới thiệu

### 1.1. Dự án là gì

ABC Fashion E-Commerce IS là hệ thống bán thời trang gồm: danh mục sản phẩm theo **style → biến thể (SKU)**, giỏ hàng, đặt hàng có voucher, thanh toán qua cổng thanh toán, **tách kiện theo kho**, theo dõi vận chuyển, huỷ đơn, đánh giá, **trả / đổi hàng**, quản lý kho và nhập hàng từ nhà cung cấp, khuyến mãi, báo cáo, quản trị tài khoản, và các chức năng AI của Chương 3 (tìm kiếm bằng ảnh / giọng nói, trợ lý hỏi đáp, tóm tắt và kiểm duyệt đánh giá).

Ứng dụng là **chương trình desktop Python** (giao diện `tkinter.ttk`) nối thẳng tới **PostgreSQL 18** (CSDL `abc_fashion_v2`, 39 bảng) theo mô hình **MVC kiểu View – DAO – Entity**.

### 1.2. Nguồn của tài liệu

| Nguồn | Nội dung dùng trong tài liệu |
|---|---|
| Mô hình Visual Paradigm (`project.xml`) | 133 lớp + 34 enum, 28 package, thuộc tính, operation, quan hệ |
| Mã sinh tự động (`code/abc_fashion/`, 104 module, 4.044 dòng) | Tên file, chữ ký hàm, import, kế thừa |
| `frm_dao_classes.md` | Kiểu trả về và ý nghĩa của từng operation, luồng màn hình theo module |
| Chương 4 báo cáo (4.2 Data model, 4.3, 4.4) | Bảng, khoá ngoại, ràng buộc CHECK/UNIQUE, quy tắc nghiệp vụ, luồng L1–L5, component |

### 1.3. Tình trạng hiện tại của mã

Mã trong `code/abc_fashion/` là **bộ khung (skeleton)** sinh bằng forward engineering:

- Mọi lớp, thuộc tính, chữ ký hàm, import và kế thừa **đã có và đúng với mô hình**.
- Thân của hầu hết hàm là `raise NotImplementedError`. Chỉ có hai chỗ có mã thật: `DAO.__init__` mở kết nối PostgreSQL và `__init__` của các Frm gán tham số + tạo đối tượng DAO/gateway.
- Kiểu trả về **chưa có** trong chữ ký (mô hình VP không ghi kiểu trả về). Kiểu trả về đúng của từng hàm được ghi trong tài liệu này (lấy từ `frm_dao_classes.md`); nên thêm vào khi lập trình.

Việc còn lại là **lập trình thân hàm** theo hướng dẫn ở mục 6–11, giữ nguyên tên và tham số để mã còn khớp với thiết kế.

---

## 2. Kiến trúc tổng thể

### 2.1. Ba layer và một tầng hạ tầng

```
┌──────────────────────────────────────────────────────────────────────┐
│ VIEW LAYER            abc_fashion.view        53 lớp *Frm (tkinter)   │
│  account · catalogue · checkout · order · order_admin · product ·     │
│  promotion · inventory · returns · review · report                    │
└───────────────┬──────────────────────────────┬───────────────────────┘
                │ gọi operation                │ giữ / truyền đối tượng entity
                ▼                              │
┌──────────────────────────────────────────┐   │
│ CONTROL LAYER        abc_fashion.control │   │
│  dao/      34 lớp DAO (SQL, transaction) │   │
│  gateway/   5 lớp gọi hệ thống ngoài     │   │
└───────────────┬──────────────────────────┘   │
                │ tạo / đọc đối tượng          │
                ▼                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ MODEL LAYER           abc_fashion.model       41 entity + 34 enum     │
│  user · customer_data · audit · catalogue · inventory · sales ·       │
│  fulfilment · returns · review · assistant · stat                     │
└──────────────────────────────────────────────────────────────────────┘
                ▲ DAO ánh xạ dòng ↔ đối tượng           ▲ REST API
┌───────────────┴───────────────────────┐  ┌────────────┴──────────────┐
│ PostgreSQL 18 — abc_fashion_v2 (39 bảng)│ │ Payment · Shipping ·      │
│ SQL / TCP 5432 (psycopg)               │  │ Email/SMS · AI Model      │
└────────────────────────────────────────┘  └───────────────────────────┘
```

### 2.2. Trách nhiệm và quy tắc phụ thuộc

| Layer | Trách nhiệm | Được import | Cấm |
|---|---|---|---|
| `view` | Hiển thị màn hình, nhận thao tác, kiểm tra dữ liệu nhập, mở màn hình kế tiếp | `view`, `control.dao`, `control.gateway`, `model`, `tkinter` | Viết SQL; import `psycopg` |
| `control.dao` | Một DAO / bảng: SELECT, INSERT, UPDATE, transaction | `control.dao`, `model`, `psycopg` | Import `view`; hiển thị bất cứ gì; import `tkinter` |
| `control.gateway` | Gọi dịch vụ ngoài (thanh toán, vận chuyển, e-mail/SMS, AI) | `model`, HTTP client | Import `view`; truy cập CSDL |
| `model` | Dataclass dữ liệu + enum; phép tính thuần | thư viện chuẩn, `model` | Import layer khác |

Ba quy tắc khi viết mã:

1. **Chỉ gọi xuống**: view → control → model. Không có lời gọi ngược lên (DAO không bao giờ mở cửa sổ hay `messagebox`).
2. **Chỉ DAO chạm CSDL**, và chỉ qua kết nối của lớp gốc `DAO`; **chỉ gateway chạm hệ thống ngoài**.
3. **Dữ liệu đi giữa các layer bằng đối tượng entity** (`Order`, `Cart`, …), không bằng dict hay tuple SQL.

> **Quy ước đặt tên:** tên lớp entity / lớp trong mô hình VP **không có tiền tố `tbl`** (lớp `Order`). Tên **bảng** trong PostgreSQL vẫn là `"tblOrder"` (các câu SQL và dòng "Bảng: tblX" ở dưới là tên bảng thật). Tiền tố `tbl_` của widget Treeview (`tbl_order`) là chuyện khác, không đổi.

`check_gen.py` (mục 12.2) kiểm tra tự động quy tắc 1–2 trên câu lệnh import.

### 2.3. Component ↔ package

| Component (Hình 4.43) | Package / lớp |
|---|---|
| Account UI, Catalogue UI, Checkout UI, Customer Order UI, Inventory UI, Return UI | `view.account`, `view.catalogue`, `view.checkout`, `view.order`, `view.inventory`, `view.returns` |
| Back-office UI | `view.order_admin`, `view.product`, `view.promotion`, `view.review`, `view.report` |
| Account / Catalogue / Inventory / Sales / Return & Review / Report Data Access | các nhóm DAO trong `control.dao` (bảng ở mục 7.2) |
| DB Connection | `control/dao/dao.py` (lớp `DAO`) |
| Integration Gateways | `control/gateway/*` |
| Domain Model | `model/*` |

---

## 3. Môi trường và cách chạy

### 3.1. Yêu cầu

| Thành phần | Phiên bản / gói | Dùng cho |
|---|---|---|
| Python | ≥ 3.11 (cú pháp `X \| None`, `list[X]`, `dataclass(kw_only=True)`) | toàn bộ |
| tkinter | có sẵn trong Python trên Windows/macOS; Linux: `sudo apt install python3-tk` | view |
| psycopg 3 | `pip install "psycopg[binary]"` | `DAO` |
| tkcalendar | `pip install tkcalendar` | widget `DateEntry` (tiền tố `dte_`) |
| Pillow | `pip install pillow` | hiện ảnh sản phẩm / ảnh tìm kiếm trên `tk.Canvas` |
| requests (tuỳ chọn) | `pip install requests` | gateway gọi REST API thật |
| sounddevice (tuỳ chọn) | `pip install sounddevice` | ghi âm tìm kiếm bằng giọng nói |
| PostgreSQL | 18, CSDL `abc_fashion_v2`, schema `public` | lưu trữ |

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install "psycopg[binary]" tkcalendar pillow requests
```

### 3.2. Cơ sở dữ liệu

CSDL đã được tạo ở mục 4.2.6 của báo cáo (pgAdmin 4): 39 bảng, 56 khoá ngoại, 26 UNIQUE, 59 CHECK, 38 index, dữ liệu mẫu 147 dòng. Tên bảng và cột được tạo **trong dấu nháy kép** để giữ chữ hoa (`"tblOrder"`, `"customerId"`) — mọi câu SQL trong DAO **phải** viết đúng như vậy.

Chuỗi kết nối nằm ở `control/dao/dao.py`:

```python
DSN = "dbname=abc_fashion_v2 user=postgres host=localhost port=5432"
```

Nên đọc từ biến môi trường để không ghi mật khẩu vào mã:

```python
import os
DSN = os.environ.get("ABC_FASHION_DSN",
                     "dbname=abc_fashion_v2 user=postgres password=postgres host=localhost port=5432")
```

> Trước khi lập trình `ReviewDAO.add_review`, đọc mục 13 (bảng `Review` trong CSDL còn hai cột cũ).

### 3.3. Chạy ứng dụng

Đặt thư mục chứa `abc_fashion/` (tức `code/`) làm thư mục làm việc:

```bash
cd code
python -m abc_fashion.main
```

`main.py` mở `LoginFrm`. Kiểm tra bộ khung (không cần CSDL, không cần màn hình):

```bash
python check_gen.py .
# imported modules: 104 / layer violations: 0 / {...số lớp...}
```

---

## 4. Cấu trúc thư mục — từng file

Mỗi thư mục có `__init__.py` rỗng (đánh dấu package). Cột "Lớp" là lớp chứa trong file; chi tiết từng hàm ở mục 6–8.

```text
code/
├── vp2py.py                 sinh mã từ project.xml của Visual Paradigm (mục 12.1)
├── check_gen.py             kiểm tra import, quy tắc layer, số lớp (mục 12.2)
└── abc_fashion/
    ├── __init__.py
    ├── main.py              điểm khởi động: mở LoginFrm (mục 9.1)
    ├── view/                 VIEW LAYER — 11 package, mỗi Frm một file
    │   ├── account/
    │   │   ├── admin_home_frm.py             AdminHomeFrm: Trang chủ quản trị viên
    │   │   ├── audit_log_frm.py              AuditLogFrm: Xem nhật ký thay đổi
    │   │   ├── customer_home_frm.py          CustomerHomeFrm: Trang chủ của khách: tìm kiếm và đi tới các chức năng
    │   │   ├── edit_account_frm.py           EditAccountFrm: Khoá / mở / đặt lại mật khẩu / đổi vai trò
    │   │   ├── edit_address_frm.py           EditAddressFrm: Thêm / sửa một địa chỉ
    │   │   ├── link_payment_method_frm.py    LinkPaymentMethodFrm: Liên kết thẻ / ví / tài khoản ngân hàng
    │   │   ├── login_frm.py                  LoginFrm: Màn hình đầu tiên
    │   │   ├── profile_frm.py                ProfileFrm: Hồ sơ khách: thông tin, sổ địa chỉ, phương thức thanh toán, cỡ đã lưu
    │   │   ├── register_frm.py               RegisterFrm: Đăng ký tài khoản khách
    │   │   └── search_account_frm.py         SearchAccountFrm: Tìm tài khoản
    │   ├── catalogue/
    │   │   ├── assistant_frm.py              AssistantFrm: Hỏi trợ lý AI về sản phẩm
    │   │   ├── browse_style_frm.py           BrowseStyleFrm: Duyệt sản phẩm theo danh mục có bộ lọc
    │   │   ├── search_style_frm.py           SearchStyleFrm: Tìm kiếm bằng chữ, ảnh, giọng nói
    │   │   └── style_detail_frm.py           StyleDetailFrm: Trang chi tiết sản phẩm
    │   ├── checkout/
    │   │   ├── cart_frm.py                   CartFrm: Giỏ hàng
    │   │   ├── checkout_frm.py               CheckoutFrm: Thanh toán
    │   │   └── confirm_order_frm.py          ConfirmOrderFrm: Kết quả đặt hàng
    │   ├── inventory/
    │   │   ├── adjust_stock_frm.py           AdjustStockFrm: Điều chỉnh tồn có lý do
    │   │   ├── confirm_restock_frm.py        ConfirmRestockFrm: Nhà cung cấp xác nhận / từ chối phiếu
    │   │   ├── edit_restock_request_frm.py   EditRestockRequestFrm: Lập / sửa phiếu nhập hàng
    │   │   ├── manage_restock_frm.py         ManageRestockFrm: Danh sách phiếu nhập hàng
    │   │   ├── select_variant_frm.py         SelectVariantFrm: Chọn một biến thể
    │   │   ├── stock_level_frm.py            StockLevelFrm: Tồn kho theo kho
    │   │   ├── stock_movement_frm.py         StockMovementFrm: Sổ kho của một biến thể
    │   │   ├── supplier_home_frm.py          SupplierHomeFrm: Trang chủ nhà cung cấp: các phiếu được gửi tới họ
    │   │   └── warehouse_home_frm.py         WarehouseHomeFrm: Trang chủ nhân viên kho
    │   ├── order/
    │   │   ├── cancel_request_frm.py         CancelRequestFrm: Huỷ đơn / gửi yêu cầu huỷ
    │   │   ├── order_detail_frm.py           OrderDetailFrm: Chi tiết đơn và các hành động sau mua
    │   │   ├── order_list_frm.py             OrderListFrm: Danh sách đơn của khách
    │   │   ├── return_request_frm.py         ReturnRequestFrm: Yêu cầu trả / đổi hàng
    │   │   ├── review_frm.py                 ReviewFrm: Đánh giá sản phẩm đã mua
    │   │   └── track_shipment_frm.py         TrackShipmentFrm: Theo dõi kiện
    │   ├── order_admin/
    │   │   ├── manage_order_frm.py           ManageOrderFrm: Xử lý đơn: chuyển trạng thái, huỷ, duyệt yêu cầu huỷ, hoàn tiền
    │   │   ├── manager_home_frm.py           ManagerHomeFrm: Trang chủ quản lý
    │   │   └── search_order_frm.py           SearchOrderFrm: Tìm đơn
    │   ├── product/
    │   │   ├── edit_style_frm.py             EditStyleFrm: Thêm / sửa style với vật liệu, bảng cỡ, media, biến thể
    │   │   ├── edit_variant_frm.py           EditVariantFrm: Thêm / sửa một biến thể
    │   │   └── manage_style_frm.py           ManageStyleFrm: Danh sách sản phẩm cho quản trị
    │   ├── promotion/
    │   │   ├── edit_promotion_frm.py         EditPromotionFrm: Thêm / sửa khuyến mãi, style áp dụng, voucher
    │   │   ├── manage_promotion_frm.py       ManagePromotionFrm: Danh sách khuyến mãi
    │   │   ├── merchandiser_home_frm.py      MerchandiserHomeFrm: Trang chủ merchandiser
    │   │   └── select_style_frm.py           SelectStyleFrm: Chọn nhiều style
    │   ├── report/
    │   │   ├── marketing_home_frm.py         MarketingHomeFrm: Trang chủ marketing
    │   │   ├── return_detail_frm.py          ReturnDetailFrm: Chi tiết các dòng trả của một style
    │   │   ├── return_report_frm.py          ReturnReportFrm: Báo cáo trả hàng theo style
    │   │   ├── sales_detail_frm.py           SalesDetailFrm: Chi tiết các dòng đơn của một style
    │   │   ├── sales_report_frm.py           SalesReportFrm: Báo cáo doanh số theo style
    │   │   └── select_report_frm.py          SelectReportFrm: Chọn loại báo cáo
    │   ├── returns/
    │   │   ├── customer_service_home_frm.py  CustomerServiceHomeFrm: Trang chủ chăm sóc khách hàng
    │   │   ├── inspect_return_frm.py         InspectReturnFrm: Kho kiểm tra hàng trả về
    │   │   ├── process_return_frm.py         ProcessReturnFrm: Xử lý yêu cầu trả / đổi
    │   │   └── search_return_request_frm.py  SearchReturnRequestFrm: Danh sách yêu cầu trả hàng
    │   └── review/
    │       └── manage_review_frm.py          ManageReviewFrm: Duyệt đánh giá
    ├── control/              CONTROL LAYER
    │   ├── dao/
    │   │   ├── address_dao.py                AddressDAO: Sổ địa chỉ của khách
    │   │   ├── assistant_turn_dao.py         AssistantTurnDAO: Nhật ký trợ lý AI
    │   │   ├── audit_log_entry_dao.py        AuditLogEntryDAO: Nhật ký thay đổi của nhân viên
    │   │   ├── cart_dao.py                   CartDAO: Giỏ hàng lưu trên server, một giỏ cho mỗi khách
    │   │   ├── category_dao.py               CategoryDAO: Cây danh mục
    │   │   ├── collection_dao.py             CollectionDAO: Bộ sưu tập theo mùa
    │   │   ├── customer_dao.py               CustomerDAO: Hồ sơ khách hàng
    │   │   ├── dao.py                        DAO: 
    │   │   ├── material_component_dao.py     MaterialComponentDAO: Thành phần vải của style
    │   │   ├── notification_dao.py           NotificationDAO: Thông báo gửi khách
    │   │   ├── order_dao.py                  OrderDAO: Đơn hàng
    │   │   ├── order_item_dao.py             OrderItemDAO: Dòng đơn — dùng cho báo cáo chi tiết
    │   │   ├── payment_dao.py                PaymentDAO: Các lần thu
    │   │   ├── payment_method_dao.py         PaymentMethodDAO: Phương thức thanh toán đã liên kết
    │   │   ├── product_media_dao.py          ProductMediaDAO: Ảnh / video của style
    │   │   ├── product_variant_dao.py        ProductVariantDAO: SKU: một cỡ + một màu của style, có giá
    │   │   ├── promotion_dao.py              PromotionDAO: Chương trình khuyến mãi
    │   │   ├── restock_request_dao.py        RestockRequestDAO: Phiếu yêu cầu nhập hàng gửi nhà cung cấp
    │   │   ├── return_item_dao.py            ReturnItemDAO: Dòng trả — dùng cho báo cáo chi tiết
    │   │   ├── return_request_dao.py         ReturnRequestDAO: Yêu cầu trả / đổi hàng
    │   │   ├── return_stat_dao.py            ReturnStatDAO: Số liệu trả hàng theo style cho báo cáo
    │   │   ├── review_dao.py                 ReviewDAO: Đánh giá của một dòng đơn đã mua
    │   │   ├── saved_size_dao.py             SavedSizeDAO: Cỡ đã lưu của khách theo danh mục
    │   │   ├── shipment_dao.py               ShipmentDAO: Kiện hàng
    │   │   ├── size_chart_entry_dao.py       SizeChartEntryDAO: Bảng số đo theo cỡ
    │   │   ├── staff_member_dao.py           StaffMemberDAO: Hồ sơ nhân viên và vai trò
    │   │   ├── stock_level_dao.py            StockLevelDAO: Tồn kho: **mỗi biến thể đúng một dòng** ở một kho
    │   │   ├── stock_location_dao.py         StockLocationDAO: Kho hàng
    │   │   ├── stock_movement_dao.py         StockMovementDAO: Sổ kho: mỗi thay đổi tồn là một dòng
    │   │   ├── style_dao.py                  StyleDAO: Mẫu sản phẩm
    │   │   ├── style_stat_dao.py             StyleStatDAO: Số liệu bán hàng theo style cho báo cáo
    │   │   ├── supplier_dao.py               SupplierDAO: Nhà cung cấp
    │   │   ├── user_dao.py                   UserDAO: Tài khoản đăng nhập của mọi loại người dùng
    │   │   └── voucher_dao.py                VoucherDAO: Mã giảm giá của một chương trình
    │   └── gateway/
    │       ├── assistant_engine.py           AssistantEngine: 
    │       ├── notification_gateway.py       NotificationGateway: 
    │       ├── payment_gateway.py            PaymentGateway: 
    │       ├── search_engine.py              SearchEngine: 
    │       └── shipping_gateway.py           ShippingGateway: 
    └── model/                MODEL LAYER — mỗi package một file
        ├── assistant.py          AssistantMode, GroundingCheck, AssistantTurn, GroundingEvent
        ├── audit.py              AuditAction, AuditLogEntry
        ├── catalogue.py          FitType, Measure, MediaType, Season, StyleStatus, VariantStatus, Category, Collection, MaterialComponent, ProductMedia, ProductVariant, SizeChartEntry, Style
        ├── customer_data.py      Channel, LinkedMethodType, NotificationEvent, NotificationStatus, Address, Notification, PaymentMethod, SavedSize
        ├── fulfilment.py         ShipmentDirection, ShipmentStatus, Shipment, ShipmentEvent, ShipmentRecord
        ├── inventory.py          MovementReason, RestockStatus, RestockItem, RestockRequest, StockLevel, StockLocation, StockMovement
        ├── returns.py            InspectionResult, Resolution, ReturnReason, ReturnStatus, ReturnType, ReturnEvidence, ReturnItem, ReturnRequest
        ├── review.py             FitVote, ReviewStatus, Review
        ├── sales.py              DeliveryService, DiscountType, OrderStatus, PaymentKind, PaymentMethodType, PaymentStatus, PromoType, PromotionStatus, Cart, CartItem, Order, OrderItem, OrderVoucher, Payment, Promotion, PromotionStyle, Voucher
        ├── stat.py               ReturnStat, StyleStat
        └── user.py               AccountStatus, StaffRole, User, Customer, StaffMember, Supplier
```

---

## 5. Quy ước lập trình

### 5.1. Đặt tên

| Thành phần | Quy ước | Ví dụ |
|---|---|---|
| Entity | tên bảng, tiền tố `tbl` | `Order`, `CartItem` |
| Lớp thống kê | không tiền tố | `StyleStat`, `ReturnStat` |
| View | hậu tố `Frm`, file `snake_case` + `_frm.py` | `CheckoutFrm` → `checkout_frm.py` |
| DAO | hậu tố `DAO`, file `..._dao.py` | `OrderDAO` → `order_dao.py` |
| Operation DAO | động từ + entity | `add_order`, `get_cart_by_customer`, `search_style` |
| Handler View | `on_<hành động>` — một handler / nút | `on_place_order` |
| Cột khoá ngoại | camelCase + `Id`, giống CSDL | `customerId`, `productVariantId` |
| Thuộc tính đối tượng DAO trong Frm | `snake_case` của tên lớp | `self.order_dao`, `self.payment_gateway` |

### 5.2. Tiền tố widget (thuộc tính của Frm)

| Tiền tố | Widget | Ghi chú |
|---|---|---|
| `txt_` | `ttk.Entry` | mật khẩu: `show="*"` |
| `txa_` | `tk.Text` | đoạn văn nhiều dòng |
| `btn_` | `ttk.Button` | `command=self.on_…` |
| `lbl_` | `ttk.Label` | hiển thị / thông báo lỗi |
| `cbo_` | `ttk.Combobox` | `state="readonly"` cho danh sách cố định |
| `chk_` | `ttk.Checkbutton` | gắn `tk.BooleanVar` |
| `rdo_` | `ttk.Radiobutton` | một nhóm dùng chung `tk.StringVar` |
| `spn_` | `ttk.Spinbox` | `from_`, `to` |
| `tbl_` / `tree_` | `ttk.Treeview` | bảng / cây |
| `dte_` | `tkcalendar.DateEntry` | **cần** `from tkcalendar import DateEntry` (mã sinh chưa import) |
| `cnv_` | `tk.Canvas` | ảnh |
| `list_…` | `list[X]` | dữ liệu đang hiển thị trong bảng tương ứng |

### 5.3. Kiểu dữ liệu

| Python (model) | PostgreSQL | Ghi chú |
|---|---|---|
| `int` | `integer` | tiền (VND) là số nguyên, không dùng float |
| `str` | `character varying(n)` | |
| `float` | `real` | chỉ `value_cm`, `return_rate` |
| `bool` | `boolean` | |
| `date` / `datetime` | `date` / `timestamp without time zone` | dùng `datetime.now()` của máy chủ CSDL (`now()`) cho thống nhất |
| Enum | `character varying(50)` + CHECK | lưu `enum.value` (chữ thường, vd. `'pending_payment'`) |
| `list[str]` (`preferred_colours`) | `character varying(255)` | nối bằng dấu phẩy |

Mọi trường của entity mặc định `None` (`= None`) để tạo được đối tượng từ một phần dòng (ví dụ chỉ có `email`, `password` lúc đăng nhập).

### 5.4. Kiểu trả về chuẩn của DAO

| Loại operation | Trả về | Khi lỗi |
|---|---|---|
| `add_…`, `update_…`, `delete_…`, `cancel_…`, `save_…`, `receive_…`, `reserve_…`, `adjust_…`, `clear_…` | `bool` (`True` = thành công) và điền `id` mới vào đối tượng | `False` cho lỗi nghiệp vụ dự kiến (trùng UNIQUE, hết hàng, chuyển trạng thái sai); lỗi kết nối / lỗi lập trình thì để exception bay lên |
| `get_…_by_…` một đối tượng | `X \| None` | `None` nếu không có |
| `get_…`, `search_…` danh sách | `list[X]` | danh sách rỗng |
| `check_login`, `is_…` | `bool` | |

### 5.5. Xử lý lỗi ở view

- Lỗi nhập liệu: hiện ở `lbl_message` (hoặc `messagebox.showwarning`) và **không** gọi DAO.
- DAO trả `False`: thông báo nghiệp vụ dễ hiểu ("Sản phẩm vừa hết hàng").
- Exception (mất kết nối, lỗi SQL): bắt ở handler, `messagebox.showerror("Lỗi hệ thống", str(e))`, ghi log; không để chương trình tắt.

### 5.6. Không sửa chữ ký

Giữ nguyên tên lớp, tên hàm, tên và thứ tự tham số đã sinh. Được phép: thêm kiểu trả về, thêm hàm **riêng tư** bắt đầu bằng `_` (ví dụ `_reload`, `_recalc`, `_to_entity`), thêm import cần thiết (đúng quy tắc layer). Khi thiết kế cần đổi, sửa trong Visual Paradigm rồi sinh lại (mục 12).

---

## 6. Model layer — lớp thực thể và enum

### 6.1. Cách tổ chức

- Mỗi package model là **một file** `model/<package>.py` chứa các enum rồi các entity của package đó.
- Entity là `@dataclass(kw_only=True)`: tạo bằng tham số tên (`Order(order_no="ORD-…", status=OrderStatus.PENDING_PAYMENT)`), mọi trường mặc định `None`.
- Enum: `class OrderStatus(Enum): PENDING_PAYMENT = "pending_payment"` — **giá trị trùng với giá trị trong CHECK của CSDL**. Ghi xuống CSDL dùng `.value`, đọc lên dùng `OrderStatus(row["status"])`.
- Quan hệ giữa entity được ghi trong docstring (`Relationships: OrderItem (composition, 1..*) …`); trong dữ liệu chúng là các cột khoá ngoại (`customerId`, …). Khi cần một danh sách con (các dòng của đơn, các dòng của giỏ), DAO **gắn động** thuộc tính lên đối tượng: `order.items = [...]`, `cart.items = [...]`, `order.payments`, `order.shipments`, `request.items`, `promotion.styles`, `promotion.vouchers`, `turn.grounding_events`. Đây là quy ước của dự án; mọi chỗ dùng phải thống nhất các tên này.

### 6.2. Kế thừa và cái bẫy trường `id`

| Lớp con | Lớp cha | Ý nghĩa |
|---|---|---|
| `Customer`, `StaffMember`, `Supplier` | `User` | ba loại người dùng có chung tài khoản |
| `CartItem` | `ProductVariant` | dòng giỏ "là" một biến thể với số lượng |
| `OrderItem` | `CartItem` | dòng đơn là dòng giỏ đã đặt (đơn giá đóng băng) |
| `ReturnItem` | `OrderItem` | dòng trả là dòng đơn được trả |
| `StyleStat`, `ReturnStat` | `Style` | style kèm số liệu |
| `XxxDAO` (33 lớp) | `DAO` | dùng chung kết nối |

Dataclass con khai báo lại trường `id` nên **`id` luôn là khoá của bảng con**: `Customer.id` là id trong `Customer`, id tài khoản nằm ở `userId`; `OrderItem.id` là id dòng đơn, id biến thể nằm ở `productVariantId`; `ReturnItem.id` là id dòng trả, id dòng đơn gốc ở `orderItemId`. Các trường kế thừa còn lại (`email`, `sku`, `price`, `unit_price`, …) được DAO điền bằng JOIN để màn hình hiển thị mà không cần đọc thêm.

### 6.3. Tham chiếu từng file model

#### `model/assistant.py` — Nhật ký trợ lý AI (Chương 3).

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `AssistantMode` | `model`, `basic` |
| `GroundingCheck` | `price`, `stock`, `fit`, `fabric`, `popularity`, `policy`, `health` |

**`AssistantTurn`** — Một lượt hỏi–đáp; `customerId` NULL với khách vãng lai.

Quan hệ: GroundingEvent (composition, 0..*); Customer (aggregation, 0..1); Style (aggregation, 0..1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `question` | `str` | varchar |  |
| `answer` | `str` | varchar |  |
| `mode` | `AssistantMode` | varchar(50) + CHECK (enum) |  |
| `model_name` | `str` | varchar |  |
| `latency_ms` | `int` | integer |  |
| `created_at` | `datetime` | timestamp |  |
| `customerId` | `int` | integer | khoá ngoại |
| `styleId` | `int` | integer | khoá ngoại |

**`GroundingEvent`** — Câu bị loại khỏi câu trả lời vì không khớp dữ liệu (giá, tồn kho, …).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `check_name` | `GroundingCheck` | varchar(50) + CHECK (enum) |  |
| `removed_text` | `str` | varchar |  |
| `assistantTurnId` | `int` | integer | khoá ngoại |

#### `model/audit.py` — Nhật ký.

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `AuditAction` | `create`, `update`, `deactivate`, `adjust_stock`, `suspend_account`, `reset_password` |

**`AuditLogEntry`** — Mỗi thay đổi quan trọng của nhân viên (tạo / sửa / ngừng sản phẩm, điều chỉnh kho, khoá tài khoản, đặt lại mật khẩu).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `entity` | `str` | varchar |  |
| `action` | `AuditAction` | varchar(50) + CHECK (enum) |  |
| `changes` | `str` | varchar |  |
| `created_at` | `datetime` | timestamp |  |
| `staffMemberId` | `int` | integer | khoá ngoại |

#### `model/catalogue.py` — Danh mục sản phẩm.

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `FitType` | `slim`, `regular`, `relaxed`, `oversized` |
| `Measure` | `chest`, `waist`, `hip`, `length`, `sleeve`, `inseam`, `foot_length` |
| `MediaType` | `image`, `video` |
| `Season` | `spring_summer`, `autumn_winter`, `all_season` |
| `StyleStatus` | `draft`, `active`, `inactive` |
| `VariantStatus` | `active`, `discontinued` |

**`Category`** — Cây danh mục; `parentId` NULL = gốc.

Quan hệ: Category (association, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `name` | `str` | varchar |  |
| `parentId` | `int` | integer | khoá ngoại |

**`Collection`** — Bộ sưu tập theo mùa, năm.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `name` | `str` | varchar |  |
| `season` | `Season` | varchar(50) + CHECK (enum) |  |
| `year` | `int` | integer |  |

**`MaterialComponent`** — Thành phần vải; `percent` 1–100, tổng của một style = 100 (kiểm ở ứng dụng).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `material` | `str` | varchar |  |
| `percent` | `int` | integer |  |
| `styleId` | `int` | integer | khoá ngoại |

**`ProductMedia`** — Ảnh / video, thứ tự `sort_order`, có thể gắn màu.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `url` | `str` | varchar |  |
| `media_type` | `MediaType` | varchar(50) + CHECK (enum) |  |
| `colour` | `str` | varchar |  |
| `sort_order` | `int` | integer |  |
| `styleId` | `int` | integer | khoá ngoại |

**`ProductVariant`** — SKU = style + cỡ + màu, có giá (VND, số nguyên). UNIQUE `sku` và (`styleId`,`size_label`,`colour`).

Quan hệ: RestockItem (aggregation, 1); StockLevel (aggregation, 1); StockMovement (aggregation, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `sku` | `str` | varchar |  |
| `size_label` | `str` | varchar |  |
| `colour` | `str` | varchar |  |
| `price` | `int` | integer |  |
| `status` | `VariantStatus` | varchar(50) + CHECK (enum) |  |
| `styleId` | `int` | integer | khoá ngoại |

**`SizeChartEntry`** — Một số đo của một cỡ; `value_cm > 0` (cột `real`).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `size_label` | `str` | varchar |  |
| `measure` | `Measure` | varchar(50) + CHECK (enum) |  |
| `value_cm` | `float` | real |  |
| `styleId` | `int` | integer | khoá ngoại |

**`Style`** — Mẫu sản phẩm. `code` UNIQUE. `collectionId` tuỳ chọn (ON DELETE SET NULL). Hợp thành bởi biến thể, vật liệu, bảng cỡ, media.

Quan hệ: Category (aggregation, 1); ProductMedia (composition, 0..*); Supplier (aggregation, 1); MaterialComponent (composition, 1..*); SizeChartEntry (composition, 0..*); Collection (aggregation, 0..1); ProductVariant (composition, 1..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `code` | `str` | varchar |  |
| `name` | `str` | varchar |  |
| `description` | `str` | varchar |  |
| `brand` | `str` | varchar |  |
| `fit_type` | `FitType` | varchar(50) + CHECK (enum) |  |
| `care_instructions` | `str` | varchar |  |
| `features` | `str` | varchar |  |
| `model_info` | `str` | varchar |  |
| `status` | `StyleStatus` | varchar(50) + CHECK (enum) |  |
| `categoryId` | `int` | integer | khoá ngoại |
| `supplierId` | `int` | integer | khoá ngoại |
| `collectionId` | `int` | integer | khoá ngoại |

#### `model/customer_data.py` — Dữ liệu riêng của khách.

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `Channel` | `email`, `sms`, `app` |
| `LinkedMethodType` | `card`, `e_wallet`, `bank_account` |
| `NotificationEvent` | `order_confirmed`, `order_shipped`, `order_delivered`, `order_cancelled`, `return_authorised`, `return_rejected`, `refund_completed`, `exchange_shipped` |
| `NotificationStatus` | `queued`, `sent`, `failed` |

**`Address`** — Sổ địa chỉ; một địa chỉ `is_default` cho mỗi khách (quy tắc ứng dụng). FK `customerId` ON DELETE CASCADE.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `recipient_name` | `str` | varchar |  |
| `phone` | `str` | varchar |  |
| `street` | `str` | varchar |  |
| `ward` | `str` | varchar |  |
| `district` | `str` | varchar |  |
| `city` | `str` | varchar |  |
| `is_default` | `bool` | boolean |  |
| `customerId` | `int` | integer | khoá ngoại |

**`Notification`** — Thông báo đã gửi / chờ gửi cho khách.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `channel` | `Channel` | varchar(50) + CHECK (enum) |  |
| `event_type` | `NotificationEvent` | varchar(50) + CHECK (enum) |  |
| `message` | `str` | varchar |  |
| `status` | `NotificationStatus` | varchar(50) + CHECK (enum) |  |
| `sent_at` | `datetime` | timestamp |  |
| `customerId` | `int` | integer | khoá ngoại |

**`PaymentMethod`** — Phương thức đã liên kết; chỉ `masked_number` (vd. `**** 4242`). FK `customerId` CASCADE.

Quan hệ: Customer (aggregation, 1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `provider` | `str` | varchar |  |
| `method_type` | `LinkedMethodType` | varchar(50) + CHECK (enum) |  |
| `masked_number` | `str` | varchar |  |
| `is_default` | `bool` | boolean |  |
| `customerId` | `int` | integer | khoá ngoại |

**`SavedSize`** — Một cỡ đã lưu cho mỗi (khách, danh mục).

Quan hệ: Customer (aggregation, 1); Category (aggregation, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `size_label` | `str` | varchar |  |
| `customerId` | `int` | integer | khoá ngoại |
| `categoryId` | `int` | integer | khoá ngoại |

#### `model/fulfilment.py` — Vận chuyển.

Phụ thuộc: `from abc_fashion.model.sales import DeliveryService`

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `ShipmentDirection` | `outbound`, `return` |
| `ShipmentStatus` | `requested`, `picked_up`, `in_transit`, `delivered`, `failed` |

**`Shipment`** — Kiện hàng: `outbound` (giao) hoặc `return` (lấy về); CHECK `direction = outbound OR returnRequestId IS NOT NULL`; mỗi kiện rời một kho.

Quan hệ: ShipmentEvent (composition, 0..*); StockLocation (aggregation, 1); ShipmentRecord (aggregation, 1..*); ReturnRequest (aggregation, 0..1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `direction` | `ShipmentDirection` | varchar(50) + CHECK (enum) |  |
| `carrier` | `str` | varchar |  |
| `service_level` | `DeliveryService` | varchar(50) + CHECK (enum) |  |
| `tracking_no` | `str` | varchar |  |
| `fee` | `int` | integer |  |
| `status` | `ShipmentStatus` | varchar(50) + CHECK (enum) |  |
| `delivered_at` | `datetime` | timestamp |  |
| `orderId` | `int` | integer | khoá ngoại |
| `stockLocationId` | `int` | integer | khoá ngoại |
| `returnRequestId` | `int` | integer | khoá ngoại |

**`ShipmentEvent`** — Lịch sử theo dõi của kiện.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `status` | `ShipmentStatus` | varchar(50) + CHECK (enum) |  |
| `occurred_at` | `datetime` | timestamp |  |
| `note` | `str` | varchar |  |
| `shipmentId` | `int` | integer | khoá ngoại |

**`ShipmentRecord`** — Nội dung kiện: dòng đơn + số lượng (tách kiện khi hàng ở nhiều kho).

Quan hệ: OrderItem (aggregation, 1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `quantity` | `int` | integer |  |
| `shipmentId` | `int` | integer | khoá ngoại |
| `orderItemId` | `int` | integer | khoá ngoại |

#### `model/inventory.py` — Kho, tồn kho, sổ kho, nhập hàng.

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `MovementReason` | `sale`, `return`, `restock`, `adjustment` |
| `RestockStatus` | `draft`, `sent`, `confirmed`, `received`, `cancelled` |

**`RestockItem`** — Dòng phiếu nhập (`quantity > 0`).

Quan hệ: RestockRequest (aggregation, 1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `quantity` | `int` | integer |  |
| `restockRequestId` | `int` | integer | khoá ngoại |
| `productVariantId` | `int` | integer | khoá ngoại |

**`RestockRequest`** — Phiếu nhập hàng; `request_no` UNIQUE; trạng thái RestockStatus.

Quan hệ: Supplier (aggregation, 1); StaffMember (aggregation, 0..1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `request_no` | `str` | varchar |  |
| `status` | `RestockStatus` | varchar(50) + CHECK (enum) |  |
| `created_at` | `datetime` | timestamp |  |
| `expected_date` | `date` | date |  |
| `supplier_note` | `str` | varchar |  |
| `confirm_at` | `date` | date |  |
| `supplierId` | `int` | integer | khoá ngoại |
| `stockLocationId` | `int` | integer | khoá ngoại |
| `staffMemberId` | `int` | integer | khoá ngoại |

**`StockLevel`** — Một dòng cho mỗi biến thể (UNIQUE `productVariantId`). CHECK `0 ≤ reserved ≤ on_hand`, `available = on_hand − reserved` → mọi UPDATE phải sửa cả `available`.

Quan hệ: StockLocation (aggregation, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `on_hand` | `int` | integer |  |
| `reserved` | `int` | integer |  |
| `reorder_point` | `int` | integer |  |
| `available` | `int` | integer |  |
| `productVariantId` | `int` | integer | khoá ngoại |
| `stockLocationId` | `int` | integer | khoá ngoại |

**`StockLocation`** — Kho hàng.

Quan hệ: RestockRequest (aggregation, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `name` | `str` | varchar |  |
| `address` | `str` | varchar |  |

**`StockMovement`** — Sổ kho: `quantity_change` (+ nhập / − xuất), `reason` (sale / return / restock / adjustment), `reference` (mã đơn, mã phiếu, mã trả).

Quan hệ: StaffMember (aggregation, 0..1); StockLocation (aggregation, 1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `quantity_change` | `int` | integer |  |
| `reason` | `MovementReason` | varchar(50) + CHECK (enum) |  |
| `reference` | `str` | varchar |  |
| `note` | `str` | varchar |  |
| `created_at` | `datetime` | timestamp |  |
| `productVariantId` | `int` | integer | khoá ngoại |
| `stockLocationId` | `int` | integer | khoá ngoại |
| `staffMemberId` | `int` | integer | khoá ngoại |

#### `model/returns.py` — Trả / đổi hàng.

Phụ thuộc: `from abc_fashion.model.catalogue import MediaType`; `from abc_fashion.model.sales import OrderItem`

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `InspectionResult` | `pending`, `passed`, `failed` |
| `Resolution` | `refund`, `exchange` |
| `ReturnReason` | `too_small`, `too_large`, `defect`, `wrong_item`, `not_as_described`, `changed_mind` |
| `ReturnStatus` | `requested`, `authorised`, `rejected`, `in_transit`, `inspected`, `refunded`, `exchanged`, `closed` |
| `ReturnType` | `return`, `exchange` |

**`ReturnEvidence`** — Ảnh / video bằng chứng.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `url` | `str` | varchar |  |
| `media_type` | `MediaType` | varchar(50) + CHECK (enum) |  |
| `returnRequestId` | `int` | integer | khoá ngoại |

**`ReturnItem`** (kế thừa `OrderItem`) — Dòng trả; kế thừa `OrderItem` trong model; `orderItemId` trỏ dòng đơn gốc; kết quả kiểm tra.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `quantity` | `int` | integer |  |
| `inspection_result` | `InspectionResult` | varchar(50) + CHECK (enum) |  |
| `inspection_note` | `str` | varchar |  |
| `returnRequestId` | `int` | integer | khoá ngoại |
| `orderItemId` | `int` | integer | khoá ngoại |

**`ReturnRequest`** — Yêu cầu trả / đổi; UNIQUE `orderId` (mỗi đơn một yêu cầu).

Quan hệ: ReturnEvidence (composition, 0..*); StaffMember (aggregation, 0..1); ReturnItem (composition, 1..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `return_no` | `str` | varchar |  |
| `return_type` | `ReturnType` | varchar(50) + CHECK (enum) |  |
| `reason_code` | `ReturnReason` | varchar(50) + CHECK (enum) |  |
| `reason_detail` | `str` | varchar |  |
| `desired_resolution` | `Resolution` | varchar(50) + CHECK (enum) |  |
| `status` | `ReturnStatus` | varchar(50) + CHECK (enum) |  |
| `requested_at` | `datetime` | timestamp |  |
| `decided_at` | `datetime` | timestamp |  |
| `decision_note` | `str` | varchar |  |
| `orderId` | `int` | integer | khoá ngoại |
| `staffMemberId` | `int` | integer | khoá ngoại |

#### `model/review.py` — Đánh giá.

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `FitVote` | `runs_small`, `true_to_size`, `runs_large` |
| `ReviewStatus` | `pending`, `approved`, `rejected` |

**`Review`** — Đánh giá một dòng đơn (UNIQUE `orderItemId`); `rating` 1–5; `status` qua kiểm duyệt.

Quan hệ: StaffMember (aggregation, 0..1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `rating` | `int` | integer |  |
| `body` | `str` | varchar |  |
| `size_purchased` | `str` | varchar |  |
| `fit_vote` | `FitVote` | varchar(50) + CHECK (enum) |  |
| `status` | `ReviewStatus` | varchar(50) + CHECK (enum) |  |
| `moderation_note` | `str` | varchar |  |
| `created_at` | `datetime` | timestamp |  |
| `orderItemId` | `int` | integer | khoá ngoại |
| `staffMemberId` | `int` | integer | khoá ngoại |

#### `model/sales.py` — Giỏ hàng, khuyến mãi, đơn hàng, thanh toán.

Phụ thuộc: `from abc_fashion.model.catalogue import ProductVariant`

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `DeliveryService` | `standard`, `express` |
| `DiscountType` | `percent`, `fixed_amount` |
| `OrderStatus` | `pending_payment`, `confirmed`, `processing`, `partially_shipped`, `shipped`, `delivered`, `completed`, `cancelled` |
| `PaymentKind` | `charge`, `refund` |
| `PaymentMethodType` | `cod`, `card`, `e_wallet`, `bank_transfer` |
| `PaymentStatus` | `pending`, `succeeded`, `failed` |
| `PromoType` | `seasonal`, `flash_sale`, `clearance`, `loyalty` |
| `PromotionStatus` | `draft`, `active`, `ended` |

**`Cart`** — Một giỏ / khách (UNIQUE `customerId`).

Quan hệ: Customer (aggregation, 1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `updated_at` | `datetime` | timestamp |  |
| `subtotal` | `int` | integer |  |
| `customerId` | `int` | integer | khoá ngoại |

**`CartItem`** (kế thừa `ProductVariant`) — Dòng giỏ. Kế thừa `ProductVariant` trong model (dòng giỏ "là" một biến thể) → khi đọc nên điền luôn `sku`, `price`, … của biến thể. `quantity > 0`.

Quan hệ: Cart (aggregation, 1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `quantity` | `int` | integer |  |
| `added_at` | `datetime` | timestamp |  |
| `cartId` | `int` | integer | khoá ngoại |
| `productVariantId` | `int` | integer | khoá ngoại |

**`Order`** — Đơn hàng; `order_no` UNIQUE; CHECK `grand_total = subtotal − discount + shipping_fee`. Không có cột địa chỉ (xem mục 13).

Quan hệ: OrderItem (composition, 1..*); Customer (aggregation, 1); Payment (composition, 0..*); Shipment (composition, 0..*); ReturnRequest (composition, 0..1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `order_no` | `str` | varchar |  |
| `status` | `OrderStatus` | varchar(50) + CHECK (enum) |  |
| `placed_at` | `datetime` | timestamp |  |
| `subtotal` | `int` | integer |  |
| `discount` | `int` | integer |  |
| `shipping_fee` | `int` | integer |  |
| `grand_total` | `int` | integer |  |
| `delivery_service` | `DeliveryService` | varchar(50) + CHECK (enum) |  |
| `note` | `str` | varchar |  |
| `cancel_reason` | `str` | varchar |  |
| `customerId` | `int` | integer | khoá ngoại |

**`OrderItem`** (kế thừa `CartItem`) — Dòng đơn: `unit_price`, `discount` đóng băng lúc đặt; CHECK `line_total = quantity × unit_price − discount`; UNIQUE (`orderId`,`productVariantId`).

Quan hệ: Review (composition, 0..1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `quantity` | `int` | integer |  |
| `unit_price` | `int` | integer |  |
| `discount` | `int` | integer |  |
| `line_total` | `int` | integer |  |
| `orderId` | `int` | integer | khoá ngoại |
| `productVariantId` | `int` | integer | khoá ngoại |

**`OrderVoucher`** — Bảng nối Order M:N Voucher; UNIQUE (`orderId`,`voucherId`).

Quan hệ: Voucher (aggregation, Unspecified); Order (aggregation, Unspecified).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `orderId` | `int` | integer | khoá ngoại |
| `voucherId` | `int` | integer | khoá ngoại |

**`Payment`** — Lần thu (`charge`) / hoàn (`refund`); `transaction_ref` của cổng thanh toán.

Quan hệ: PaymentMethod (aggregation, 1).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `kind` | `PaymentKind` | varchar(50) + CHECK (enum) |  |
| `method` | `PaymentMethodType` | varchar(50) + CHECK (enum) |  |
| `amount` | `int` | integer |  |
| `status` | `PaymentStatus` | varchar(50) + CHECK (enum) |  |
| `transaction_ref` | `str` | varchar |  |
| `created_at` | `datetime` | timestamp |  |
| `orderId` | `int` | integer | khoá ngoại |
| `paymentMethodId` | `int` | integer | khoá ngoại |

**`Promotion`** — Chương trình; CHECK `ends_at > starts_at`; giảm % trong 1–100.

Quan hệ: Voucher (composition, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `name` | `str` | varchar |  |
| `promo_type` | `PromoType` | varchar(50) + CHECK (enum) |  |
| `discount_type` | `DiscountType` | varchar(50) + CHECK (enum) |  |
| `discount_value` | `int` | integer |  |
| `min_order_value` | `int` | integer |  |
| `starts_at` | `datetime` | timestamp |  |
| `ends_at` | `datetime` | timestamp |  |
| `status` | `PromotionStatus` | varchar(50) + CHECK (enum) |  |

**`PromotionStyle`** — Bảng nối Promotion M:N Style.

Quan hệ: Promotion (aggregation, Unspecified); Style (aggregation, Unspecified).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `promotionId` | `int` | integer | khoá ngoại |
| `styleId` | `int` | integer | khoá ngoại |

**`Voucher`** — Mã giảm giá; `code` UNIQUE; CHECK `0 ≤ used_count ≤ usage_limit`.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `code` | `str` | varchar |  |
| `usage_limit` | `int` | integer |  |
| `used_count` | `int` | integer |  |
| `promotionId` | `int` | integer | khoá ngoại |

#### `model/stat.py` — Lớp thống kê cho báo cáo (không có bảng).

Phụ thuộc: `from abc_fashion.model.catalogue import Style`; `from abc_fashion.model.returns import ReturnReason`

**`ReturnStat`** (kế thừa `Style`) — Một style + số liệu trả (`quantity_sold`, `quantity_returned`, `return_rate`, `main_reason`); do `ReturnStatDAO` tính.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `quantity_sold` | `int` | tính toán |  |
| `quantity_returned` | `int` | tính toán |  |
| `return_rate` | `float` | tính toán |  |
| `main_reason` | `ReturnReason` | tính toán |  |

**`StyleStat`** (kế thừa `Style`) — Một style + số liệu bán (`quantity_sold`, `revenue`, `order_count`); do `StyleStatDAO` tính.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `quantity_sold` | `int` | tính toán |  |
| `revenue` | `int` | tính toán |  |
| `order_count` | `int` | tính toán |  |

#### `model/user.py` — Tài khoản và ba loại người dùng.

| Enum | Giá trị (`.value` lưu trong CSDL) |
|---|---|
| `AccountStatus` | `active`, `suspended` |
| `StaffRole` | `administrator`, `manager`, `merchandiser`, `marketing`, `customer_service`, `warehouse`, `sales` |

**`User`** — Tài khoản đăng nhập. `email` UNIQUE; `password` lưu **hash** (không lưu bản rõ); `status` active/suspended.

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `email` | `str` | varchar |  |
| `password` | `str` | varchar |  |
| `status` | `AccountStatus` | varchar(50) + CHECK (enum) |  |
| `created_at` | `datetime` | timestamp |  |
| `last_login_at` | `datetime` | timestamp |  |

**`Customer`** (kế thừa `User`) — Khách hàng, kế thừa `User`. Bảng có `userId` UNIQUE → 1–1 với User. Chú ý: vì dataclass con khai báo lại `id`, `Customer.id` là id của **dòng khách**, còn id tài khoản nằm ở `userId`. `preferred_colours` trong CSDL là `varchar(255)` (chuỗi phân tách dấu phẩy).

Quan hệ: Notification (composition, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `full_name` | `str` | varchar |  |
| `phone` | `str` | varchar |  |
| `marketing_consent` | `bool` | boolean |  |
| `preferred_colours` | `list[str]` | varchar(255) |  |
| `userId` | `int` | integer | khoá ngoại |

**`StaffMember`** (kế thừa `User`) — Nhân viên, kế thừa `User`; `code` UNIQUE; `role` (StaffRole) quyết định màn hình home.

Quan hệ: AuditLogEntry (composition, 0..*).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `code` | `str` | varchar |  |
| `full_name` | `str` | varchar |  |
| `role` | `StaffRole` | varchar(50) + CHECK (enum) |  |
| `userId` | `int` | integer | khoá ngoại |

**`Supplier`** (kế thừa `User`) — Nhà cung cấp, kế thừa `User` (có thể đăng nhập để xác nhận phiếu nhập).

| Trường | Kiểu Python | Kiểu CSDL | Ghi chú |
|---|---|---|---|
| `id` | `int` | integer | khoá chính, `GENERATED BY DEFAULT AS IDENTITY` |
| `name` | `str` | varchar |  |
| `email` | `str` | varchar |  |
| `phone` | `str` | varchar |  |
| `userId` | `int` | integer | khoá ngoại |


---

## 7. Control layer — DAO và gateway

### 7.1. Lớp gốc `DAO` (`control/dao/dao.py`)

Mã sinh hiện tại:

```python
class DAO:
    def __init__(self):
        self.con = psycopg.connect(DSN)
```

Mỗi đối tượng DAO mở một kết nối riêng, mà một Frm như `CheckoutFrm` tạo 6 DAO → 6 kết nối, và **không thể** gộp nhiều DAO vào một transaction. Thiết kế yêu cầu "mở kết nối một lần và dùng chung cho mọi lớp con". Thân `__init__` nên viết lại như sau (chữ ký không đổi):

```python
# control/dao/dao.py
from __future__ import annotations

import dataclasses
import enum
import os
import typing

import psycopg
from psycopg.rows import dict_row

DSN = os.environ.get("ABC_FASHION_DSN",
                     "dbname=abc_fashion_v2 user=postgres host=localhost port=5432")


class DAO:
    """DAO -- layer abc_fashion.control.dao. Mở kết nối một lần, dùng chung."""

    _shared: psycopg.Connection | None = None

    def __init__(self):
        if DAO._shared is None or DAO._shared.closed:
            # autocommit=True: mỗi câu lệnh lẻ tự commit; nhóm câu lệnh
            # cần nguyên tử thì bọc trong  with self.con.transaction():
            DAO._shared = psycopg.connect(DSN, autocommit=True, row_factory=dict_row)
        self.con = DAO._shared


# ---------- tiện ích dùng chung cho mọi DAO (hàm riêng tư của module) ----------
def _to_entity(cls, row: dict):
    """Tạo entity từ một dòng (dict). Chuyển chuỗi sang Enum theo type hint."""
    hints = typing.get_type_hints(cls)
    kw = {}
    for f in dataclasses.fields(cls):
        if f.name not in row:
            continue
        value = row[f.name]
        for t in (typing.get_args(hints[f.name]) or (hints[f.name],)):
            if isinstance(t, type) and issubclass(t, enum.Enum) and value is not None:
                value = t(value)
                break
        kw[f.name] = value
    return cls(**kw)


def _val(v):
    """Giá trị để truyền vào câu SQL: Enum -> .value."""
    return v.value if isinstance(v, enum.Enum) else v


def _hash_password(plain: str) -> str:
    import hashlib, secrets
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", plain.encode(), bytes.fromhex(salt), 200_000).hex()
    return f"pbkdf2${salt}${h}"


def _check_password(plain: str, stored: str) -> bool:
    import hashlib, hmac
    try:
        _, salt, h = stored.split("$")
    except ValueError:                      # dữ liệu mẫu cũ lưu bản rõ
        return hmac.compare_digest(plain, stored)
    calc = hashlib.pbkdf2_hmac("sha256", plain.encode(), bytes.fromhex(salt), 200_000).hex()
    return hmac.compare_digest(calc, h)
```

Cách dùng trong một DAO con:

```python
from abc_fashion.control.dao.dao import DAO, _to_entity, _val

class AddressDAO(DAO):
    def get_address_by_customer(self, customer: Customer) -> list[Address]:
        rows = self.con.execute(
            'SELECT * FROM "tblAddress" WHERE "customerId" = %s ORDER BY "is_default" DESC, "id"',
            (customer.id,)).fetchall()
        return [_to_entity(Address, r) for r in rows]

    def add_address(self, address: Address, customer: Customer) -> bool:
        with self.con.transaction():
            if address.is_default:
                self.con.execute('UPDATE "tblAddress" SET "is_default" = false WHERE "customerId" = %s',
                                 (customer.id,))
            row = self.con.execute(
                'INSERT INTO "tblAddress"("recipient_name","phone","street","ward","district","city",'
                '"is_default","customerId") VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING "id"',
                (address.recipient_name, address.phone, address.street, address.ward, address.district,
                 address.city, bool(address.is_default), customer.id)).fetchone()
        address.id, address.customerId = row["id"], customer.id
        return True
```

Ghi nhớ:

- **Luôn** dùng tham số `%s`, không bao giờ ghép chuỗi SQL từ dữ liệu người dùng (chống SQL injection).
- `with self.con.transaction():` lồng nhau thì khối trong thành **savepoint** của khối ngoài → một Frm có thể mở transaction rồi gọi nhiều DAO bên trong (vì dùng chung kết nối), mọi thứ cùng commit hoặc cùng rollback.
- Bắt lỗi ràng buộc để trả `False`: `except psycopg.errors.UniqueViolation`, `ForeignKeyViolation`, `CheckViolation`.
- Tìm kiếm không phân biệt hoa thường: `ILIKE %s` với tham số `f"%{key}%"`.

### 7.2. DAO ↔ bảng ↔ component

| Component | DAO | Bảng chính (và bảng phụ được ghi trong cùng transaction) |
|---|---|---|
| Account Data Access | UserDAO, CustomerDAO, StaffMemberDAO, SupplierDAO, AddressDAO, PaymentMethodDAO, SavedSizeDAO, AuditLogEntryDAO | User, Customer (+Cart khi đăng ký), StaffMember, Supplier, Address, PaymentMethod, SavedSize, AuditLogEntry |
| Catalogue Data Access | CategoryDAO, CollectionDAO, StyleDAO, ProductVariantDAO, ProductMediaDAO, MaterialComponentDAO, SizeChartEntryDAO | Category, Collection, Style, ProductVariant, ProductMedia, MaterialComponent, SizeChartEntry |
| Inventory Data Access | StockLocationDAO, StockLevelDAO, StockMovementDAO, RestockRequestDAO | StockLocation, StockLevel, StockMovement, RestockRequest (+RestockItem) |
| Sales Data Access | CartDAO, PromotionDAO, VoucherDAO, OrderDAO, OrderItemDAO, PaymentDAO, ShipmentDAO, NotificationDAO | Cart (+CartItem), Promotion (+PromotionStyle), Voucher, Order (+OrderItem, OrderVoucher, Shipment, ShipmentRecord), Payment, Shipment (+ShipmentEvent), Notification |
| Return & Review Data Access | ReturnRequestDAO, ReturnItemDAO, ReviewDAO, AssistantTurnDAO | ReturnRequest (+ReturnItem, ReturnEvidence), Review, AssistantTurn (+GroundingEvent) |
| Report Data Access | StyleStatDAO, ReturnStatDAO | đọc nhiều bảng, không ghi |
| DB Connection | DAO | — |

### 7.3. Tham chiếu từng DAO

Mỗi mục: file, bảng, rồi từng operation với **chữ ký đầy đủ (đã thêm kiểu trả về)**, việc phải làm, và câu SQL gợi ý.

#### `UserDAO` — `control/dao/user_dao.py`

Bảng: **tblUser**. Tài khoản đăng nhập của mọi loại người dùng (khách, nhân viên, nhà cung cấp).  
Được dùng bởi: EditAccountFrm, LoginFrm, SearchAccountFrm.

- **`def check_login(self, user: User) -> bool`**  
  Kiểm tra e-mail và mật khẩu. `user` đến từ `LoginFrm` chỉ có `email`, `password` (bản rõ). Nếu đúng và `status = active` thì điền `id`, `status`, `created_at`, `last_login_at` vào chính đối tượng `user`, cập nhật `last_login_at = now()` và trả `True`. Sai mật khẩu, không có e-mail hoặc tài khoản `suspended` thì trả `False` (không phân biệt lý do với người dùng để tránh dò tài khoản).  
  *SQL:* `SELECT "id","password","status","created_at","last_login_at" FROM "tblUser" WHERE "email" = %s;  → so khớp hash; UPDATE "tblUser" SET "last_login_at" = now() WHERE "id" = %s`
- **`def search_user(self, key: str, user_type: str, status: str) -> list[User]`**  
  Tìm tài khoản cho quản trị viên (UC20). `key` khớp một phần e-mail hoặc họ tên (họ tên nằm ở bảng con); `user_type` là `customer` / `staff` / `supplier` / `""` (tất cả); `status` là `active` / `suspended` / `""`.  
  *SQL:* `SELECT u.* FROM "tblUser" u LEFT JOIN "tblCustomer" c ON c."userId"=u."id" LEFT JOIN "tblStaffMember" s ON s."userId"=u."id" LEFT JOIN "tblSupplier" p ON p."userId"=u."id" WHERE (u."email" ILIKE %s OR c."full_name" ILIKE %s OR s."full_name" ILIKE %s OR p."name" ILIKE %s) AND (… điều kiện loại …) AND (%s = '' OR u."status" = %s) ORDER BY u."email"`
- **`def update_user_status(self, user: User) -> bool`**  
  Khoá (`suspended`) hoặc mở (`active`) tài khoản theo `user.status` đã được Frm gán sẵn. Trả `True` nếu đúng 1 dòng bị cập nhật.  
  *SQL:* `UPDATE "tblUser" SET "status"=%s WHERE "id"=%s`
- **`def reset_password(self, user: User) -> bool`**  
  Đặt lại mật khẩu: Frm sinh mật khẩu tạm, gán vào `user.password` (bản rõ); DAO băm rồi lưu. Frm hiển thị / gửi mật khẩu tạm cho người dùng.  
  *SQL:* `UPDATE "tblUser" SET "password"=%s WHERE "id"=%s`
- **`def is_email_used(self, email: str) -> bool`**  
  Kiểm tra e-mail đã có tài khoản chưa (UC01 E1) trước khi đăng ký.  
  *SQL:* `SELECT 1 FROM "tblUser" WHERE lower("email") = lower(%s)`

#### `CustomerDAO` — `control/dao/customer_dao.py`

Bảng: **tblCustomer**. Hồ sơ khách hàng (lớp con của tblUser).  
Được dùng bởi: ProfileFrm, RegisterFrm.

- **`def add_customer(self, customer: Customer) -> bool`**  
  Đăng ký khách hàng (UC01). Trong **một transaction**: INSERT `User` (e-mail, mật khẩu đã băm, `status=active`, `created_at=now()`) lấy `id` mới, rồi INSERT `Customer` với `userId` = id đó; tạo luôn giỏ hàng rỗng (`Cart`) để `CartDAO` không phải tạo sau. Điền lại `customer.id`, `customer.userId`. Vi phạm UNIQUE e-mail → rollback, trả `False`.  
  *SQL:* `INSERT INTO "tblUser"("email","password","status","created_at") VALUES (…) RETURNING "id"; INSERT INTO "tblCustomer"("full_name","phone","marketing_consent","preferred_colours","userId") VALUES (…) RETURNING "id"`
- **`def get_customer_by_user(self, user: User) -> Customer | None`**  
  Sau khi đăng nhập, lấy hồ sơ khách theo `user.id`. Trả đối tượng `Customer` đã điền cả các trường của `User` (email, status, …) để các màn hình sau dùng chung. `None` nếu tài khoản không phải khách hàng.  
  *SQL:* `SELECT c.*, u."email", u."status", u."created_at", u."last_login_at" FROM "tblCustomer" c JOIN "tblUser" u ON u."id"=c."userId" WHERE c."userId"=%s`
- **`def update_customer(self, customer: Customer) -> bool`**  
  Lưu họ tên, điện thoại, `marketing_consent`, `preferred_colours` (UC03). Cột `preferred_colours` trong CSDL là `varchar(255)` còn trong model là `list[str]` → nối bằng dấu phẩy khi ghi, tách khi đọc.  
  *SQL:* `UPDATE "tblCustomer" SET "full_name"=%s,"phone"=%s,"marketing_consent"=%s,"preferred_colours"=%s WHERE "id"=%s`

#### `StaffMemberDAO` — `control/dao/staff_member_dao.py`

Bảng: **tblStaffMember**. Hồ sơ nhân viên và vai trò.  
Được dùng bởi: EditAccountFrm.

- **`def get_staff_member_by_user(self, user: User) -> StaffMember | None`**  
  Như `get_customer_by_user` nhưng cho nhân viên; `role` quyết định màn hình home sau đăng nhập.  
  *SQL:* `SELECT s.*, u."email", u."status" FROM "tblStaffMember" s JOIN "tblUser" u ON u."id"=s."userId" WHERE s."userId"=%s`
- **`def get_all_staff_member(self) -> list[StaffMember]`**  
  Danh sách nhân viên cho combobox lọc nhật ký (`AuditLogFrm.cbo_staff`).  
  *SQL:* `SELECT * FROM "tblStaffMember" ORDER BY "full_name"`
- **`def update_role(self, staff: StaffMember) -> bool`**  
  Đổi vai trò của nhân viên (UC20, `EditAccountFrm.on_save_role`). Frm ghi thêm một dòng nhật ký bằng `AuditLogEntryDAO`.  
  *SQL:* `UPDATE "tblStaffMember" SET "role"=%s WHERE "id"=%s`

#### `SupplierDAO` — `control/dao/supplier_dao.py`

Bảng: **tblSupplier**. Nhà cung cấp (cũng đăng nhập được).  
Được dùng bởi: EditRestockRequestFrm, EditStyleFrm.

- **`def get_supplier_by_user(self, user: User) -> Supplier | None`**  
  Lấy nhà cung cấp sau đăng nhập để mở `SupplierHomeFrm`.  
  *SQL:* `SELECT * FROM "tblSupplier" WHERE "userId"=%s`
- **`def get_all_supplier(self) -> list[Supplier]`**  
  Danh sách nhà cung cấp cho combobox ở `EditStyleFrm`, `EditRestockRequestFrm`.  
  *SQL:* `SELECT * FROM "tblSupplier" ORDER BY "name"`

#### `AddressDAO` — `control/dao/address_dao.py`

Bảng: **tblAddress**. Sổ địa chỉ của khách.  
Được dùng bởi: CheckoutFrm, EditAddressFrm, ProfileFrm.

- **`def get_address_by_customer(self, customer: Customer) -> list[Address]`**  
  Các địa chỉ của khách, địa chỉ mặc định lên đầu.  
  *SQL:* `SELECT * FROM "tblAddress" WHERE "customerId"=%s ORDER BY "is_default" DESC, "id"`
- **`def add_address(self, address: Address, customer: Customer) -> bool`**  
  Thêm địa chỉ. Nếu `address.is_default` thì trong cùng transaction bỏ mặc định của các địa chỉ khác của khách. Địa chỉ đầu tiên luôn là mặc định. Điền `address.id`.  
  *SQL:* `UPDATE "tblAddress" SET "is_default"=false WHERE "customerId"=%s; INSERT … RETURNING "id"`
- **`def update_address(self, address: Address) -> bool`**  
  Sửa địa chỉ; quy tắc mặc định như `add_address`.  
  *SQL:* `UPDATE "tblAddress" SET … WHERE "id"=%s`
- **`def delete_address(self, address: Address) -> bool`**  
  Xoá địa chỉ. Không cho xoá địa chỉ mặc định khi khách còn địa chỉ khác (Frm báo chọn địa chỉ mặc định khác trước). Đơn hàng cũ không bị ảnh hưởng vì không có FK tới địa chỉ.  
  *SQL:* `DELETE FROM "tblAddress" WHERE "id"=%s`

#### `PaymentMethodDAO` — `control/dao/payment_method_dao.py`

Bảng: **tblPaymentMethod**. Phương thức thanh toán đã liên kết (chỉ lưu số đã che).  
Được dùng bởi: CheckoutFrm, LinkPaymentMethodFrm, ProfileFrm.

- **`def get_payment_method_by_customer(self, customer: Customer) -> list[PaymentMethod]`**  
  Các phương thức của khách, mặc định lên đầu.  
  *SQL:* `SELECT * FROM "tblPaymentMethod" WHERE "customerId"=%s ORDER BY "is_default" DESC`
- **`def add_payment_method(self, method: PaymentMethod, customer: Customer) -> bool`**  
  Lưu phương thức mà `PaymentGateway.link_method` vừa trả về (`provider`, `method_type`, `masked_number`). **Không bao giờ** lưu số thẻ đầy đủ (NFR04). Quy tắc mặc định như địa chỉ.  
  *SQL:* `INSERT INTO "tblPaymentMethod"(…) VALUES (…) RETURNING "id"`
- **`def delete_payment_method(self, method: PaymentMethod) -> bool`**  
  Gỡ liên kết. Phương thức đã dùng trong `Payment` không xoá được do FK RESTRICT → bắt lỗi `ForeignKeyViolation`, trả `False`, Frm báo cho khách.  
  *SQL:* `DELETE FROM "tblPaymentMethod" WHERE "id"=%s`

#### `SavedSizeDAO` — `control/dao/saved_size_dao.py`

Bảng: **tblSavedSize**. Cỡ đã lưu của khách theo danh mục.  
Được dùng bởi: ProfileFrm.

- **`def get_saved_size_by_customer(self, customer: Customer) -> list[SavedSize]`**  
  Cỡ đã lưu của khách (kèm tên danh mục nếu cần hiển thị).  
  *SQL:* `SELECT * FROM "tblSavedSize" WHERE "customerId"=%s`
- **`def save_saved_size(self, size: SavedSize, customer: Customer) -> bool`**  
  Mỗi khách có tối đa một cỡ cho một danh mục: nếu đã có dòng (`customerId`,`categoryId`) thì UPDATE, ngược lại INSERT.  
  *SQL:* `INSERT … ON CONFLICT ("customerId","categoryId") DO UPDATE SET "size_label"=EXCLUDED."size_label"  (nếu không có UNIQUE thì SELECT trước rồi UPDATE/INSERT)`

#### `AuditLogEntryDAO` — `control/dao/audit_log_entry_dao.py`

Bảng: **tblAuditLogEntry**. Nhật ký thay đổi của nhân viên.  
Được dùng bởi: AuditLogFrm, EditStyleFrm.

- **`def add_audit_log_entry(self, entry: AuditLogEntry, staff: StaffMember) -> bool`**  
  Ghi một dòng nhật ký: `entity` (vd. `Style#12`), `action` (AuditAction), `changes` (mô tả hoặc JSON trước/sau), `created_at=now()`, `staffMemberId=staff.id`. Gọi trong cùng transaction với thay đổi được ghi nếu có thể.  
  *SQL:* `INSERT INTO "tblAuditLogEntry"(…) VALUES (…)`
- **`def search_audit_log_entry(self, start: date, end: date, staff: StaffMember | None, action: str | None) -> list[AuditLogEntry]`**  
  Lọc nhật ký theo khoảng ngày (`start` 00:00 đến hết ngày `end`), nhân viên và hành động; `None` = không lọc.  
  *SQL:* `SELECT * FROM "tblAuditLogEntry" WHERE "created_at" >= %s AND "created_at" < %s + 1 AND (%s IS NULL OR "staffMemberId"=%s) AND (%s IS NULL OR "action"=%s) ORDER BY "created_at" DESC`

#### `CategoryDAO` — `control/dao/category_dao.py`

Bảng: **tblCategory**. Cây danh mục (tự tham chiếu `parentId`).  
Được dùng bởi: BrowseStyleFrm, EditStyleFrm.

- **`def get_all_category(self) -> list[Category]`**  
  Toàn bộ danh mục; Frm dựng cây từ `parentId` (`NULL` = gốc, vd. Women, Men).  
  *SQL:* `SELECT * FROM "tblCategory" ORDER BY "parentId" NULLS FIRST, "name"`
- **`def add_category(self, category: Category) -> bool`**  
  Thêm danh mục con / gốc. Điền `category.id`.  
  *SQL:* `INSERT … RETURNING "id"`
- **`def update_category(self, category: Category) -> bool`**  
  Đổi tên hoặc chuyển nhánh. Phải chặn vòng lặp (không được đặt cha là chính nó hoặc con cháu của nó).  
  *SQL:* `UPDATE "tblCategory" SET "name"=%s,"parentId"=%s WHERE "id"=%s`

#### `CollectionDAO` — `control/dao/collection_dao.py`

Bảng: **tblCollection**. Bộ sưu tập theo mùa.  
Được dùng bởi: EditStyleFrm.

- **`def get_all_collection(self) -> list[Collection]`**  
  Danh sách bộ sưu tập cho combobox (`EditStyleFrm`, `SalesReportFrm`).  
  *SQL:* `SELECT * FROM "tblCollection" ORDER BY "year" DESC, "name"`

#### `StyleDAO` — `control/dao/style_dao.py`

Bảng: **tblStyle**. Mẫu sản phẩm (thiết kế), cha của các biến thể.  
Được dùng bởi: BrowseStyleFrm, EditStyleFrm, ManageStyleFrm, SearchStyleFrm, SelectStyleFrm, StyleDetailFrm.

- **`def search_style(self, key: str) -> list[Style]`**  
  Tìm theo từ khoá trên mã, tên, thương hiệu, mô tả (UC05 tìm bằng chữ). Màn hình khách chỉ hiện `status = active`; màn hình quản trị (`ManageStyleFrm`) hiện tất cả → tham số thêm không có trong thiết kế, nên lọc trạng thái ở Frm hoặc thêm một hàm riêng tư.  
  *SQL:* `SELECT * FROM "tblStyle" WHERE "code" ILIKE %s OR "name" ILIKE %s OR "brand" ILIKE %s OR "description" ILIKE %s ORDER BY "name"`
- **`def search_style_by_ids(self, ids: list[int]) -> list[Style]`**  
  Đọc các style theo danh sách id mà `SearchEngine` trả về (tìm bằng ảnh / giọng nói), **giữ đúng thứ tự xếp hạng** của danh sách.  
  *SQL:* `SELECT * FROM "tblStyle" WHERE "id" = ANY(%s) AND "status"='active'  → sắp lại theo vị trí trong ids`
- **`def get_style_by_category(self, category: Category, size: str, colour: str, fit_type: str, min_price: int, max_price: int, sort: str) -> list[Style]`**  
  Duyệt danh mục có bộ lọc (UC04): `category` gồm cả danh mục con (dùng CTE đệ quy), có ít nhất một biến thể `active` khớp `size`, `colour`, giá trong [`min_price`,`max_price`]; `fit_type` lọc trên style; chuỗi rỗng / 0 = bỏ lọc. `sort`: `price_asc`, `price_desc`, `newest`, `name`.  
  *SQL:* `WITH RECURSIVE cat AS (SELECT "id" FROM "tblCategory" WHERE "id"=%s UNION ALL SELECT c."id" FROM "tblCategory" c JOIN cat ON c."parentId"=cat."id") SELECT DISTINCT s.* , min(v."price") … FROM "tblStyle" s JOIN "tblProductVariant" v ON v."styleId"=s."id" WHERE s."categoryId" IN (SELECT "id" FROM cat) AND … GROUP BY s."id" ORDER BY …`
- **`def get_style_detail(self, style: Style) -> Style`**  
  Đọc đầy đủ một style theo `style.id`. Vì `Style` không có thuộc tính danh sách, hàm trả về style đã đọc lại; các danh sách vật liệu, bảng cỡ, media, biến thể được lấy bằng DAO tương ứng (`MaterialComponentDAO`, `SizeChartEntryDAO`, `ProductMediaDAO`, `ProductVariantDAO`). Có thể gắn tạm thuộc tính động (`style.materials = …`) nếu muốn trả một đối tượng gộp.  
  *SQL:* `SELECT * FROM "tblStyle" WHERE "id"=%s`
- **`def add_style(self, style: Style) -> bool`**  
  Tạo style mới (UC21), thường `status = draft`. Mã `code` là UNIQUE. Điền `style.id`. `EditStyleFrm` gọi tiếp `save_material`, `save_size_chart`, `add_media` và ghi nhật ký trong cùng transaction (xem mục transaction).  
  *SQL:* `INSERT INTO "tblStyle"(…) VALUES (…) RETURNING "id"`
- **`def update_style(self, style: Style) -> bool`**  
  Lưu thay đổi của style. Khi chuyển sang `active` phải kiểm tra đủ thông tin bắt buộc (có ít nhất một vật liệu và một biến thể, theo bội số 1..* của thiết kế).  
  *SQL:* `UPDATE "tblStyle" SET … WHERE "id"=%s`
- **`def deactivate_style(self, style: Style) -> bool`**  
  Ngừng bán: `status = inactive` (không xoá vì có đơn hàng tham chiếu). Có thể đặt các biến thể sang `discontinued` trong cùng transaction.  
  *SQL:* `UPDATE "tblStyle" SET "status"='inactive' WHERE "id"=%s`

#### `ProductVariantDAO` — `control/dao/product_variant_dao.py`

Bảng: **tblProductVariant**. SKU: một cỡ + một màu của style, có giá.  
Được dùng bởi: EditStyleFrm, EditVariantFrm, SelectVariantFrm, StyleDetailFrm.

- **`def get_variant_by_style(self, style: Style) -> list[ProductVariant]`**  
  Các biến thể của style, sắp theo màu rồi cỡ.  
  *SQL:* `SELECT * FROM "tblProductVariant" WHERE "styleId"=%s ORDER BY "colour","size_label"`
- **`def search_variant(self, key: str) -> list[ProductVariant]`**  
  Tìm biến thể theo SKU hoặc tên style (dùng ở `SelectVariantFrm` khi lập phiếu nhập hàng).  
  *SQL:* `SELECT v.* FROM "tblProductVariant" v JOIN "tblStyle" s ON s."id"=v."styleId" WHERE v."sku" ILIKE %s OR s."name" ILIKE %s`
- **`def add_variant(self, variant: ProductVariant, style: Style) -> bool`**  
  Thêm biến thể cho `style` (`styleId = style.id`). UNIQUE (`sku`) và (`styleId`,`size_label`,`colour`) → bắt lỗi trùng. `EditVariantFrm` gọi tiếp `StockLevelDAO.add_stock_level` **trong cùng transaction** vì mỗi biến thể có đúng một bản ghi tồn kho.  
  *SQL:* `INSERT INTO "tblProductVariant"(…) RETURNING "id"`
- **`def update_variant(self, variant: ProductVariant) -> bool`**  
  Sửa giá, trạng thái, cỡ/màu. Giá mới chỉ áp dụng cho đơn sau (đơn cũ đã đóng băng `unit_price`).  
  *SQL:* `UPDATE "tblProductVariant" SET … WHERE "id"=%s`

#### `ProductMediaDAO` — `control/dao/product_media_dao.py`

Bảng: **tblProductMedia**. Ảnh / video của style.  
Được dùng bởi: EditStyleFrm.

- **`def get_media_by_style(self, style: Style) -> list[ProductMedia]`**  
  Media theo thứ tự `sort_order`.  
  *SQL:* `SELECT * FROM "tblProductMedia" WHERE "styleId"=%s ORDER BY "sort_order"`
- **`def add_media(self, media: ProductMedia, style: Style) -> bool`**  
  Lưu đường dẫn (`url`) của file đã tải lên (thư mục media cục bộ hoặc kho ảnh), `media_type`, `colour`, `sort_order` = lớn nhất + 1.  
  *SQL:* `INSERT …`
- **`def delete_media(self, media: ProductMedia) -> bool`**  
  Xoá một media (và file nếu lưu cục bộ).  
  *SQL:* `DELETE FROM "tblProductMedia" WHERE "id"=%s`

#### `MaterialComponentDAO` — `control/dao/material_component_dao.py`

Bảng: **tblMaterialComponent**. Thành phần vải của style.  
Được dùng bởi: EditStyleFrm.

- **`def get_material_by_style(self, style: Style) -> list[MaterialComponent]`**  
  Thành phần vải của style.  
  *SQL:* `SELECT * FROM "tblMaterialComponent" WHERE "styleId"=%s`
- **`def save_material(self, style: Style, materials: list[MaterialComponent]) -> bool`**  
  Thay toàn bộ thành phần của style bằng danh sách mới (DELETE rồi INSERT trong một transaction). Kiểm tra tổng `percent` = 100 và mỗi phần trong 1–100 (CHECK).  
  *SQL:* `DELETE FROM "tblMaterialComponent" WHERE "styleId"=%s; INSERT … (lặp)`

#### `SizeChartEntryDAO` — `control/dao/size_chart_entry_dao.py`

Bảng: **tblSizeChartEntry**. Bảng số đo theo cỡ.  
Được dùng bởi: EditStyleFrm.

- **`def get_size_chart_by_style(self, style: Style) -> list[SizeChartEntry]`**  
  Bảng cỡ; Frm xoay thành bảng (cỡ × số đo) để hiển thị.  
  *SQL:* `SELECT * FROM "tblSizeChartEntry" WHERE "styleId"=%s ORDER BY "size_label","measure"`
- **`def save_size_chart(self, style: Style, entries: list[SizeChartEntry]) -> bool`**  
  Thay toàn bộ bảng cỡ (DELETE + INSERT). `value_cm > 0`.  
  *SQL:* như save_material

#### `StockLocationDAO` — `control/dao/stock_location_dao.py`

Bảng: **tblStockLocation**. Kho hàng.  
Được dùng bởi: EditRestockRequestFrm, EditVariantFrm, StockLevelFrm.

- **`def get_all_stock_location(self) -> list[StockLocation]`**  
  Danh sách kho cho combobox.  
  *SQL:* `SELECT * FROM "tblStockLocation" ORDER BY "name"`

#### `StockLevelDAO` — `control/dao/stock_level_dao.py`

Bảng: **tblStockLevel**. Tồn kho: **mỗi biến thể đúng một dòng** ở một kho. `available = on_hand − reserved` (CHECK), `reserved ≤ on_hand`.  
Được dùng bởi: AdjustStockFrm, CartFrm, EditVariantFrm, InspectReturnFrm, ManageRestockFrm, StockLevelFrm, StyleDetailFrm.

- **`def get_stock_level_by_variant(self, variant: ProductVariant) -> StockLevel | None`**  
  Tồn kho của một biến thể (trang chi tiết sản phẩm hiện "Còn hàng / Sắp hết / Hết hàng" theo `available` và `reorder_point`).  
  *SQL:* `SELECT * FROM "tblStockLevel" WHERE "productVariantId"=%s`
- **`def check_availability(self, items: list[CartItem]) -> list[CartItem]`**  
  UC29: với mỗi dòng giỏ, so `quantity` với `available` của biến thể; trả về **các dòng không đáp ứng được** (danh sách rỗng = hợp lệ). Biến thể `discontinued` hoặc style không `active` cũng tính là không đáp ứng. Chỉ đọc, không khoá.  
  *SQL:* `SELECT "productVariantId","available" FROM "tblStockLevel" WHERE "productVariantId" = ANY(%s)`
- **`def reserve_stock(self, order: Order) -> bool`**  
  UC25/UC29 lúc đặt hàng: khoá các dòng tồn kho của mọi biến thể trong đơn bằng `SELECT … FOR UPDATE` (sắp theo `productVariantId` để tránh deadlock), kiểm tra lại `available ≥ quantity`; nếu đủ thì `reserved += q`, `available -= q`. Thiếu bất kỳ dòng nào → trả `False` (người gọi rollback). Hàm **không tự commit**: được gọi bên trong transaction của `OrderDAO.add_order` (dùng chung kết nối). Hai khách mua món cuối cùng cùng lúc: người thứ hai chờ khoá, đọc lại thấy hết hàng → `False` (NFR10).  
  *SQL:* `SELECT * FROM "tblStockLevel" WHERE "productVariantId" = ANY(%s) ORDER BY "productVariantId" FOR UPDATE; UPDATE "tblStockLevel" SET "reserved"="reserved"+%s, "available"="available"-%s WHERE "id"=%s`
- **`def add_stock_level(self, level: StockLevel, variant: ProductVariant, location: StockLocation) -> bool`**  
  Tạo bản ghi tồn kho đầu tiên cho biến thể mới ở kho `location` (`on_hand=0`, `reserved=0`, `available=0`, `reorder_point` do người dùng nhập). UNIQUE (`productVariantId`).  
  *SQL:* `INSERT INTO "tblStockLevel"(…) VALUES (…)`
- **`def search_stock_level(self, location: StockLocation | None, key: str, below_reorder_point: bool) -> list[StockLevel]`**  
  Màn hình tồn kho (UC17): lọc theo kho (`None` = mọi kho), từ khoá SKU/tên style, và `below_reorder_point` (`available ≤ reorder_point`). Nên JOIN biến thể + style để Frm hiển thị SKU, tên, màu, cỡ (gắn tạm vào đối tượng hoặc trả kèm).  
  *SQL:* `SELECT l.*, v."sku", s."name" FROM "tblStockLevel" l JOIN "tblProductVariant" v ON v."id"=l."productVariantId" JOIN "tblStyle" s ON s."id"=v."styleId" WHERE (%s IS NULL OR l."stockLocationId"=%s) AND (v."sku" ILIKE %s OR s."name" ILIKE %s) AND (NOT %s OR l."available" <= l."reorder_point")`
- **`def adjust_stock(self, level: StockLevel, movement: StockMovement) -> bool`**  
  Điều chỉnh tồn (UC17) và cũng là hàm chung cho mọi thay đổi tồn: trong **một transaction** khoá dòng `level`, cộng `movement.quantity_change` vào `on_hand` (và `available`), kiểm tra không âm, rồi INSERT `movement` (`reason`: adjustment / return / restock / sale; `reference`; `note`; `staffMemberId`; `created_at=now()`). Lý do bắt buộc với điều chỉnh tay (FR23). Mọi thay đổi tồn đều phải có dòng sổ kho tương ứng (NFR11).  
  *SQL:* `SELECT … FOR UPDATE; UPDATE "tblStockLevel" SET "on_hand"="on_hand"+%s,"available"="available"+%s WHERE "id"=%s; INSERT INTO "tblStockMovement"(…)`

#### `StockMovementDAO` — `control/dao/stock_movement_dao.py`

Bảng: **tblStockMovement**. Sổ kho: mỗi thay đổi tồn là một dòng.  
Được dùng bởi: InspectReturnFrm, ManageOrderFrm, ManageRestockFrm, StockMovementFrm.

- **`def add_stock_movement(self, movement: StockMovement) -> bool`**  
  Ghi một dòng sổ kho mà **không** đổi tồn (dùng khi tồn đã được đổi bởi hàm khác trong cùng transaction, ví dụ ghi `sale` khi xác nhận đơn, hoặc trả lại khi huỷ). Nếu muốn đổi tồn + ghi sổ thì dùng `StockLevelDAO.adjust_stock`.  
  *SQL:* `INSERT INTO "tblStockMovement"(…)`
- **`def get_movement_by_variant(self, variant: ProductVariant, start: date, end: date, reason: str | None) -> list[StockMovement]`**  
  Lịch sử tồn của biến thể trong khoảng ngày, lọc theo lý do (`None` = tất cả), mới nhất trước.  
  *SQL:* `SELECT * FROM "tblStockMovement" WHERE "productVariantId"=%s AND "created_at" >= %s AND "created_at" < %s + 1 AND (%s IS NULL OR "reason"=%s) ORDER BY "created_at" DESC`

#### `RestockRequestDAO` — `control/dao/restock_request_dao.py`

Bảng: **tblRestockRequest**. Phiếu yêu cầu nhập hàng gửi nhà cung cấp (kèm `tblRestockItem`).  
Được dùng bởi: ConfirmRestockFrm, EditRestockRequestFrm, ManageRestockFrm, SupplierHomeFrm.

- **`def search_restock_request(self, status: str | None, supplier: Supplier | None) -> list[RestockRequest]`**  
  Danh sách phiếu theo trạng thái và nhà cung cấp. `SupplierHomeFrm` gọi với `supplier` = chính họ và chỉ thấy phiếu từ `sent` trở đi.  
  *SQL:* `SELECT * FROM "tblRestockRequest" WHERE (%s IS NULL OR "status"=%s) AND (%s IS NULL OR "supplierId"=%s) ORDER BY "created_at" DESC`
- **`def get_restock_request_detail(self, request: RestockRequest) -> RestockRequest`**  
  Đọc phiếu và các dòng `RestockItem` (gắn vào `request.items`, kèm SKU để hiển thị).  
  *SQL:* `SELECT * FROM "tblRestockRequest" WHERE "id"=%s; SELECT i.*, v."sku" FROM "tblRestockItem" i JOIN "tblProductVariant" v … WHERE i."restockRequestId"=%s`
- **`def add_restock_request(self, request: RestockRequest, staff: StaffMember) -> bool`**  
  Tạo phiếu (`status = draft` hoặc `sent`), sinh `request_no` (vd. `RST-YYMMDD-NNN`), `staffMemberId = staff.id`, INSERT các dòng `items` (`quantity > 0`) trong một transaction.  
  *SQL:* `INSERT INTO "tblRestockRequest"(…) RETURNING "id"; INSERT INTO "tblRestockItem"(…)`
- **`def update_restock_request(self, request: RestockRequest) -> bool`**  
  Lưu thay đổi phiếu: sửa nháp (thay dòng), gửi (`draft→sent`), nhà cung cấp xác nhận (`sent→confirmed`, `confirm_at`, `expected_date`, `supplier_note`) hoặc từ chối (`sent→cancelled`, `supplier_note` bắt buộc — UC17 E1). Kiểm tra chuyển trạng thái hợp lệ.  
  *SQL:* `UPDATE "tblRestockRequest" SET … WHERE "id"=%s AND "status"=%s  (kèm trạng thái cũ để chống ghi đè đồng thời)`
- **`def receive_restock_request(self, request: RestockRequest, staff: StaffMember) -> bool`**  
  Nhận hàng: chỉ với phiếu `confirmed`. Trong **một transaction**: với mỗi dòng, khoá `StockLevel` của biến thể, `on_hand += quantity`, `available += quantity`, INSERT `StockMovement` (`reason = restock`, `reference = request_no`, `staffMemberId = staff.id`); cuối cùng `status = received`. Lưu ý mỗi biến thể chỉ có một kho: nếu kho của biến thể khác kho nhận của phiếu thì báo lỗi (hoặc chuyển kho theo quy định).  
  *SQL:* xem adjust_stock, lặp cho từng item; UPDATE "tblRestockRequest" SET "status"='received'

#### `CartDAO` — `control/dao/cart_dao.py`

Bảng: **tblCart**. Giỏ hàng lưu trên server, một giỏ cho mỗi khách (NFR12).  
Được dùng bởi: CartFrm, StyleDetailFrm.

- **`def get_cart_by_customer(self, customer: Customer) -> Cart`**  
  Lấy giỏ của khách; chưa có thì tạo. Đọc kèm các dòng `CartItem` JOIN biến thể + style (gắn vào `cart.items`; vì `CartItem` kế thừa `ProductVariant` nên các trường `sku`, `size_label`, `colour`, `price` của biến thể điền thẳng vào đối tượng dòng giỏ; tên style gắn động `item.style_name`). Tính lại `subtotal = Σ quantity × price`.  
  *SQL:* `SELECT * FROM "tblCart" WHERE "customerId"=%s; SELECT i."id", i."quantity", i."added_at", i."cartId", i."productVariantId", v."sku", v."size_label", v."colour", v."price", v."status", v."styleId", s."name" AS style_name FROM "tblCartItem" i JOIN "tblProductVariant" v ON v."id"=i."productVariantId" JOIN "tblStyle" s ON s."id"=v."styleId" WHERE i."cartId"=%s`
- **`def add_cart_item(self, cart: Cart, item: CartItem) -> bool`**  
  Thêm vào giỏ (UC07): nếu biến thể đã có trong giỏ thì cộng dồn số lượng. Kiểm tra sơ bộ `available` (kiểm tra ràng buộc thực sự ở checkout). Cập nhật `Cart.updated_at`, `subtotal`.  
  *SQL:* `SELECT "id" FROM "tblCartItem" WHERE "cartId"=%s AND "productVariantId"=%s; UPDATE … SET "quantity"="quantity"+%s | INSERT …`
- **`def update_cart_item(self, item: CartItem) -> bool`**  
  Đổi số lượng một dòng (`quantity > 0`; số 0 → gọi `delete_cart_item`). Cập nhật tổng giỏ.  
  *SQL:* `UPDATE "tblCartItem" SET "quantity"=%s WHERE "id"=%s`
- **`def delete_cart_item(self, item: CartItem) -> bool`**  
  Xoá một dòng giỏ.  
  *SQL:* `DELETE FROM "tblCartItem" WHERE "id"=%s`
- **`def clear_cart(self, cart: Cart) -> bool`**  
  Xoá hết dòng giỏ (gọi trong transaction đặt hàng sau khi tạo đơn).  
  *SQL:* `DELETE FROM "tblCartItem" WHERE "cartId"=%s; UPDATE "tblCart" SET "subtotal"=0`

#### `PromotionDAO` — `control/dao/promotion_dao.py`

Bảng: **tblPromotion**. Chương trình khuyến mãi (kèm `tblPromotionStyle`, `tblVoucher`).  
Được dùng bởi: EditPromotionFrm, ManagePromotionFrm, StyleDetailFrm.

- **`def get_active_promotion_by_style(self, style: Style) -> Promotion | None`**  
  Khuyến mãi đang chạy áp dụng cho style (status `active`, now() trong [`starts_at`,`ends_at`)), để trang sản phẩm hiện nhãn và giá sau giảm. Nhiều chương trình → lấy chương trình giảm nhiều nhất.  
  *SQL:* `SELECT p.* FROM "tblPromotion" p JOIN "tblPromotionStyle" ps ON ps."promotionId"=p."id" WHERE ps."styleId"=%s AND p."status"='active' AND now() BETWEEN p."starts_at" AND p."ends_at"`
- **`def search_promotion(self, key: str, status: str | None) -> list[Promotion]`**  
  Danh sách chương trình theo tên và trạng thái cho `ManagePromotionFrm`.  
  *SQL:* `SELECT * FROM "tblPromotion" WHERE "name" ILIKE %s AND (%s IS NULL OR "status"=%s) ORDER BY "starts_at" DESC`
- **`def get_promotion_detail(self, promotion: Promotion) -> Promotion`**  
  Đọc chương trình kèm các style tham gia (`promotion.styles`) và voucher (`promotion.vouchers`).  
  *SQL:* `SELECT …; SELECT s.* FROM "tblStyle" s JOIN "tblPromotionStyle" ps …; SELECT * FROM "tblVoucher" WHERE "promotionId"=%s`
- **`def add_promotion(self, promotion: Promotion) -> bool`**  
  Tạo chương trình và các dòng `PromotionStyle` trong một transaction. Kiểm tra `ends_at > starts_at`, phần trăm 1–100 (CHECK). Voucher thêm bằng `VoucherDAO.add_voucher`.  
  *SQL:* `INSERT INTO "tblPromotion" … RETURNING "id"; INSERT INTO "tblPromotionStyle"("promotionId","styleId") …`
- **`def update_promotion(self, promotion: Promotion) -> bool`**  
  Lưu chương trình; thay danh sách style (DELETE + INSERT `PromotionStyle`). Kết thúc sớm (`ManagePromotionFrm.on_end`) = `status = ended`.  
  *SQL:* `UPDATE …; DELETE FROM "tblPromotionStyle" WHERE "promotionId"=%s; INSERT …`

#### `VoucherDAO` — `control/dao/voucher_dao.py`

Bảng: **tblVoucher**. Mã giảm giá của một chương trình.  
Được dùng bởi: CheckoutFrm, EditPromotionFrm.

- **`def get_voucher_by_code(self, code: str) -> Voucher | None`**  
  UC26: tìm mã (không phân biệt hoa thường) kèm chương trình của nó (gắn `voucher.promotion`). Frm kiểm tra: chương trình `active`, trong thời gian, `used_count < usage_limit`, `subtotal ≥ min_order_value`, giỏ có style thuộc chương trình.  
  *SQL:* `SELECT v.*, p.* FROM "tblVoucher" v JOIN "tblPromotion" p ON p."id"=v."promotionId" WHERE upper(v."code")=upper(%s)`
- **`def add_voucher(self, voucher: Voucher, promotion: Promotion) -> bool`**  
  Thêm mã cho chương trình (`used_count = 0`). Mã là UNIQUE.  
  *SQL:* `INSERT INTO "tblVoucher"("code","usage_limit","used_count","promotionId") VALUES (%s,%s,0,%s)`
- **`def get_voucher_by_promotion(self, promotion: Promotion) -> list[Voucher]`**  
  Các mã của một chương trình (bảng voucher trong `EditPromotionFrm`).  
  *SQL:* `SELECT * FROM "tblVoucher" WHERE "promotionId"=%s`

#### `OrderDAO` — `control/dao/order_dao.py`

Bảng: **tblOrder**. Đơn hàng (kèm `tblOrderItem`, `tblOrderVoucher`, và tạo `tblShipment`).  
Được dùng bởi: CancelRequestFrm, CheckoutFrm, ManageOrderFrm, OrderDetailFrm, OrderListFrm, SearchOrderFrm.

- **`def add_order(self, order: Order, customer: Customer) -> bool`**  
  Hàm quan trọng nhất của UC08. `order` đã được `CheckoutFrm` dựng sẵn: các dòng `order.items` (OrderItem với `unit_price` = giá hiện tại, `discount` phần giảm phân bổ, `line_total`), `subtotal`, `discount`, `shipping_fee`, `grand_total`, `delivery_service`, `note`, và `order.vouchers`. Trong **một transaction**: (1) sinh `order_no` (`ORD-YYMMDD…`), INSERT `Order` (`status = pending_payment`, `placed_at = now()`, `customerId = customer.id`); (2) INSERT từng `OrderItem`; (3) với mỗi voucher: khoá dòng `Voucher` (`FOR UPDATE`), kiểm tra `used_count < usage_limit`, tăng `used_count`, INSERT `OrderVoucher`; (4) gọi `StockLevelDAO.reserve_stock(order)` — `False` thì rollback toàn bộ và trả `False`; (5) nhóm các dòng theo kho (`StockLevel.stockLocationId` của từng biến thể) và INSERT một `Shipment` `outbound`/`requested` cho mỗi kho cùng các `ShipmentRecord` (UC28 tách kiện); (6) `CartDAO.clear_cart`. Bất kỳ lỗi nào → rollback, không còn đơn dở dang (NFR07). Điền `order.id`, `order.order_no`.  
  *SQL:* with self.con.transaction(): … (xem mã mẫu mục 9.3)
- **`def get_order_by_customer(self, customer: Customer, status: str | None) -> list[Order]`**  
  Đơn của một khách (UC09), lọc trạng thái (`None` = tất cả), mới nhất trước. **Luôn lọc theo `customer.id`** để khách không xem được đơn người khác (NFR03).  
  *SQL:* `SELECT * FROM "tblOrder" WHERE "customerId"=%s AND (%s IS NULL OR "status"=%s) ORDER BY "placed_at" DESC`
- **`def get_order_detail(self, order: Order) -> Order`**  
  Đọc đầy đủ đơn: các dòng (kèm SKU, tên style, màu, cỡ), voucher, thanh toán (`PaymentDAO`), kiện hàng (`ShipmentDAO`), yêu cầu trả (nếu có). Gắn vào `order.items`, `order.payments`, `order.shipments`.  
  *SQL:* nhiều SELECT theo "orderId"
- **`def update_order_status(self, order: Order) -> bool`**  
  Đổi `order.status` (giá trị mới đã gán ở Frm). Kiểm tra chuyển trạng thái hợp lệ (mục 10.1) bằng `UPDATE … WHERE "status" = <trạng thái cũ>`. Tác động phụ trong cùng transaction: `pending_payment→confirmed` (thanh toán xong hoặc COD) — chốt bán: với mỗi dòng `on_hand -= q`, `reserved -= q` và ghi `StockMovement` `sale` (UC25, BR2: chỉ trừ kho sau thanh toán); `→delivered` — đặt `delivered_at` cho kiện; `delivered→completed` khi khách xác nhận đã nhận (UC12).  
  *SQL:* `UPDATE "tblOrder" SET "status"=%s WHERE "id"=%s AND "status"=%s`
- **`def cancel_order(self, order: Order) -> bool`**  
  Huỷ đơn (UC10/UC23) với `order.cancel_reason` bắt buộc. Chỉ cho phép khi chưa giao vận chuyển (`pending_payment`, `confirmed`, `processing`). Trong cùng transaction: nếu còn `pending_payment` → nhả giữ hàng (`reserved -= q`, `available += q`); nếu đã `confirmed`/`processing` (đã trừ `on_hand`) → cộng lại `on_hand`/`available` và ghi `StockMovement` (`reason = adjustment`, `reference = order_no`, note "order cancelled"); trả lại lượt voucher (`used_count -= 1`); kiện `requested` chuyển `failed`. Hoàn tiền (nếu đã trả) do Frm gọi `PaymentGateway.refund` + `PaymentDAO.add_payment(kind=refund)`.  
  *SQL:* `UPDATE "tblOrder" SET "status"='cancelled',"cancel_reason"=%s WHERE "id"=%s AND "status" IN (…)`
- **`def search_order(self, key: str, status: str | None, start: date, end: date) -> list[Order]`**  
  Tìm đơn cho quản lý (UC22): từ khoá trên `order_no`, tên / e-mail / điện thoại khách; trạng thái; khoảng ngày đặt.  
  *SQL:* `SELECT o.* FROM "tblOrder" o JOIN "tblCustomer" c ON c."id"=o."customerId" JOIN "tblUser" u ON u."id"=c."userId" WHERE (o."order_no" ILIKE %s OR c."full_name" ILIKE %s OR u."email" ILIKE %s OR c."phone" ILIKE %s) AND … AND o."placed_at"::date BETWEEN %s AND %s`

#### `OrderItemDAO` — `control/dao/order_item_dao.py`

Bảng: **tblOrderItem**. Dòng đơn — dùng cho báo cáo chi tiết.  
Được dùng bởi: SalesDetailFrm.

- **`def get_order_item_by_style(self, style: Style, start: date, end: date) -> list[OrderItem]`**  
  Các dòng đơn của mọi biến thể thuộc style trong khoảng ngày (đơn không bị huỷ), cho `SalesDetailFrm`.  
  *SQL:* `SELECT i.*, o."order_no", o."placed_at" FROM "tblOrderItem" i JOIN "tblOrder" o ON o."id"=i."orderId" JOIN "tblProductVariant" v ON v."id"=i."productVariantId" WHERE v."styleId"=%s AND o."status" <> 'cancelled' AND o."placed_at"::date BETWEEN %s AND %s`

#### `PaymentDAO` — `control/dao/payment_dao.py`

Bảng: **tblPayment**. Các lần thu (`charge`) và hoàn (`refund`) của đơn.  
Được dùng bởi: CheckoutFrm, ConfirmOrderFrm, ManageOrderFrm, ProcessReturnFrm.

- **`def add_payment(self, payment: Payment, order: Order) -> bool`**  
  Ghi kết quả `PaymentGateway.charge/refund`: `kind`, `method`, `amount`, `status` (pending/succeeded/failed), `transaction_ref`, `created_at`, `orderId = order.id`, `paymentMethodId`. Lần thanh toán lại sau khi thất bại là một dòng mới.  
  *SQL:* `INSERT INTO "tblPayment"(…) RETURNING "id"`
- **`def update_payment(self, payment: Payment) -> bool`**  
  Cập nhật trạng thái một lần thanh toán `pending` khi cổng thanh toán báo kết quả sau (callback). Gọi lặp lại không làm thay đổi gì (idempotent) — `WHERE "status" = 'pending'`.  
  *SQL:* `UPDATE "tblPayment" SET "status"=%s,"transaction_ref"=%s WHERE "id"=%s AND "status"='pending'`
- **`def get_payment_by_order(self, order: Order) -> list[Payment]`**  
  Lịch sử thanh toán của đơn; số tiền đã thu ròng = Σ charge succeeded − Σ refund succeeded (dùng để giới hạn hoàn tiền).  
  *SQL:* `SELECT * FROM "tblPayment" WHERE "orderId"=%s ORDER BY "created_at"`

#### `ShipmentDAO` — `control/dao/shipment_dao.py`

Bảng: **tblShipment**. Kiện hàng (giao đi `outbound`, lấy về `return`) kèm `tblShipmentRecord`, `tblShipmentEvent`.  
Được dùng bởi: ManageOrderFrm, ProcessReturnFrm, TrackShipmentFrm.

- **`def get_shipment_by_order(self, order: Order) -> list[Shipment]`**  
  Các kiện của đơn (kèm các dòng `ShipmentRecord` nếu cần).  
  *SQL:* `SELECT * FROM "tblShipment" WHERE "orderId"=%s ORDER BY "id"`
- **`def get_shipment_event(self, shipment: Shipment) -> list[ShipmentEvent]`**  
  Lịch sử theo dõi của một kiện (UC11), theo thời gian.  
  *SQL:* `SELECT * FROM "tblShipmentEvent" WHERE "shipmentId"=%s ORDER BY "occurred_at"`
- **`def update_shipment(self, shipment: Shipment) -> bool`**  
  Lưu `carrier`, `tracking_no` (sau `ShippingGateway.create_shipment`), `status`, `delivered_at`. Sau khi đổi trạng thái kiện, Frm tính lại trạng thái đơn: một phần kiện đã đi → `partially_shipped`; tất cả đi → `shipped`; tất cả giao xong → `delivered`.  
  *SQL:* `UPDATE "tblShipment" SET … WHERE "id"=%s`
- **`def add_shipment_event(self, event: ShipmentEvent, shipment: Shipment) -> bool`**  
  Thêm sự kiện theo dõi (từ `ShippingGateway.get_tracking` hoặc nhập tay) và cập nhật `Shipment.status` theo sự kiện mới nhất, trong một transaction. Bỏ qua sự kiện trùng (`status`,`occurred_at`).  
  *SQL:* `INSERT INTO "tblShipmentEvent"(…); UPDATE "tblShipment" SET "status"=%s`
- **`def add_shipment(self, shipment: Shipment, order: Order) -> bool`**  
  Tạo kiện mới cho `order`: dùng cho kiện lấy hàng trả (`direction = return`, `returnRequestId` bắt buộc — CHECK) và kiện giao hàng đổi (`outbound`, `returnRequestId` = yêu cầu đổi). INSERT kèm `ShipmentRecord` cho các dòng hàng. (Kiện giao đơn thường được `add_order` tạo.)  
  *SQL:* `INSERT INTO "tblShipment"(…) RETURNING "id"; INSERT INTO "tblShipmentRecord"(…)`

#### `ReturnRequestDAO` — `control/dao/return_request_dao.py`

Bảng: **tblReturnRequest**. Yêu cầu trả / đổi hàng (kèm `tblReturnItem`, `tblReturnEvidence`). Mỗi đơn tối đa một yêu cầu (UNIQUE `orderId`).  
Được dùng bởi: InspectReturnFrm, ProcessReturnFrm, ReturnRequestFrm, SearchReturnRequestFrm.

- **`def add_return_request(self, request: ReturnRequest, order: Order) -> bool`**  
  UC14: trong một transaction INSERT yêu cầu (`return_no` `RET-…`, `status = requested`, `requested_at = now()`, `orderId`), các dòng `items` (mỗi dòng trỏ `orderItemId`, `quantity ≤` số đã mua, `inspection_result = pending`) và các `evidence`. Kiểm tra: đơn `delivered`/`completed`, trong hạn trả (30 ngày từ khi giao — giả định), chưa có yêu cầu (UNIQUE → bắt lỗi, báo "đơn đã có yêu cầu trả").  
  *SQL:* `INSERT INTO "tblReturnRequest" … RETURNING "id"; INSERT INTO "tblReturnItem" …; INSERT INTO "tblReturnEvidence" …`
- **`def get_return_request_by_order(self, order: Order) -> ReturnRequest | None`**  
  Yêu cầu của đơn (để `OrderDetailFrm` ẩn nút "Trả hàng" khi đã có).  
  *SQL:* `SELECT * FROM "tblReturnRequest" WHERE "orderId"=%s`
- **`def search_return_request(self, key: str, status: str | None) -> list[ReturnRequest]`**  
  Danh sách cho CSKH / kho: từ khoá trên `return_no`, `order_no`, tên khách; trạng thái. Nhân viên kho chỉ cần các yêu cầu `in_transit`.  
  *SQL:* `SELECT r.* FROM "tblReturnRequest" r JOIN "tblOrder" o ON o."id"=r."orderId" … WHERE …`
- **`def get_return_request_detail(self, request: ReturnRequest) -> ReturnRequest`**  
  Đọc đầy đủ: các dòng trả (kèm SKU, đơn giá, giảm giá của dòng đơn gốc), bằng chứng, các kiện liên quan.  
  *SQL:* nhiều SELECT theo "returnRequestId"
- **`def update_return_request(self, request: ReturnRequest, staff: StaffMember) -> bool`**  
  Lưu quyết định / tiến trình: `status` mới (mục 10.2), `decision_note`, `decided_at = now()` khi duyệt/từ chối, `staffMemberId = staff.id`. Kiểm tra chuyển trạng thái hợp lệ.  
  *SQL:* `UPDATE "tblReturnRequest" SET "status"=%s,"decision_note"=%s,"decided_at"=…,"staffMemberId"=%s WHERE "id"=%s AND "status"=%s`
- **`def update_return_item(self, item: ReturnItem) -> bool`**  
  Lưu kết quả kiểm tra của một dòng (`inspection_result` passed/failed, `inspection_note`).  
  *SQL:* `UPDATE "tblReturnItem" SET "inspection_result"=%s,"inspection_note"=%s WHERE "id"=%s`

#### `ReturnItemDAO` — `control/dao/return_item_dao.py`

Bảng: **tblReturnItem**. Dòng trả — dùng cho báo cáo chi tiết.  
Được dùng bởi: ReturnDetailFrm.

- **`def get_return_item_by_style(self, style: Style, start: date, end: date) -> list[ReturnItem]`**  
  Các dòng trả của style trong khoảng ngày (theo `requested_at`), yêu cầu không bị từ chối, cho `ReturnDetailFrm`.  
  *SQL:* `SELECT ri.*, r."reason_code", r."return_no" FROM "tblReturnItem" ri JOIN "tblReturnRequest" r … JOIN "tblOrderItem" oi ON oi."id"=ri."orderItemId" JOIN "tblProductVariant" v ON v."id"=oi."productVariantId" WHERE v."styleId"=%s AND r."status" <> 'rejected' AND …`

#### `ReviewDAO` — `control/dao/review_dao.py`

Bảng: **tblReview**. Đánh giá của một dòng đơn đã mua (UNIQUE `orderItemId`).  
Được dùng bởi: ManageReviewFrm, ReviewFrm, StyleDetailFrm.

- **`def get_approved_review_by_style(self, style: Style) -> list[Review]`**  
  Đánh giá `approved` của mọi biến thể thuộc style, mới nhất trước (trang chi tiết, và đầu vào cho `AssistantEngine.summarise_reviews` — UC33).  
  *SQL:* `SELECT r.* FROM "tblReview" r JOIN "tblOrderItem" oi ON oi."id"=r."orderItemId" JOIN "tblProductVariant" v ON v."id"=oi."productVariantId" WHERE v."styleId"=%s AND r."status"='approved' ORDER BY r."created_at" DESC`
- **`def add_review(self, review: Review, order_item: OrderItem) -> bool`**  
  UC13: lưu đánh giá cho `order_item` (`rating` 1–5, `body`, `size_purchased`, `fit_vote`, `status` do kiểm duyệt tự động quyết định: `approved` hoặc `pending` để người duyệt — UC34). Chỉ cho đơn đã giao. **Lưu ý CSDL hiện tại** còn cột `verified_purchase`/`origin` với CHECK → xem mục 13.  
  *SQL:* `INSERT INTO "tblReview"(…) VALUES (…)`
- **`def is_reviewed(self, order_item: OrderItem) -> bool`**  
  Dòng đơn đã được đánh giá chưa (ẩn nút "Đánh giá").  
  *SQL:* `SELECT 1 FROM "tblReview" WHERE "orderItemId"=%s`
- **`def search_review(self, key: str, status: str | None, rating: int | None) -> list[Review]`**  
  Danh sách cho người duyệt (UC19): từ khoá trên nội dung / tên style, trạng thái, số sao.  
  *SQL:* `SELECT r.* … WHERE r."body" ILIKE %s AND (%s IS NULL OR r."status"=%s) AND (%s IS NULL OR r."rating"=%s)`
- **`def update_review(self, review: Review, staff: StaffMember) -> bool`**  
  Duyệt / từ chối: `status`, `moderation_note`, `staffMemberId = staff.id`.  
  *SQL:* `UPDATE "tblReview" SET "status"=%s,"moderation_note"=%s,"staffMemberId"=%s WHERE "id"=%s`

#### `NotificationDAO` — `control/dao/notification_dao.py`

Bảng: **tblNotification**. Thông báo gửi khách (e-mail / SMS / app).  
Được dùng bởi: CheckoutFrm, ManageOrderFrm, ProcessReturnFrm.

- **`def add_notification(self, notification: Notification, customer: Customer) -> bool`**  
  Ghi thông báo: `channel`, `event_type`, `message`, `status` (`sent`/`failed` theo kết quả `NotificationGateway.send`, hoặc `queued` nếu gửi sau), `sent_at`, `customerId = customer.id`.  
  *SQL:* `INSERT INTO "tblNotification"(…)`

#### `AssistantTurnDAO` — `control/dao/assistant_turn_dao.py`

Bảng: **tblAssistantTurn**. Nhật ký trợ lý AI (kèm `tblGroundingEvent`).  
Được dùng bởi: AssistantFrm.

- **`def add_assistant_turn(self, turn: AssistantTurn, customer: Customer | None, style: Style) -> bool`**  
  Lưu một lượt hỏi–đáp: `question` (đã che dữ liệu cá nhân — NFR16), `answer`, `mode` (model/basic), `model_name`, `latency_ms`, `created_at`, `customerId` (NULL nếu khách vãng lai), `styleId`; và các `turn.grounding_events` (câu trả lời bị loại bỏ vì sai giá, tồn kho, …) trong cùng transaction.  
  *SQL:* `INSERT INTO "tblAssistantTurn" … RETURNING "id"; INSERT INTO "tblGroundingEvent"(…)`
- **`def get_turn_by_customer(self, customer: Customer, style: Style) -> list[AssistantTurn]`**  
  Lịch sử hỏi của khách về một style (hiển thị lại hội thoại khi mở `AssistantFrm`).  
  *SQL:* `SELECT * FROM "tblAssistantTurn" WHERE "customerId"=%s AND "styleId"=%s ORDER BY "created_at"`

#### `StyleStatDAO` — `control/dao/style_stat_dao.py`

Bảng: **— (nhiều bảng)**. Số liệu bán hàng theo style cho báo cáo.  
Được dùng bởi: SalesReportFrm.

- **`def get_style_stat(self, start: date, end: date, category: Category | None, collection: Collection | None) -> list[StyleStat]`**  
  UC16/UC24 báo cáo doanh số: mỗi style một dòng `StyleStat` (các trường của style + `quantity_sold = Σ quantity`, `revenue = Σ line_total`, `order_count = COUNT(DISTINCT order)`), chỉ đơn không huỷ trong khoảng ngày, lọc danh mục / bộ sưu tập (`None` = tất cả), sắp theo doanh thu giảm dần.  
  *SQL:* `SELECT s.*, SUM(i."quantity") AS quantity_sold, SUM(i."line_total") AS revenue, COUNT(DISTINCT o."id") AS order_count FROM "tblOrderItem" i JOIN "tblOrder" o ON o."id"=i."orderId" JOIN "tblProductVariant" v ON v."id"=i."productVariantId" JOIN "tblStyle" s ON s."id"=v."styleId" WHERE o."status" <> 'cancelled' AND o."placed_at"::date BETWEEN %s AND %s AND (%s IS NULL OR s."categoryId"=%s) AND (%s IS NULL OR s."collectionId"=%s) GROUP BY s."id" ORDER BY revenue DESC`

#### `ReturnStatDAO` — `control/dao/return_stat_dao.py`

Bảng: **— (nhiều bảng)**. Số liệu trả hàng theo style cho báo cáo.  
Được dùng bởi: ReturnReportFrm.

- **`def get_return_stat(self, start: date, end: date, reason: str | None) -> list[ReturnStat]`**  
  Báo cáo trả hàng: mỗi style `quantity_sold`, `quantity_returned` (Σ dòng trả của yêu cầu không bị từ chối), `return_rate = returned / sold`, `main_reason` = lý do xuất hiện nhiều nhất; lọc theo lý do (`None` = tất cả). Sắp theo tỉ lệ trả giảm dần.  
  *SQL:* hai truy vấn con (sold, returned) JOIN theo styleId; main_reason bằng mode() WITHIN GROUP (ORDER BY r."reason_code")


### 7.4. Gateway (`control/gateway/`)

Gateway là **ranh giới với hệ thống ngoài**. Mỗi lớp nên có hai bản cài đặt: bản **sandbox** (giả lập, dùng khi phát triển và chấm bài) và bản thật gọi REST API của nhà cung cấp. Chỉ cần đổi thân hàm; các Frm không biết đang dùng bản nào. Thiết kế không ghi kiểu trả về, nên dự án thống nhất **hợp đồng** sau:

#### `AssistantEngine` — `control/gateway/assistant_engine.py`

Hệ thống ngoài: AI Model Service — LLM của Chương 3, có chế độ cơ bản. Được dùng bởi: AssistantFrm, ReviewFrm, StyleDetailFrm.

- **`def ask(self, question: str, style: Style) -> dict`**  
  Trả `{"answer": str, "mode": AssistantMode, "model_name": str, "events": list[GroundingEvent]}`. Che dữ liệu cá nhân trong câu hỏi, đưa dữ liệu thật của style (giá, tồn, chất liệu, bảng cỡ, chính sách) làm ngữ cảnh, kiểm tra câu trả lời với dữ liệu đó và loại câu sai (mỗi câu loại là một event).
- **`def summarise_reviews(self, style: Style) -> str`**  
  Tóm tắt các đánh giá `approved` của style (ưu/nhược, độ vừa cỡ). Chuỗi rỗng nếu chưa có đánh giá.
- **`def moderate(self, review: Review) -> tuple[bool, str]`**  
  Kiểm duyệt đánh giá: `(True, "")` nếu đăng được; `(False, lý_do)` nếu có ngôn từ xấu, dữ liệu cá nhân, quảng cáo → chờ duyệt tay.

#### `NotificationGateway` — `control/gateway/notification_gateway.py`

Hệ thống ngoài: Email/SMS Service. Được dùng bởi: CheckoutFrm, ManageOrderFrm, ProcessReturnFrm.

- **`def send(self, notification: Notification) -> bool`**  
  Gửi `notification.message` qua `notification.channel` tới khách. `True` → Frm đặt `status = SENT`, `sent_at = now`; `False` → `FAILED`.

#### `PaymentGateway` — `control/gateway/payment_gateway.py`

Hệ thống ngoài: Payment Service (VNPay / MoMo / thẻ — sandbox). Được dùng bởi: CheckoutFrm, ConfirmOrderFrm, LinkPaymentMethodFrm, ManageOrderFrm, ProcessReturnFrm.

- **`def charge(self, order: Order, method: PaymentMethod) -> tuple[bool, str]`**  
  Thu `order.grand_total` bằng `method` (None với ví / chuyển khoản không liên kết). Trả `(thành_công, transaction_ref)`. Không ném lỗi khi bị từ chối; chỉ ném khi không kết nối được.
- **`def refund(self, payment: Payment) -> tuple[bool, str]`**  
  Hoàn `payment.amount` cho giao dịch `payment.transaction_ref`. Trả `(thành_công, ref_hoàn)`.
- **`def link_method(self, customer: Customer, type: str, provider: str) -> PaymentMethod | None`**  
  Mở trang liên kết của nhà cung cấp; trả `PaymentMethod` chỉ có `provider`, `method_type`, `masked_number` (không có số đầy đủ); `None` nếu khách huỷ.

#### `SearchEngine` — `control/gateway/search_engine.py`

Hệ thống ngoài: AI Model Service — CLIP (ảnh), Whisper (giọng nói), Chương 3. Được dùng bởi: SearchStyleFrm.

- **`def search_by_image(self, image: bytes) -> list[int]`**  
  Mã hoá ảnh, tìm style gần nhất trong chỉ mục vector; trả id style theo độ phù hợp giảm dần (tối đa ~20).
- **`def search_by_voice(self, audio: bytes) -> list[int]`**  
  Chuyển giọng nói thành văn bản rồi tìm như văn bản; trả id style.

#### `ShippingGateway` — `control/gateway/shipping_gateway.py`

Hệ thống ngoài: Shipping Provider (GHN / GHTK). Được dùng bởi: ManageOrderFrm, ProcessReturnFrm, TrackShipmentFrm.

- **`def create_shipment(self, shipment: Shipment) -> tuple[str, str]`**  
  Đăng ký kiện với hãng (địa chỉ kho → địa chỉ khách, hoặc ngược lại với kiện trả). Trả `(carrier, tracking_no)`.
- **`def get_tracking(self, shipment: Shipment) -> list[ShipmentEvent]`**  
  Các sự kiện theo dõi hiện có của kiện (chưa có `id`, có `shipmentId`).


Mã sandbox mẫu (đủ để chạy toàn bộ luồng mà không cần dịch vụ thật):

```python
# control/gateway/payment_gateway.py
import uuid

class PaymentGateway:
    def charge(self, order: Order, method: PaymentMethod) -> tuple[bool, str]:
        # Sandbox: thẻ có masked_number kết thúc "0002" luôn bị từ chối, để thử E2
        ok = not (method and (method.masked_number or "").endswith("0002"))
        return ok, "SBX-" + uuid.uuid4().hex[:12].upper()

    def refund(self, payment: Payment) -> tuple[bool, str]:
        return True, "SBX-R-" + uuid.uuid4().hex[:10].upper()

    def link_method(self, customer: Customer, type: str, provider: str) -> PaymentMethod:
        return PaymentMethod(provider=provider, method_type=LinkedMethodType(type),
                                masked_number="**** " + uuid.uuid4().hex[:4], is_default=False,
                                customerId=customer.id)
```

```python
# control/gateway/shipping_gateway.py
from datetime import datetime

class ShippingGateway:
    def create_shipment(self, shipment: Shipment) -> tuple[str, str]:
        return "GHN-SANDBOX", f"GHN{shipment.id:08d}"           # (carrier, tracking_no)

    def get_tracking(self, shipment: Shipment) -> list[ShipmentEvent]:
        return [ShipmentEvent(status=ShipmentStatus.IN_TRANSIT, occurred_at=datetime.now(),
                                 note="Sandbox: đang vận chuyển", shipmentId=shipment.id)]
```

Bản thật của `SearchEngine` và `AssistantEngine` gọi các mô hình của Chương 3 (CLIP cho ảnh, Whisper cho giọng nói, LLM cho trợ lý). Khi không có mô hình, `AssistantEngine` chạy **chế độ cơ bản** (`mode = BASIC`): trả lời bằng mẫu câu từ dữ liệu sản phẩm (giá, tồn kho, chất liệu, bảng cỡ), không bịa thông tin (NFR14).

---

## 8. View layer — các màn hình Frm

### 8.1. Khung chung của một Frm

Mã sinh cho mỗi màn hình là `class XxxFrm(tk.Toplevel)`. Mẫu lập trình thống nhất:

```python
import tkinter as tk
from tkinter import ttk, messagebox


class CartFrm(tk.Toplevel):
    def __init__(self, customer: Customer):
        super().__init__()
        self.customer = customer
        self.cart_dao = CartDAO()
        self.stock_level_dao = StockLevelDAO()
        self.title("Giỏ hàng")
        self._build()            # tạo và đặt widget
        self._reload()           # nạp dữ liệu

    # ---------- dựng giao diện ----------
    def _build(self) -> None:
        self.tbl_cart_item = ttk.Treeview(self, columns=("sku", "name", "colour", "size", "price", "qty", "total"),
                                          show="headings", height=10)
        for c, t in zip(self.tbl_cart_item["columns"],
                        ("SKU", "Sản phẩm", "Màu", "Cỡ", "Đơn giá", "SL", "Thành tiền")):
            self.tbl_cart_item.heading(c, text=t)
        self.tbl_cart_item.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
        self.spn_quantity = ttk.Spinbox(self, from_=0, to=99, width=5)
        self.spn_quantity.grid(row=1, column=0, sticky="w", padx=8)
        self.btn_update_quantity = ttk.Button(self, text="Cập nhật", command=self.on_update_quantity)
        self.btn_update_quantity.grid(row=1, column=1)
        self.btn_remove_item = ttk.Button(self, text="Xoá", command=self.on_remove_item)
        self.btn_remove_item.grid(row=1, column=2)
        self.lbl_subtotal = ttk.Label(self, text="")
        self.lbl_subtotal.grid(row=2, column=0, columnspan=2, sticky="w", padx=8)
        self.lbl_message = ttk.Label(self, foreground="red")
        self.lbl_message.grid(row=3, column=0, columnspan=4, sticky="w", padx=8)
        self.btn_continue_shopping = ttk.Button(self, text="Tiếp tục mua", command=self.on_continue_shopping)
        self.btn_continue_shopping.grid(row=4, column=2, pady=8)
        self.btn_checkout = ttk.Button(self, text="Thanh toán", command=self.on_checkout)
        self.btn_checkout.grid(row=4, column=3, pady=8)

    def _reload(self) -> None:
        self.cart = self.cart_dao.get_cart_by_customer(self.customer)
        self.tbl_cart_item.delete(*self.tbl_cart_item.get_children())
        for i in self.cart.items:
            self.tbl_cart_item.insert("", "end", iid=str(i.id), values=(
                i.sku, i.style_name, i.colour, i.size_label, f"{i.price:,}", i.quantity, f"{i.quantity * i.price:,}"))
        self.lbl_subtotal.config(text=f"Tạm tính: {self.cart.subtotal:,} đ")

    def _selected_item(self):
        sel = self.tbl_cart_item.selection()
        return next((i for i in self.cart.items if str(i.id) == sel[0]), None) if sel else None

    # ---------- handler ----------
    def on_checkout(self):
        if not self.cart.items:
            self.lbl_message.config(text="Giỏ hàng trống")
            return
        bad = self.stock_level_dao.check_availability(self.cart.items)        # UC29
        if bad:
            self.lbl_message.config(text="Không đủ hàng: " + ", ".join(b.sku for b in bad))
            return
        CheckoutFrm(self.customer, self.cart)
```

Các kỹ thuật dùng lặp lại:

| Nhu cầu | Cách làm |
|---|---|
| Mở màn hình kế tiếp | Tạo `NextFrm(...)` — nó là một `Toplevel` mới, truyền đối tượng qua constructor |
| Chờ màn hình con đóng rồi nạp lại | `frm = EditAddressFrm(...); self.wait_window(frm); self._reload()` |
| Màn hình chọn trả kết quả (`SelectStyleFrm`, `SelectVariantFrm`) | Màn hình con lưu kết quả vào thuộc tính (`list_selected`, `selected`); cha đọc sau `wait_window` |
| Hộp thoại mô thức | `frm.transient(self); frm.grab_set()` |
| Lấy dòng chọn trong Treeview | dùng `iid = str(entity.id)` khi insert, tra lại trong `list_…` |
| Xác nhận | `messagebox.askyesno("Xác nhận", "…?", parent=self)` |
| Tác vụ chậm (AI, cổng thanh toán) | `threading.Thread(target=…, daemon=True).start()` và cập nhật giao diện bằng `self.after(0, callback)` — không chạm widget từ luồng phụ |
| Đăng xuất | đóng mọi `Toplevel` của phiên, hiện lại cửa sổ đăng nhập (mục 9.1) |
| Tiền | hiển thị `f"{x:,}".replace(",", ".") + " đ"` |

### 8.2. Sơ đồ điều hướng

```
LoginFrm ─┬─ RegisterFrm
          ├─ CustomerHomeFrm ─┬─ BrowseStyleFrm ─┐
          │                   ├─ SearchStyleFrm ─┴─ StyleDetailFrm ── AssistantFrm
          │                   ├─ CartFrm ── CheckoutFrm ── ConfirmOrderFrm ── OrderDetailFrm
          │                   │               └─ EditAddressFrm
          │                   ├─ OrderListFrm ── OrderDetailFrm ─┬─ TrackShipmentFrm
          │                   │                                  ├─ CancelRequestFrm
          │                   │                                  ├─ ReviewFrm
          │                   │                                  └─ ReturnRequestFrm
          │                   └─ ProfileFrm ─┬─ EditAddressFrm
          │                                  └─ LinkPaymentMethodFrm
          ├─ AdminHomeFrm ─┬─ SearchAccountFrm ── EditAccountFrm
          │                ├─ AuditLogFrm
          │                ├─ ManageStyleFrm ── EditStyleFrm ── EditVariantFrm
          │                └─ ManageReviewFrm
          ├─ ManagerHomeFrm ─┬─ SearchOrderFrm ── ManageOrderFrm
          │                  ├─ ManageStyleFrm (như trên)
          │                  ├─ SearchReturnRequestFrm ── ProcessReturnFrm
          │                  └─ SelectReportFrm
          ├─ MerchandiserHomeFrm ─┬─ ManagePromotionFrm ── EditPromotionFrm ── SelectStyleFrm
          │                       └─ SelectReportFrm
          ├─ MarketingHomeFrm ── SelectReportFrm ─┬─ SalesReportFrm ── SalesDetailFrm
          │                                       ├─ ReturnReportFrm ── ReturnDetailFrm
          │                                       └─ StockLevelFrm (hàng sắp hết)
          ├─ CustomerServiceHomeFrm ─┬─ SearchReturnRequestFrm ── ProcessReturnFrm
          │                          ├─ ManageReviewFrm
          │                          └─ SelectReportFrm
          ├─ WarehouseHomeFrm ─┬─ StockLevelFrm ─┬─ AdjustStockFrm
          │                    │                 └─ StockMovementFrm
          │                    ├─ ManageRestockFrm ── EditRestockRequestFrm ── SelectVariantFrm
          │                    └─ SearchReturnRequestFrm ── InspectReturnFrm
          └─ SupplierHomeFrm ── ConfirmRestockFrm
```

### 8.3. Tham chiếu từng màn hình

Mỗi mục: file, vai trò, constructor, DAO/gateway dùng (theo association trong mô hình), màn hình mở được, dữ liệu giữ, widget, việc trong `__init__`, rồi từng handler.

### Package `view.account`

#### `AdminHomeFrm` — `view/account/admin_home_frm.py`

Trang chủ quản trị viên.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | — |
| Mở (view) | SearchAccountFrm |
| Dữ liệu giữ | `staff: StaffMember` |
| Widget | `btn_manage_account`, `btn_manage_product`, `btn_manage_review`, `btn_view_audit_log`, `btn_logout` |
| `__init__` làm gì | — |

Handler:

- **`on_manage_account(self) -> None`** — Mở `SearchAccountFrm(staff)`.
- **`on_manage_product(self) -> None`** — Mở `ManageStyleFrm(staff)`.
- **`on_manage_review(self) -> None`** — Mở `ManageReviewFrm(staff)`.
- **`on_view_audit_log(self) -> None`** — Mở `AuditLogFrm(staff)`.
- **`on_logout(self) -> None`** — Như `CustomerHomeFrm.on_logout`.

#### `AuditLogFrm` — `view/account/audit_log_frm.py`

Xem nhật ký thay đổi (UC20).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | AuditLogEntryDAO |
| Mở (view) | — |
| Dữ liệu giữ | `staff: StaffMember`, `list_entry: list[AuditLogEntry]` |
| Widget | `dte_from`, `dte_to`, `cbo_staff`, `cbo_action`, `btn_view`, `tbl_audit_log` |
| `__init__` làm gì | Mặc định 7 ngày gần nhất; `cbo_staff` từ `StaffMemberDAO.get_all_staff_member` (cần thêm DAO này), `cbo_action` từ `AuditAction`. |

Handler:

- **`on_view(self) -> None`** — `list_entry = AuditLogEntryDAO.search_audit_log_entry(start, end, staff|None, action|None)`; đổ vào `tbl_audit_log`.

#### `CustomerHomeFrm` — `view/account/customer_home_frm.py`

Trang chủ của khách: tìm kiếm và đi tới các chức năng.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer)` |
| Dùng (control) | — |
| Mở (view) | ProfileFrm, BrowseStyleFrm, SearchStyleFrm, CartFrm, OrderListFrm |
| Dữ liệu giữ | `customer: Customer` |
| Widget | `txt_keyword`, `btn_search`, `btn_search_by_image`, `btn_browse`, `btn_cart`, `btn_orders`, `btn_profile`, `btn_logout` |
| `__init__` làm gì | Hiện "Xin chào <full_name>". |

Handler:

- **`on_search(self) -> None`** — Mở `SearchStyleFrm(customer, keyword=txt_keyword)`; trang tìm kiếm chạy luôn tìm theo từ khoá.
- **`on_search_by_image(self) -> None`** — Mở `SearchStyleFrm(customer, "")` và gọi ngay `on_search_by_image()` của nó (chọn ảnh).
- **`on_browse(self) -> None`** — Mở `BrowseStyleFrm(customer)`.
- **`on_cart(self) -> None`** — Mở `CartFrm(customer)`.
- **`on_orders(self) -> None`** — Mở `OrderListFrm(customer)`.
- **`on_profile(self) -> None`** — Mở `ProfileFrm(customer)`.
- **`on_logout(self) -> None`** — Đóng mọi cửa sổ con, huỷ trang chủ, hiện lại LoginFrm (xoá ô mật khẩu).

#### `EditAccountFrm` — `view/account/edit_account_frm.py`

Khoá / mở / đặt lại mật khẩu / đổi vai trò (UC20).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, user: User)` |
| Dùng (control) | UserDAO, StaffMemberDAO |
| Mở (view) | AuditLogFrm |
| Dữ liệu giữ | `staff: StaffMember`, `user: User` |
| Widget | `lbl_email`, `lbl_full_name`, `lbl_status`, `lbl_last_login_at`, `cbo_role`, `btn_suspend`, `btn_activate`, `btn_reset_password`, `btn_save_role` |
| `__init__` làm gì | Hiện thông tin `user`; nếu là nhân viên thì nạp `StaffMemberDAO.get_staff_member_by_user` và bật `cbo_role`, ngược lại ẩn. |

Handler:

- **`on_suspend(self) -> None`** — Xác nhận; không cho tự khoá chính mình; `user.status = SUSPENDED`; `UserDAO.update_user_status`; ghi nhật ký `SUSPEND_ACCOUNT` (`AuditLogEntryDAO`, cần thêm vào Frm — xem mục 13).
- **`on_activate(self) -> None`** — `user.status = ACTIVE`; `update_user_status`; nhật ký `UPDATE`.
- **`on_reset_password(self) -> None`** — Sinh mật khẩu tạm (`secrets.token_urlsafe(8)`), `UserDAO.reset_password`, hiện cho quản trị viên một lần; nhật ký `RESET_PASSWORD`.
- **`on_save_role(self) -> None`** — `staff_member.role = StaffRole(cbo_role)`; `StaffMemberDAO.update_role`; nhật ký `UPDATE`.

#### `EditAddressFrm` — `view/account/edit_address_frm.py`

Thêm / sửa một địa chỉ. `address = None` → thêm mới.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer, address: Address \| None)` |
| Dùng (control) | AddressDAO |
| Mở (view) | — |
| Dữ liệu giữ | `customer: Customer`, `address: Address \| None` |
| Widget | `txt_recipient_name`, `txt_phone`, `txt_street`, `txt_ward`, `txt_district`, `chk_is_default`, `btn_save`, `btn_reset` |
| `__init__` làm gì | Điền ô từ `address` nếu có. |

Handler:

- **`on_save(self) -> None`** — Kiểm tra bắt buộc (người nhận, điện thoại, đường, phường, quận, thành phố); gán vào `address` (tạo mới nếu None, `customerId = customer.id`); `add_address` hoặc `update_address`; đóng.
- **`on_reset(self) -> None`** — Khôi phục giá trị ban đầu.

#### `LinkPaymentMethodFrm` — `view/account/link_payment_method_frm.py`

Liên kết thẻ / ví / tài khoản ngân hàng (UC03).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer)` |
| Dùng (control) | PaymentMethodDAO, PaymentGateway |
| Mở (view) | — |
| Dữ liệu giữ | `customer: Customer` |
| Widget | `cbo_method_type`, `cbo_provider`, `chk_is_default`, `btn_link`, `btn_cancel` |
| `__init__` làm gì | Đổ `LinkedMethodType` vào `cbo_method_type`; danh sách nhà cung cấp theo loại vào `cbo_provider`. |

Handler:

- **`on_link(self) -> None`** — Gọi `PaymentGateway.link_method(customer, type, provider)` — cổng thanh toán tự thu thập số thẻ trên trang của họ và chỉ trả `masked_number` (+ token). Tạo `PaymentMethod` và `PaymentMethodDAO.add_payment_method`. Thất bại → báo lỗi, không lưu gì.
- **`on_cancel(self) -> None`** — Đóng.

#### `LoginFrm` — `view/account/login_frm.py`

Màn hình đầu tiên (UC02). Mọi vai trò đăng nhập ở đây.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self)` |
| Dùng (control) | UserDAO |
| Mở (view) | RegisterFrm, CustomerHomeFrm, AdminHomeFrm, ManagerHomeFrm, MerchandiserHomeFrm, WarehouseHomeFrm, CustomerServiceHomeFrm, SupplierHomeFrm, MarketingHomeFrm |
| Dữ liệu giữ | — |
| Widget | `txt_email`, `txt_password`, `btn_login`, `btn_register`, `lbl_message` |
| `__init__` làm gì | Tạo `txt_email`, `txt_password` (`show="*"`), hai nút, `lbl_message`. Gán `bind("<Return>", …)` để Enter = đăng nhập. |

Handler:

- **`on_login(self) -> None`** — Đọc e-mail, mật khẩu; kiểm tra không rỗng. Tạo `User(email=…, password=…)` và gọi `UserDAO.check_login(user)`. `False` → `lbl_message` = "Sai e-mail hoặc mật khẩu". `True` → xác định vai trò: `CustomerDAO.get_customer_by_user` → `CustomerHomeFrm(customer)`; `SupplierDAO.get_supplier_by_user` → `SupplierHomeFrm(supplier)`; `StaffMemberDAO.get_staff_member_by_user` → theo `staff.role`: ADMINISTRATOR→`AdminHomeFrm`, MANAGER→`ManagerHomeFrm`, MERCHANDISER→`MerchandiserHomeFrm`, MARKETING→`MarketingHomeFrm`, CUSTOMER_SERVICE→`CustomerServiceHomeFrm`, WAREHOUSE→`WarehouseHomeFrm` (SALES: xem mục 13). Ẩn LoginFrm (`withdraw()`) thay vì huỷ, để đăng xuất thì hiện lại.
- **`on_register(self) -> None`** — Mở `RegisterFrm()`.

#### `ProfileFrm` — `view/account/profile_frm.py`

Hồ sơ khách: thông tin, sổ địa chỉ, phương thức thanh toán, cỡ đã lưu (UC03).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer)` |
| Dùng (control) | CustomerDAO, AddressDAO, PaymentMethodDAO, SavedSizeDAO |
| Mở (view) | EditAddressFrm, LinkPaymentMethodFrm |
| Dữ liệu giữ | `customer: Customer`, `list_address: list[Address]`, `list_payment_method: list[PaymentMethod]`, `list_saved_size: list[SavedSize]` |
| Widget | `txt_full_name`, `txt_phone`, `txt_preferred_colours`, `chk_marketing_consent`, `tbl_address`, `btn_add_address`, `btn_edit_address`, `btn_delete_address`, `tbl_payment_method`, `btn_link_payment_method`, `btn_remove_payment_method`, `tbl_saved_size`, `cbo_category`, `txt_size_label`, `btn_save_size`, `btn_save` |
| `__init__` làm gì | Điền ô nhập từ `customer`; nạp `list_address = AddressDAO.get_address_by_customer`, `list_payment_method = PaymentMethodDAO.get_payment_method_by_customer`, `list_saved_size = SavedSizeDAO.get_saved_size_by_customer`, đổ vào 3 Treeview; nạp danh mục cho `cbo_category`. Viết một hàm riêng `_reload()` để gọi lại sau mỗi thay đổi. |

Handler:

- **`on_save(self) -> None`** — Kiểm tra họ tên, điện thoại; gán vào `customer`; `CustomerDAO.update_customer`.
- **`on_add_address(self) -> None`** — Mở `EditAddressFrm(customer, None)`; chờ đóng (`wait_window`) rồi `_reload()`.
- **`on_edit_address(self) -> None`** — Lấy địa chỉ đang chọn trong `tbl_address` (chưa chọn → báo); mở `EditAddressFrm(customer, address)`; `_reload()`.
- **`on_delete_address(self) -> None`** — Hỏi xác nhận (`messagebox.askyesno`); `AddressDAO.delete_address`; `_reload()`.
- **`on_link_payment_method(self) -> None`** — Mở `LinkPaymentMethodFrm(customer)`; `_reload()`.
- **`on_remove_payment_method(self) -> None`** — Xác nhận; `PaymentMethodDAO.delete_payment_method`; báo nếu không xoá được vì đã dùng.
- **`on_save_size(self) -> None`** — Tạo `SavedSize(size_label, customerId, categoryId)` từ `cbo_category`, `txt_size_label`; `SavedSizeDAO.save_saved_size`; `_reload()`.

#### `RegisterFrm` — `view/account/register_frm.py`

Đăng ký tài khoản khách (UC01).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self)` |
| Dùng (control) | CustomerDAO |
| Mở (view) | AdminHomeFrm |
| Dữ liệu giữ | — |
| Widget | `txt_full_name`, `txt_email`, `txt_phone`, `txt_password`, `txt_confirm_password`, `chk_marketing_consent`, `btn_register`, `btn_cancel`, `lbl_message` |
| `__init__` làm gì | Tạo các ô nhập, `chk_marketing_consent` gắn `tk.BooleanVar`. |

Handler:

- **`on_register(self) -> None`** — Kiểm tra: đủ trường; e-mail đúng dạng; điện thoại số; mật khẩu ≥ 8 ký tự có chữ và số; hai mật khẩu trùng (UC01 E2). `UserDAO.is_email_used(email)` → báo "E-mail đã được dùng" (E1). Dựng `Customer(email, password, full_name, phone, marketing_consent)` và gọi `CustomerDAO.add_customer`. Thành công → thông báo, đóng, quay về LoginFrm (điền sẵn e-mail).
- **`on_cancel(self) -> None`** — Đóng màn hình.

#### `SearchAccountFrm` — `view/account/search_account_frm.py`

Tìm tài khoản (UC20).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | UserDAO |
| Mở (view) | EditAccountFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_user: list[User]` |
| Widget | `txt_keyword`, `cbo_user_type`, `cbo_status`, `btn_search`, `tbl_user` |
| `__init__` làm gì | Đổ `cbo_user_type` (Tất cả/Khách/Nhân viên/Nhà cung cấp), `cbo_status`; Treeview cột e-mail, tên, loại, trạng thái, đăng nhập cuối. |

Handler:

- **`on_search(self) -> None`** — `list_user = UserDAO.search_user(key, user_type, status)`; đổ vào `tbl_user`.
- **`on_select_user(self) -> None`** — Mở `EditAccountFrm(staff, user đang chọn)` (gán cho double-click Treeview); đóng xong thì tìm lại.

### Package `view.catalogue`

#### `AssistantFrm` — `view/catalogue/assistant_frm.py`

Hỏi trợ lý AI về sản phẩm (UC32).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer \| None, style: Style)` |
| Dùng (control) | AssistantTurnDAO, AssistantEngine |
| Mở (view) | — |
| Dữ liệu giữ | `customer: Customer \| None`, `style: Style`, `list_turn: list[AssistantTurn]` |
| Widget | `txa_conversation`, `txt_question`, `btn_ask`, `lbl_mode` |
| `__init__` làm gì | Nếu có `customer`: `list_turn = AssistantTurnDAO.get_turn_by_customer(customer, style)` và hiện lại hội thoại trong `txa_conversation` (chỉ đọc). |

Handler:

- **`on_ask(self) -> None`** — Câu hỏi rỗng → bỏ qua. Ghi thời điểm; `result = AssistantEngine.ask(question, style)` (trả câu trả lời, `mode`, `model_name`, các grounding event — mục 7.3); thêm vào hội thoại; `lbl_mode` hiện "AI" hoặc "cơ bản". Tạo `AssistantTurn` (question đã che, answer, mode, latency_ms, created_at, customerId|None, styleId) + events; `AssistantTurnDAO.add_assistant_turn`. Chạy `ask` trong luồng phụ (`threading`) để giao diện không treo, cập nhật UI bằng `after()`.

#### `BrowseStyleFrm` — `view/catalogue/browse_style_frm.py`

Duyệt sản phẩm theo danh mục có bộ lọc (UC04). `customer` có thể `None` (khách vãng lai).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer \| None)` |
| Dùng (control) | CategoryDAO, StyleDAO |
| Mở (view) | StyleDetailFrm |
| Dữ liệu giữ | `customer: Customer \| None`, `list_category: list[Category]`, `list_style: list[Style]` |
| Widget | `tree_category`, `cbo_size`, `cbo_colour`, `cbo_fit_type`, `txt_min_price`, `txt_max_price`, `cbo_sort`, `btn_filter`, `tbl_style` |
| `__init__` làm gì | `list_category = CategoryDAO.get_all_category()` rồi dựng `tree_category` (Treeview lồng theo `parentId`); đổ giá trị lọc cỡ, màu, `FitType`, cách sắp xếp. |

Handler:

- **`on_select_category(self) -> None`** — Khi chọn nút cây: ghi nhớ danh mục và gọi `on_filter()`.
- **`on_filter(self) -> None`** — Đọc bộ lọc (giá phải là số, min ≤ max); `list_style = StyleDAO.get_style_by_category(category, size, colour, fit_type, min_price, max_price, sort)`; đổ vào `tbl_style` (tên, thương hiệu, giá từ …).
- **`on_open_style(self) -> None`** — Mở `StyleDetailFrm(customer, style đang chọn)`.

#### `SearchStyleFrm` — `view/catalogue/search_style_frm.py`

Tìm kiếm bằng chữ, ảnh, giọng nói (UC05).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer \| None, keyword: str)` |
| Dùng (control) | StyleDAO, SearchEngine |
| Mở (view) | StyleDetailFrm |
| Dữ liệu giữ | `customer: Customer \| None`, `list_style: list[Style]` |
| Widget | `txt_keyword`, `btn_search`, `btn_search_by_image`, `btn_search_by_voice`, `cnv_query_image`, `tbl_style`, `lbl_message` |
| `__init__` làm gì | Nếu `keyword` khác rỗng: điền ô và gọi `on_search()` ngay. |

Handler:

- **`on_search(self) -> None`** — `list_style = StyleDAO.search_style(keyword)`; không có kết quả → `lbl_message` gợi ý từ khoá khác.
- **`on_search_by_image(self) -> None`** — `filedialog.askopenfilename` (jpg/png); hiện ảnh trên `cnv_query_image` (Pillow → `ImageTk.PhotoImage`); đọc bytes; `ids = SearchEngine.search_by_image(bytes)`; `list_style = StyleDAO.search_style_by_ids(ids)`. Lỗi dịch vụ AI → báo và gợi ý tìm bằng chữ.
- **`on_search_by_voice(self) -> None`** — Ghi âm vài giây (thư viện `sounddevice`) hoặc chọn file âm thanh; `ids = SearchEngine.search_by_voice(bytes)`; `search_style_by_ids`.
- **`on_open_style(self) -> None`** — Mở `StyleDetailFrm(customer, style)`.

#### `StyleDetailFrm` — `view/catalogue/style_detail_frm.py`

Trang chi tiết sản phẩm (UC06, UC33).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer \| None, style: Style)` |
| Dùng (control) | StyleDAO, ProductVariantDAO, ReviewDAO, StockLevelDAO, PromotionDAO, CartDAO, AssistantEngine |
| Mở (view) | AssistantFrm |
| Dữ liệu giữ | `customer: Customer \| None`, `style: Style`, `list_variant: list[ProductVariant]`, `list_media: list[ProductMedia]`, `list_review: list[Review]`, `selected_variant: ProductVariant \| None` |
| Widget | `lbl_name`, `lbl_brand`, `lbl_price`, `lbl_promotion`, `cnv_media`, `txa_description`, `lbl_material`, `lbl_care_instructions`, `lbl_model_info`, `tbl_size_chart`, `cbo_colour`, `cbo_size`, `lbl_availability`, `spn_quantity`, `btn_add_to_cart`, `lbl_review_summary`, `tbl_review`, `btn_ask_assistant` |
| `__init__` làm gì | `style = StyleDAO.get_style_detail(style)`; `list_variant = ProductVariantDAO.get_variant_by_style`; `list_media = ProductMediaDAO.get_media_by_style` (ảnh đầu lên `cnv_media`); vật liệu + bảng cỡ (cần thêm `MaterialComponentDAO`, `SizeChartEntryDAO` — mục 13); `list_review = ReviewDAO.get_approved_review_by_style`; `lbl_review_summary = AssistantEngine.summarise_reviews(style)` (UC33, lỗi → bỏ trống); khuyến mãi `PromotionDAO.get_active_promotion_by_style` → `lbl_promotion`; đổ màu/cỡ có thật vào `cbo_colour`, `cbo_size`. |

Handler:

- **`on_select_variant(self) -> None`** — Khi đổi màu/cỡ: tìm biến thể khớp trong `list_variant` → `selected_variant`; hiện giá (và giá sau giảm nếu có khuyến mãi) ở `lbl_price`; `StockLevelDAO.get_stock_level_by_variant` → `lbl_availability` (Còn hàng / Chỉ còn n / Hết hàng); giới hạn `spn_quantity` tối đa `available`.
- **`on_add_to_cart(self) -> None`** — Khách vãng lai (`customer is None`) → yêu cầu đăng nhập. Chưa chọn biến thể / hết hàng → báo. `cart = CartDAO.get_cart_by_customer(customer)`; `CartDAO.add_cart_item(cart, CartItem(productVariantId=…, quantity=…))`; báo thành công.
- **`on_ask_assistant(self) -> None`** — Mở `AssistantFrm(customer, style)`.

### Package `view.checkout`

#### `CartFrm` — `view/checkout/cart_frm.py`

Giỏ hàng (UC07).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer)` |
| Dùng (control) | CartDAO, StockLevelDAO |
| Mở (view) | CheckoutFrm |
| Dữ liệu giữ | `customer: Customer`, `cart: Cart` |
| Widget | `tbl_cart_item`, `spn_quantity`, `btn_update_quantity`, `btn_remove_item`, `lbl_subtotal`, `lbl_message`, `btn_continue_shopping`, `btn_checkout` |
| `__init__` làm gì | `cart = CartDAO.get_cart_by_customer(customer)`; đổ `tbl_cart_item` (SKU, tên, màu, cỡ, đơn giá, số lượng, thành tiền); `lbl_subtotal`. Viết `_reload()`. |

Handler:

- **`on_update_quantity(self) -> None`** — Lấy dòng đang chọn và số ở `spn_quantity`; 0 → hỏi xoá; ngược lại `item.quantity = n`, `CartDAO.update_cart_item`; `_reload()`.
- **`on_remove_item(self) -> None`** — `CartDAO.delete_cart_item(item)`; `_reload()`.
- **`on_continue_shopping(self) -> None`** — Đóng giỏ, quay về màn hình trước.
- **`on_checkout(self) -> None`** — Giỏ rỗng → báo. UC29: `bad = StockLevelDAO.check_availability(cart.items)`; có dòng thiếu → liệt kê ở `lbl_message`, tô đỏ dòng, dừng. Hợp lệ → mở `CheckoutFrm(customer, cart)`.

#### `CheckoutFrm` — `view/checkout/checkout_frm.py`

Thanh toán (UC08 + UC26, UC28–UC31).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer, cart: Cart)` |
| Dùng (control) | AddressDAO, PaymentMethodDAO, VoucherDAO, OrderDAO, PaymentDAO, NotificationDAO, PaymentGateway, NotificationGateway |
| Mở (view) | ConfirmOrderFrm |
| Dữ liệu giữ | `customer: Customer`, `cart: Cart`, `order: Order`, `list_address: list[Address]`, `list_payment_method: list[PaymentMethod]`, `list_voucher: list[Voucher]` |
| Widget | `tbl_order_item`, `cbo_address`, `btn_add_address`, `rdo_delivery_service`, `txt_voucher_code`, `btn_apply_voucher`, `rdo_payment_method`, `cbo_linked_method`, `txt_note`, `lbl_subtotal`, `lbl_discount`, `lbl_shipping_fee`, `lbl_grand_total`, `btn_place_order`, `btn_back` |
| `__init__` làm gì | Nạp `list_address` → `cbo_address` (chọn mặc định); `list_payment_method` → `cbo_linked_method`; `rdo_delivery_service` (STANDARD/EXPRESS) và `rdo_payment_method` (COD/CARD/E_WALLET/BANK_TRANSFER) gắn `StringVar`; dựng `order = Order(...)` và các dòng từ `cart.items` (`unit_price = price`, `discount = 0`); `_recalc()` tính `subtotal`, `shipping_fee`, `discount`, `grand_total` (UC30) và hiện lên các nhãn. |

Handler:

- **`on_add_address(self) -> None`** — Mở `EditAddressFrm(customer, None)`; `wait_window`; nạp lại `list_address` và chọn địa chỉ mới.
- **`on_change_delivery_service(self) -> None`** — `order.delivery_service = DeliveryService(var)`; phí theo bảng phí (mục 9.4); `_recalc()`.
- **`on_apply_voucher(self) -> None`** — UC26: `voucher = VoucherDAO.get_voucher_by_code(code)`; kiểm tra (không tồn tại / chương trình không active / ngoài thời gian / hết lượt / dưới `min_order_value` / không có style áp dụng trong giỏ) → báo lý do cụ thể. Hợp lệ: tính giảm (PERCENT: `subtotal_đủ_điều_kiện × value / 100`; FIXED_AMOUNT: `value`, không vượt subtotal đủ điều kiện); phân bổ vào `discount` của từng dòng (theo tỉ lệ thành tiền, dòng cuối nhận phần dư để tổng khớp); thêm vào `list_voucher`; `_recalc()`.
- **`on_place_order(self) -> None`** — Kiểm tra đã chọn địa chỉ, phương thức. Gán `order.note`, `order.delivery_service`. (1) `OrderDAO.add_order(order, customer)` — `False` → báo "Sản phẩm vừa hết hàng", quay lại giỏ. (2) Nếu COD: `order.status = CONFIRMED`, `OrderDAO.update_order_status(order)`. Ngược lại `ok, ref = PaymentGateway.charge(order, method)`; `PaymentDAO.add_payment(Payment(kind=CHARGE, method, amount=grand_total, status=SUCCEEDED/FAILED, transaction_ref=ref, …), order)`; thành công → `status = CONFIRMED`, `update_order_status`. (3) Thông báo: `NotificationGateway.send(n)` rồi `NotificationDAO.add_notification(n, customer)` với `ORDER_CONFIRMED`. (4) Mở `ConfirmOrderFrm(customer, order)` và đóng CheckoutFrm, CartFrm. Thanh toán thất bại: đơn vẫn `pending_payment`, giữ hàng; ConfirmOrderFrm cho thanh toán lại.
- **`on_back(self) -> None`** — Đóng, quay lại giỏ.

#### `ConfirmOrderFrm` — `view/checkout/confirm_order_frm.py`

Kết quả đặt hàng.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer, order: Order)` |
| Dùng (control) | PaymentDAO, PaymentGateway |
| Mở (view) | — |
| Dữ liệu giữ | `customer: Customer`, `order: Order` |
| Widget | `lbl_order_no`, `lbl_status`, `tbl_order_item`, `tbl_shipment`, `lbl_grand_total`, `lbl_payment_result`, `btn_retry_payment`, `btn_view_order`, `btn_continue_shopping` |
| `__init__` làm gì | Đọc lại `OrderDAO.get_order_detail` (cần thêm OrderDAO hoặc dùng đối tượng truyền vào); hiện mã đơn, trạng thái, dòng hàng, các kiện (theo kho), tổng tiền, kết quả thanh toán; `btn_retry_payment` chỉ bật khi `pending_payment`. |

Handler:

- **`on_retry_payment(self) -> None`** — Như bước (2) của `on_place_order`: `PaymentGateway.charge` → `PaymentDAO.add_payment` → nếu thành công cập nhật trạng thái đơn và giao diện.
- **`on_view_order(self) -> None`** — Mở `OrderDetailFrm(customer, order)`.
- **`on_continue_shopping(self) -> None`** — Đóng, về trang chủ.

### Package `view.inventory`

#### `AdjustStockFrm` — `view/inventory/adjust_stock_frm.py`

Điều chỉnh tồn có lý do (UC17, FR23).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, stock_level: StockLevel)` |
| Dùng (control) | StockLevelDAO |
| Mở (view) | — |
| Dữ liệu giữ | `staff: StaffMember`, `stock_level: StockLevel` |
| Widget | `lbl_sku`, `lbl_stock_location`, `lbl_on_hand`, `lbl_reserved`, `spn_quantity_change`, `txt_reference`, `txa_note`, `btn_save`, `btn_cancel` |
| `__init__` làm gì | Hiện SKU, kho, `on_hand`, `reserved`. |

Handler:

- **`on_save(self) -> None`** — Số thay đổi ≠ 0; `on_hand + change ≥ reserved`; tham chiếu và ghi chú bắt buộc. `movement = StockMovement(quantity_change, reason=ADJUSTMENT, reference, note, productVariantId, stockLocationId, staffMemberId=staff.id)`; `StockLevelDAO.adjust_stock(stock_level, movement)`; nhật ký `ADJUST_STOCK`; đóng.
- **`on_cancel(self) -> None`** — Đóng.

#### `ConfirmRestockFrm` — `view/inventory/confirm_restock_frm.py`

Nhà cung cấp xác nhận / từ chối phiếu.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, supplier: Supplier, restock_request: RestockRequest)` |
| Dùng (control) | RestockRequestDAO |
| Mở (view) | — |
| Dữ liệu giữ | `supplier: Supplier`, `restock_request: RestockRequest` |
| Widget | `lbl_request_no`, `lbl_stock_location`, `tbl_restock_item`, `dte_expected_date`, `txa_supplier_note`, `btn_confirm`, `btn_refuse` |
| `__init__` làm gì | `get_restock_request_detail`; hiện các dòng; chỉ cho thao tác khi `SENT`. |

Handler:

- **`on_confirm(self) -> None`** — `dte_expected_date` ≥ hôm nay; `status = CONFIRMED`, `confirm_at = today`, `expected_date`, `supplier_note`; `update_restock_request`.
- **`on_refuse(self) -> None`** — Ghi chú lý do bắt buộc (UC17 E1); `status = CANCELLED`; `update_restock_request`.

#### `EditRestockRequestFrm` — `view/inventory/edit_restock_request_frm.py`

Lập / sửa phiếu nhập hàng.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, restock_request: RestockRequest \| None)` |
| Dùng (control) | RestockRequestDAO, SupplierDAO, StockLocationDAO |
| Mở (view) | SelectVariantFrm |
| Dữ liệu giữ | `staff: StaffMember`, `restock_request: RestockRequest`, `list_supplier: list[Supplier]`, `list_stock_location: list[StockLocation]` |
| Widget | `lbl_request_no`, `cbo_supplier`, `cbo_stock_location`, `dte_expected_date`, `tbl_restock_item`, `spn_quantity`, `btn_add_item`, `btn_remove_item`, `btn_save_draft`, `btn_send` |
| `__init__` làm gì | Nạp nhà cung cấp, kho; nếu có phiếu: `get_restock_request_detail` → bảng dòng; ngược lại phiếu mới `DRAFT`. |

Handler:

- **`on_add_item(self) -> None`** — Mở `SelectVariantFrm()`; `wait_window`; với biến thể đã chọn thêm `RestockItem(quantity=spn_quantity, productVariantId)` (cộng dồn nếu đã có).
- **`on_remove_item(self) -> None`** — Bỏ dòng đang chọn.
- **`on_save_draft(self) -> None`** — Có nhà cung cấp, kho, ít nhất một dòng; `add_restock_request` (mới) hoặc `update_restock_request`; `status = DRAFT`.
- **`on_send(self) -> None`** — Như lưu nháp nhưng `status = SENT`; (tuỳ chọn) gửi e-mail cho nhà cung cấp qua `NotificationGateway`.

#### `ManageRestockFrm` — `view/inventory/manage_restock_frm.py`

Danh sách phiếu nhập hàng (UC17).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | RestockRequestDAO, StockLevelDAO, StockMovementDAO |
| Mở (view) | EditRestockRequestFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_restock_request: list[RestockRequest]` |
| Widget | `cbo_status`, `cbo_supplier`, `btn_search`, `tbl_restock_request`, `btn_create`, `btn_open`, `btn_mark_received` |
| `__init__` làm gì | `cbo_status`, `cbo_supplier` (cần SupplierDAO); `on_search()`. |

Handler:

- **`on_search(self) -> None`** — `list_restock_request = RestockRequestDAO.search_restock_request(status|None, supplier|None)`.
- **`on_create(self) -> None`** — Mở `EditRestockRequestFrm(staff, None)`; tìm lại.
- **`on_open(self) -> None`** — Mở `EditRestockRequestFrm(staff, request)` (chỉ sửa được khi `draft`).
- **`on_mark_received(self) -> None`** — Chỉ với phiếu `confirmed`: xác nhận; `request = get_restock_request_detail(request)`; `RestockRequestDAO.receive_restock_request(request, staff)` (tồn + sổ kho trong DAO); báo.

#### `SelectVariantFrm` — `view/inventory/select_variant_frm.py`

Chọn một biến thể (dùng ở phiếu nhập hàng).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self)` |
| Dùng (control) | ProductVariantDAO |
| Mở (view) | — |
| Dữ liệu giữ | `list_variant: list[ProductVariant]` |
| Widget | `txt_keyword`, `btn_search`, `tbl_variant`, `btn_select` |
| `__init__` làm gì | — |

Handler:

- **`on_search(self) -> None`** — `list_variant = ProductVariantDAO.search_variant(key)`.
- **`on_select(self) -> None`** — Lưu biến thể đang chọn vào thuộc tính (vd. `self.selected`) rồi đóng.

#### `StockLevelFrm` — `view/inventory/stock_level_frm.py`

Tồn kho theo kho (UC17), cũng là báo cáo hàng sắp hết.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | StockLevelDAO, StockLocationDAO |
| Mở (view) | AdjustStockFrm, StockMovementFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_stock_level: list[StockLevel]` |
| Widget | `cbo_stock_location`, `txt_keyword`, `chk_below_reorder_point`, `btn_search`, `tbl_stock_level`, `btn_adjust`, `btn_history` |
| `__init__` làm gì | `cbo_stock_location` từ `StockLocationDAO.get_all_stock_location` (+ "Tất cả"); `on_search()`. |

Handler:

- **`on_search(self) -> None`** — `list_stock_level = StockLevelDAO.search_stock_level(location|None, key, below_reorder_point)`; dòng dưới điểm đặt hàng tô đỏ.
- **`on_adjust(self) -> None`** — Mở `AdjustStockFrm(staff, stock_level đang chọn)`; tìm lại.
- **`on_history(self) -> None`** — Mở `StockMovementFrm(variant của dòng đang chọn)` (dựng `ProductVariant(id=productVariantId, …)`).

#### `StockMovementFrm` — `view/inventory/stock_movement_frm.py`

Sổ kho của một biến thể.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, variant: ProductVariant)` |
| Dùng (control) | StockMovementDAO |
| Mở (view) | — |
| Dữ liệu giữ | `variant: ProductVariant`, `list_movement: list[StockMovement]` |
| Widget | `dte_from`, `dte_to`, `cbo_reason`, `btn_view`, `tbl_movement` |
| `__init__` làm gì | Mặc định 30 ngày; `cbo_reason` (Tất cả + MovementReason); `on_view()`. |

Handler:

- **`on_view(self) -> None`** — `list_movement = StockMovementDAO.get_movement_by_variant(variant, start, end, reason|None)`.

#### `SupplierHomeFrm` — `view/inventory/supplier_home_frm.py`

Trang chủ nhà cung cấp: các phiếu được gửi tới họ.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, supplier: Supplier)` |
| Dùng (control) | RestockRequestDAO |
| Mở (view) | ConfirmRestockFrm |
| Dữ liệu giữ | `supplier: Supplier`, `list_restock_request: list[RestockRequest]` |
| Widget | `cbo_status`, `tbl_restock_request`, `btn_open`, `btn_logout` |
| `__init__` làm gì | `cbo_status`; `list_restock_request = RestockRequestDAO.search_restock_request(status, supplier)` (chỉ phiếu từ SENT). |

Handler:

- **`on_open(self) -> None`** — Mở `ConfirmRestockFrm(supplier, request)`; nạp lại.
- **`on_logout(self) -> None`** — Đăng xuất.

#### `WarehouseHomeFrm` — `view/inventory/warehouse_home_frm.py`

Trang chủ nhân viên kho.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | — |
| Mở (view) | StockLevelFrm, ManageRestockFrm, SearchReturnRequestFrm |
| Dữ liệu giữ | `staff: StaffMember` |
| Widget | `btn_view_stock`, `btn_restock`, `btn_inspect_return`, `btn_logout` |
| `__init__` làm gì | — |

Handler:

- **`on_view_stock(self) -> None`** — Mở `StockLevelFrm(staff)`.
- **`on_restock(self) -> None`** — Mở `ManageRestockFrm(staff)`.
- **`on_inspect_return(self) -> None`** — Mở `SearchReturnRequestFrm(staff)` (với vai trò kho, mở `InspectReturnFrm`).
- **`on_logout(self) -> None`** — Đăng xuất.

### Package `view.order`

#### `CancelRequestFrm` — `view/order/cancel_request_frm.py`

Huỷ đơn / gửi yêu cầu huỷ (UC10).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, order: Order)` |
| Dùng (control) | OrderDAO |
| Mở (view) | — |
| Dữ liệu giữ | `order: Order` |
| Widget | `lbl_order_no`, `cbo_reason`, `txt_reason_detail`, `btn_send`, `btn_back` |
| `__init__` làm gì | Hiện mã đơn; `cbo_reason` các lý do có sẵn + "Khác" (bật `txt_reason_detail`). |

Handler:

- **`on_send(self) -> None`** — Lý do bắt buộc. Nếu đơn `pending_payment`/`confirmed`: `order.cancel_reason = …`; `OrderDAO.cancel_order(order)` (hoàn tiền nếu đã thu — mục 8.4). Nếu `processing`: chỉ ghi lý do và để quản lý duyệt — thiết kế không có trạng thái "yêu cầu huỷ" riêng, nên lưu `cancel_reason` với trạng thái giữ nguyên; `ManageOrderFrm.on_approve_cancel_request` nhận biết qua `cancel_reason IS NOT NULL`. Đã giao vận chuyển → báo không huỷ được, gợi ý trả hàng.
- **`on_back(self) -> None`** — Đóng.

#### `OrderDetailFrm` — `view/order/order_detail_frm.py`

Chi tiết đơn và các hành động sau mua (UC09–UC14).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer, order: Order)` |
| Dùng (control) | OrderDAO |
| Mở (view) | TrackShipmentFrm, CancelRequestFrm, ReviewFrm, ReturnRequestFrm |
| Dữ liệu giữ | `customer: Customer`, `order: Order` |
| Widget | `lbl_order_no`, `lbl_placed_at`, `lbl_status`, `lbl_address`, `tbl_order_item`, `tbl_payment`, `tbl_shipment`, `lbl_subtotal`, `lbl_discount`, `lbl_shipping_fee`, `lbl_grand_total`, `btn_track`, `btn_cancel_request`, `btn_confirm_received`, `btn_review`, `btn_return` |
| `__init__` làm gì | `order = OrderDAO.get_order_detail(order)`; kiểm tra `order.customerId == customer.id` (NFR03); hiện thông tin, dòng hàng, thanh toán, kiện. Bật/tắt nút theo trạng thái: Huỷ khi `pending_payment/confirmed/processing`; Đã nhận khi `delivered`; Đánh giá khi `delivered/completed` và dòng chưa đánh giá; Trả hàng khi `delivered/completed`, trong hạn và chưa có yêu cầu (`ReturnRequestDAO.get_return_request_by_order` — cần thêm DAO). |

Handler:

- **`on_track(self) -> None`** — Chọn kiện trong `tbl_shipment` (một kiện thì lấy luôn); mở `TrackShipmentFrm(shipment)`.
- **`on_cancel_request(self) -> None`** — Mở `CancelRequestFrm(order)`; đóng xong nạp lại đơn.
- **`on_confirm_received(self) -> None`** — UC12: xác nhận; `order.status = COMPLETED`; `OrderDAO.update_order_status`.
- **`on_review(self) -> None`** — Lấy dòng đang chọn trong `tbl_order_item`; mở `ReviewFrm(customer, order_item)`.
- **`on_return(self) -> None`** — Mở `ReturnRequestFrm(customer, order)`.

#### `OrderListFrm` — `view/order/order_list_frm.py`

Danh sách đơn của khách (UC09).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer)` |
| Dùng (control) | OrderDAO |
| Mở (view) | OrderDetailFrm |
| Dữ liệu giữ | `customer: Customer`, `list_order: list[Order]` |
| Widget | `cbo_status`, `btn_filter`, `tbl_order` |
| `__init__` làm gì | Đổ `cbo_status` (Tất cả + OrderStatus); gọi `on_filter()`. |

Handler:

- **`on_filter(self) -> None`** — `list_order = OrderDAO.get_order_by_customer(customer, status|None)`; đổ `tbl_order` (mã, ngày, trạng thái, tổng).
- **`on_open_order(self) -> None`** — Mở `OrderDetailFrm(customer, order)`; đóng xong thì lọc lại (trạng thái có thể đổi).

#### `ReturnRequestFrm` — `view/order/return_request_frm.py`

Yêu cầu trả / đổi hàng (UC14).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer, order: Order)` |
| Dùng (control) | ReturnRequestDAO |
| Mở (view) | — |
| Dữ liệu giữ | `customer: Customer`, `order: Order`, `return_request: ReturnRequest`, `list_evidence: list[ReturnEvidence]` |
| Widget | `tbl_order_item`, `spn_quantity`, `rdo_return_type`, `cbo_reason_code`, `txa_reason_detail`, `rdo_desired_resolution`, `btn_add_evidence`, `tbl_evidence`, `btn_submit` |
| `__init__` làm gì | Đổ `tbl_order_item` từ `order.items`; `rdo_return_type` (RETURN/EXCHANGE); `cbo_reason_code` (ReturnReason); `rdo_desired_resolution`; tạo `return_request` rỗng với `items = []`. |

Handler:

- **`on_select_item(self) -> None`** — Thêm dòng đang chọn vào yêu cầu với số lượng `spn_quantity` (≤ số đã mua). Đổi hàng: chọn biến thể thay thế cùng style (cỡ/màu khác) — lưu tạm trên dòng.
- **`on_add_evidence(self) -> None`** — Chọn ảnh/video; sao chép vào thư mục media; tạo `ReturnEvidence(url, media_type)`; thêm vào `list_evidence` và `tbl_evidence`.
- **`on_submit(self) -> None`** — Kiểm tra có ít nhất một dòng, có lý do; lỗi/sai hàng nên có bằng chứng. Gán các trường; `ReturnRequestDAO.add_return_request(return_request, order)`; báo mã yêu cầu; đóng.

#### `ReviewFrm` — `view/order/review_frm.py`

Đánh giá sản phẩm đã mua (UC13, UC34).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, customer: Customer, order_item: OrderItem)` |
| Dùng (control) | ReviewDAO, AssistantEngine |
| Mở (view) | — |
| Dữ liệu giữ | `customer: Customer`, `order_item: OrderItem` |
| Widget | `lbl_style_name`, `lbl_variant`, `spn_rating`, `txa_body`, `txt_size_purchased`, `rdo_fit_vote`, `btn_submit`, `lbl_message` |
| `__init__` làm gì | Hiện tên, màu, cỡ của dòng đơn; `spn_rating` 1–5; `rdo_fit_vote` (FitVote); điền sẵn `txt_size_purchased` = cỡ đã mua. |

Handler:

- **`on_submit(self) -> None`** — Kiểm tra sao 1–5, nội dung không rỗng; `ReviewDAO.is_reviewed(order_item)` → đã đánh giá thì báo. UC34: `ok, note = AssistantEngine.moderate(review)` → `status = APPROVED` nếu ok, ngược lại `PENDING` (chờ duyệt) kèm `moderation_note`; `ReviewDAO.add_review(review, order_item)`; báo kết quả (đã đăng / đang chờ duyệt).

#### `TrackShipmentFrm` — `view/order/track_shipment_frm.py`

Theo dõi kiện (UC11).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, shipment: Shipment)` |
| Dùng (control) | ShipmentDAO, ShippingGateway |
| Mở (view) | — |
| Dữ liệu giữ | `shipment: Shipment` |
| Widget | `lbl_carrier`, `lbl_tracking_no`, `lbl_status`, `tbl_shipment_record`, `tbl_shipment_event`, `btn_refresh` |
| `__init__` làm gì | Hiện hãng, mã vận đơn, trạng thái; `ShipmentDAO.get_shipment_event` → `tbl_shipment_event`. |

Handler:

- **`on_refresh(self) -> None`** — Nếu có `tracking_no`: `events = ShippingGateway.get_tracking(shipment)`; với sự kiện mới `ShipmentDAO.add_shipment_event`; nạp lại bảng.

### Package `view.order_admin`

#### `ManageOrderFrm` — `view/order_admin/manage_order_frm.py`

Xử lý đơn: chuyển trạng thái, huỷ, duyệt yêu cầu huỷ, hoàn tiền (UC22, UC23, UC10).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, order: Order)` |
| Dùng (control) | OrderDAO, ShipmentDAO, PaymentDAO, StockMovementDAO, NotificationDAO, PaymentGateway, ShippingGateway, NotificationGateway |
| Mở (view) | — |
| Dữ liệu giữ | `staff: StaffMember`, `order: Order` |
| Widget | `lbl_order_no`, `lbl_customer`, `lbl_status`, `tbl_order_item`, `tbl_payment`, `tbl_shipment`, `cbo_new_status`, `btn_update_status`, `txt_cancel_reason`, `btn_cancel_order`, `btn_approve_cancel_request`, `btn_refund` |
| `__init__` làm gì | `order = OrderDAO.get_order_detail(order)`; hiện dòng hàng, thanh toán (`PaymentDAO.get_payment_by_order`), kiện (`ShipmentDAO.get_shipment_by_order`); `cbo_new_status` chỉ chứa các trạng thái kế tiếp hợp lệ (mục 10.1). |

Handler:

- **`on_update_status(self) -> None`** — Ví dụ `confirmed→processing` (bắt đầu đóng gói); khi chuyển sang giao: với mỗi kiện `requested` gọi `ShippingGateway.create_shipment(shipment)` → `carrier`, `tracking_no`; `ShipmentDAO.update_shipment` (`status = PICKED_UP`); `order.status = PARTIALLY_SHIPPED/SHIPPED` theo số kiện đã đi; `OrderDAO.update_order_status`; thông báo `ORDER_SHIPPED`. Khi hãng báo giao xong → `DELIVERED` + thông báo `ORDER_DELIVERED`.
- **`on_cancel_order(self) -> None`** — UC23: lý do bắt buộc (`txt_cancel_reason`); `OrderDAO.cancel_order` (tồn kho, voucher trong DAO); nếu đã thu tiền → `on_refund` toàn bộ; thông báo `ORDER_CANCELLED`.
- **`on_approve_cancel_request(self) -> None`** — Chỉ bật khi đơn có `cancel_reason` do khách gửi và chưa giao vận chuyển; thực hiện như `on_cancel_order` với lý do của khách.
- **`on_refund(self) -> None`** — Số hoàn ≤ đã thu ròng (`get_payment_by_order`); `ok, ref = PaymentGateway.refund(payment)`; `PaymentDAO.add_payment(Payment(kind=REFUND, amount, status, ref, paymentMethodId của lần thu), order)`; thông báo `REFUND_COMPLETED`; ghi nhật ký.

#### `ManagerHomeFrm` — `view/order_admin/manager_home_frm.py`

Trang chủ quản lý.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | — |
| Mở (view) | SearchOrderFrm |
| Dữ liệu giữ | `staff: StaffMember` |
| Widget | `btn_manage_order`, `btn_manage_product`, `btn_process_return`, `btn_view_report`, `btn_logout` |
| `__init__` làm gì | — |

Handler:

- **`on_manage_order(self) -> None`** — Mở `SearchOrderFrm(staff)`.
- **`on_manage_product(self) -> None`** — Mở `ManageStyleFrm(staff)`.
- **`on_process_return(self) -> None`** — Mở `SearchReturnRequestFrm(staff)`.
- **`on_view_report(self) -> None`** — Mở `SelectReportFrm(staff)`.
- **`on_logout(self) -> None`** — Đăng xuất.

#### `SearchOrderFrm` — `view/order_admin/search_order_frm.py`

Tìm đơn (UC22).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | OrderDAO |
| Mở (view) | ManageOrderFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_order: list[Order]` |
| Widget | `txt_keyword`, `cbo_status`, `dte_from`, `dte_to`, `btn_search`, `tbl_order` |
| `__init__` làm gì | Mặc định 30 ngày gần nhất. |

Handler:

- **`on_search(self) -> None`** — `list_order = OrderDAO.search_order(key, status|None, start, end)`; đổ bảng; tô màu đơn có yêu cầu huỷ.
- **`on_open_order(self) -> None`** — Mở `ManageOrderFrm(staff, order)`; đóng xong tìm lại.

### Package `view.product`

#### `EditStyleFrm` — `view/product/edit_style_frm.py`

Thêm / sửa style với vật liệu, bảng cỡ, media, biến thể (UC21).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, style: Style \| None)` |
| Dùng (control) | StyleDAO, CategoryDAO, CollectionDAO, SupplierDAO, ProductMediaDAO, MaterialComponentDAO, SizeChartEntryDAO, ProductVariantDAO, AuditLogEntryDAO |
| Mở (view) | EditVariantFrm |
| Dữ liệu giữ | `staff: StaffMember`, `style: Style`, `list_category: list[Category]`, `list_supplier: list[Supplier]`, `list_collection: list[Collection]` |
| Widget | `txt_code`, `txt_name`, `txa_description`, `txt_brand`, `cbo_fit_type`, `txt_care_instructions`, `txt_features`, `txt_model_info`, `cbo_status`, `cbo_category`, `cbo_supplier`, `cbo_collection`, `tbl_material`, `txt_material`, `spn_percent`, `btn_add_material`, `tbl_size_chart`, `txt_size_label`, `cbo_measure`, `txt_value_cm`, `btn_add_size_entry`, `tbl_media`, `btn_upload_media`, `tbl_variant`, `btn_add_variant`, `btn_edit_variant`, `btn_save`, `btn_reset` |
| `__init__` làm gì | Nạp `list_category`, `list_supplier` (`SupplierDAO.get_all_supplier`), `list_collection`; nếu `style` có sẵn: `get_style_detail`, `get_material_by_style`, `get_size_chart_by_style`, `get_media_by_style`, `get_variant_by_style` và đổ vào các bảng; ngược lại tạo `Style(status=DRAFT)`. Giữ danh sách vật liệu / bảng cỡ trong bộ nhớ đến khi Lưu. |

Handler:

- **`on_add_material(self) -> None`** — Thêm (`txt_material`, `spn_percent`) vào bảng tạm; cảnh báo nếu tổng > 100.
- **`on_add_size_entry(self) -> None`** — Thêm (`txt_size_label`, `cbo_measure`, `txt_value_cm` > 0) vào bảng cỡ tạm.
- **`on_upload_media(self) -> None`** — Chọn file; sao chép vào thư mục media; `ProductMediaDAO.add_media` (style phải đã có id — nếu chưa lưu lần nào thì lưu style trước).
- **`on_add_variant(self) -> None`** — Style phải đã có `id`; mở `EditVariantFrm(staff, style, None)`; nạp lại biến thể.
- **`on_edit_variant(self) -> None`** — Mở `EditVariantFrm(staff, style, variant đang chọn)`.
- **`on_save(self) -> None`** — Kiểm tra mã, tên, danh mục, nhà cung cấp; tổng vật liệu = 100 nếu muốn `ACTIVE`. Gán ô vào `style`; trong một transaction (`with DAO.con.transaction():`): `add_style` hoặc `update_style`, `MaterialComponentDAO.save_material`, `SizeChartEntryDAO.save_size_chart`, `AuditLogEntryDAO.add_audit_log_entry` (CREATE/UPDATE, `changes` = các trường thay đổi).
- **`on_reset(self) -> None`** — Nạp lại từ CSDL (hoặc xoá form nếu thêm mới).

#### `EditVariantFrm` — `view/product/edit_variant_frm.py`

Thêm / sửa một biến thể (SKU).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, style: Style, variant: ProductVariant \| None)` |
| Dùng (control) | ProductVariantDAO, StockLocationDAO, StockLevelDAO |
| Mở (view) | — |
| Dữ liệu giữ | `staff: StaffMember`, `style: Style`, `variant: ProductVariant \| None`, `list_stock_location: list[StockLocation]` |
| Widget | `txt_sku`, `txt_size_label`, `txt_colour`, `txt_price`, `cbo_status`, `cbo_stock_location`, `spn_reorder_point`, `btn_save`, `btn_reset` |
| `__init__` làm gì | Nạp `list_stock_location` vào `cbo_stock_location` (chỉ bật khi thêm mới — mỗi biến thể một kho); `cbo_status` (VariantStatus). |

Handler:

- **`on_save(self) -> None`** — Kiểm tra SKU, cỡ, màu, giá > 0. Mới: trong một transaction `ProductVariantDAO.add_variant(variant, style)` rồi `StockLevelDAO.add_stock_level(StockLevel(on_hand=0, reserved=0, available=0, reorder_point=spn_reorder_point), variant, location)`. Sửa: `update_variant`. Trùng SKU / cỡ-màu → báo.
- **`on_reset(self) -> None`** — Khôi phục.

#### `ManageStyleFrm` — `view/product/manage_style_frm.py`

Danh sách sản phẩm cho quản trị (UC21).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | StyleDAO |
| Mở (view) | EditStyleFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_style: list[Style]` |
| Widget | `txt_keyword`, `cbo_category`, `cbo_status`, `btn_search`, `tbl_style`, `btn_add`, `btn_edit`, `btn_deactivate` |
| `__init__` làm gì | `cbo_category`, `cbo_status` để lọc; gọi `on_search()`. |

Handler:

- **`on_search(self) -> None`** — `list_style = StyleDAO.search_style(key)`, lọc tiếp theo danh mục / trạng thái ở Frm; đổ bảng.
- **`on_add(self) -> None`** — Mở `EditStyleFrm(staff, None)`; tìm lại khi đóng.
- **`on_edit(self) -> None`** — Mở `EditStyleFrm(staff, style đang chọn)`.
- **`on_deactivate(self) -> None`** — Xác nhận; `StyleDAO.deactivate_style`; nhật ký `DEACTIVATE`.

### Package `view.promotion`

#### `EditPromotionFrm` — `view/promotion/edit_promotion_frm.py`

Thêm / sửa khuyến mãi, style áp dụng, voucher (UC15, UC27).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, promotion: Promotion \| None)` |
| Dùng (control) | PromotionDAO, VoucherDAO |
| Mở (view) | SelectStyleFrm |
| Dữ liệu giữ | `staff: StaffMember`, `promotion: Promotion`, `list_style: list[Style]`, `list_voucher: list[Voucher]` |
| Widget | `txt_name`, `cbo_promo_type`, `cbo_discount_type`, `txt_discount_value`, `txt_min_order_value`, `dte_starts_at`, `dte_ends_at`, `cbo_status`, `tbl_style`, `btn_add_style`, `btn_remove_style`, `tbl_voucher`, `txt_voucher_code`, `spn_usage_limit`, `btn_add_voucher`, `btn_save`, `btn_reset` |
| `__init__` làm gì | Nếu có `promotion`: `get_promotion_detail` → `list_style`, `list_voucher = VoucherDAO.get_voucher_by_promotion`; đổ PromoType, DiscountType, PromotionStatus vào combobox. |

Handler:

- **`on_add_style(self) -> None`** — Mở `SelectStyleFrm(list_style)`; `wait_window`; lấy `list_selected` của nó gán lại `list_style`; đổ bảng.
- **`on_remove_style(self) -> None`** — Bỏ style đang chọn khỏi `list_style`.
- **`on_add_voucher(self) -> None`** — Chương trình phải đã lưu (có `id`); mã không rỗng, `usage_limit > 0`; `VoucherDAO.add_voucher(Voucher(code, usage_limit), promotion)`; nạp lại.
- **`on_save(self) -> None`** — Kiểm tra tên, `ends_at > starts_at`, giá trị giảm (PERCENT 1–100, FIXED > 0), `min_order_value ≥ 0`; gán `promotion.styles = list_style`; `add_promotion` hoặc `update_promotion`.
- **`on_reset(self) -> None`** — Khôi phục.

#### `ManagePromotionFrm` — `view/promotion/manage_promotion_frm.py`

Danh sách khuyến mãi (UC15).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | PromotionDAO |
| Mở (view) | EditPromotionFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_promotion: list[Promotion]` |
| Widget | `txt_keyword`, `cbo_status`, `btn_search`, `tbl_promotion`, `btn_add`, `btn_edit`, `btn_end` |
| `__init__` làm gì | `cbo_status`; `on_search()`. |

Handler:

- **`on_search(self) -> None`** — `list_promotion = PromotionDAO.search_promotion(key, status|None)`.
- **`on_add(self) -> None`** — Mở `EditPromotionFrm(staff, None)`.
- **`on_edit(self) -> None`** — Mở `EditPromotionFrm(staff, promotion đang chọn)`.
- **`on_end(self) -> None`** — Xác nhận; `promotion.status = ENDED`; `PromotionDAO.update_promotion`.

#### `MerchandiserHomeFrm` — `view/promotion/merchandiser_home_frm.py`

Trang chủ merchandiser.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | — |
| Mở (view) | ManagePromotionFrm |
| Dữ liệu giữ | `staff: StaffMember` |
| Widget | `btn_manage_promotion`, `btn_view_report`, `btn_logout` |
| `__init__` làm gì | — |

Handler:

- **`on_manage_promotion(self) -> None`** — Mở `ManagePromotionFrm(staff)`.
- **`on_view_report(self) -> None`** — Mở `SelectReportFrm(staff)`.
- **`on_logout(self) -> None`** — Đăng xuất.

#### `SelectStyleFrm` — `view/promotion/select_style_frm.py`

Chọn nhiều style (dùng lại ở EditPromotionFrm).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, selected: list[Style])` |
| Dùng (control) | StyleDAO |
| Mở (view) | — |
| Dữ liệu giữ | `list_style: list[Style]`, `list_selected: list[Style]` |
| Widget | `txt_keyword`, `cbo_category`, `btn_search`, `tbl_style`, `btn_select` |
| `__init__` làm gì | Sao chép `selected` vào `list_selected`; đánh dấu các dòng đã chọn. |

Handler:

- **`on_search(self) -> None`** — `list_style = StyleDAO.search_style(key)` (lọc danh mục ở Frm); Treeview `selectmode="extended"`.
- **`on_select(self) -> None`** — Gộp các dòng đang chọn vào `list_selected` (không trùng); đóng — Frm gọi đọc `list_selected` sau `wait_window`.

### Package `view.report`

#### `MarketingHomeFrm` — `view/report/marketing_home_frm.py`

Trang chủ marketing.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | — |
| Mở (view) | SelectReportFrm |
| Dữ liệu giữ | `staff: StaffMember` |
| Widget | `btn_view_report`, `btn_logout` |
| `__init__` làm gì | — |

Handler:

- **`on_view_report(self) -> None`** — Mở `SelectReportFrm(staff)`.
- **`on_logout(self) -> None`** — Đăng xuất.

#### `ReturnDetailFrm` — `view/report/return_detail_frm.py`

Chi tiết các dòng trả của một style.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, return_stat: ReturnStat, start: date, end: date)` |
| Dùng (control) | ReturnItemDAO |
| Mở (view) | — |
| Dữ liệu giữ | `return_stat: ReturnStat`, `list_return_item: list[ReturnItem]` |
| Widget | `lbl_style_name`, `tbl_return_item` |
| `__init__` làm gì | `list_return_item = ReturnItemDAO.get_return_item_by_style(return_stat, start, end)`. |


#### `ReturnReportFrm` — `view/report/return_report_frm.py`

Báo cáo trả hàng theo style.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | ReturnStatDAO |
| Mở (view) | ReturnDetailFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_return_stat: list[ReturnStat]` |
| Widget | `dte_from`, `dte_to`, `cbo_reason`, `btn_view`, `tbl_return_stat` |
| `__init__` làm gì | `cbo_reason` (Tất cả + ReturnReason). |

Handler:

- **`on_view(self) -> None`** — `list_return_stat = ReturnStatDAO.get_return_stat(start, end, reason|None)`; hiện tỉ lệ dạng %.
- **`on_open_detail(self) -> None`** — Mở `ReturnDetailFrm(return_stat, start, end)`.

#### `SalesDetailFrm` — `view/report/sales_detail_frm.py`

Chi tiết các dòng đơn của một style.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, style_stat: StyleStat, start: date, end: date)` |
| Dùng (control) | OrderItemDAO |
| Mở (view) | — |
| Dữ liệu giữ | `style_stat: StyleStat`, `list_order_item: list[OrderItem]` |
| Widget | `lbl_style_name`, `lbl_period`, `tbl_order_item` |
| `__init__` làm gì | `list_order_item = OrderItemDAO.get_order_item_by_style(style_stat, start, end)`; đổ bảng (mã đơn, ngày, SKU, SL, đơn giá, giảm, thành tiền). |


#### `SalesReportFrm` — `view/report/sales_report_frm.py`

Báo cáo doanh số theo style.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | StyleStatDAO |
| Mở (view) | SalesDetailFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_style_stat: list[StyleStat]` |
| Widget | `dte_from`, `dte_to`, `cbo_category`, `cbo_collection`, `btn_view`, `tbl_style_stat`, `lbl_total_revenue`, `btn_export` |
| `__init__` làm gì | Mặc định tháng hiện tại; `cbo_category`, `cbo_collection` (+ "Tất cả"). |

Handler:

- **`on_view(self) -> None`** — Từ ≤ đến; `list_style_stat = StyleStatDAO.get_style_stat(start, end, category|None, collection|None)`; đổ bảng (mã, tên, SL bán, doanh thu, số đơn); `lbl_total_revenue = Σ revenue`.
- **`on_open_detail(self) -> None`** — Mở `SalesDetailFrm(style_stat, start, end)`.
- **`on_export(self) -> None`** — `filedialog.asksaveasfilename(".csv")`; ghi `list_style_stat` bằng module `csv` (UTF-8 có BOM để Excel đọc đúng tiếng Việt).

#### `SelectReportFrm` — `view/report/select_report_frm.py`

Chọn loại báo cáo (UC16, UC24).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | — |
| Mở (view) | SalesReportFrm, ReturnReportFrm |
| Dữ liệu giữ | `staff: StaffMember` |
| Widget | `cbo_report_type`, `btn_select` |
| `__init__` làm gì | `cbo_report_type`: Doanh số theo sản phẩm / Trả hàng theo sản phẩm / Hàng sắp hết. |

Handler:

- **`on_select(self) -> None`** — Mở `SalesReportFrm(staff)`, `ReturnReportFrm(staff)` hoặc `StockLevelFrm(staff)` (tick "dưới điểm đặt hàng").

### Package `view.returns`

#### `CustomerServiceHomeFrm` — `view/returns/customer_service_home_frm.py`

Trang chủ chăm sóc khách hàng.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | — |
| Mở (view) | SearchReturnRequestFrm, ManageReviewFrm |
| Dữ liệu giữ | `staff: StaffMember` |
| Widget | `btn_process_return`, `btn_manage_review`, `btn_view_report`, `btn_logout` |
| `__init__` làm gì | — |

Handler:

- **`on_process_return(self) -> None`** — Mở `SearchReturnRequestFrm(staff)`.
- **`on_manage_review(self) -> None`** — Mở `ManageReviewFrm(staff)`.
- **`on_view_report(self) -> None`** — Mở `SelectReportFrm(staff)`.
- **`on_logout(self) -> None`** — Đăng xuất.

#### `InspectReturnFrm` — `view/returns/inspect_return_frm.py`

Kho kiểm tra hàng trả về.

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, return_request: ReturnRequest)` |
| Dùng (control) | ReturnRequestDAO, StockLevelDAO, StockMovementDAO |
| Mở (view) | — |
| Dữ liệu giữ | `staff: StaffMember`, `return_request: ReturnRequest` |
| Widget | `lbl_return_no`, `tbl_return_item`, `cbo_inspection_result`, `txt_inspection_note`, `btn_save_inspection`, `btn_finish` |
| `__init__` làm gì | Chỉ với `IN_TRANSIT`; bảng các dòng trả. |

Handler:

- **`on_save_inspection(self) -> None`** — Dòng đang chọn: `inspection_result = PASSED/FAILED` (`cbo_inspection_result`), `inspection_note` (bắt buộc khi FAILED); `ReturnRequestDAO.update_return_item`.
- **`on_finish(self) -> None`** — Mọi dòng đã kiểm tra. Trong một transaction: mỗi dòng PASSED → `StockLevelDAO.adjust_stock(level, StockMovement(quantity_change=+q, reason=RETURN, reference=return_no, staffMemberId))` (FR29); `status = INSPECTED`; `update_return_request`. Hàng FAILED không nhập kho.

#### `ProcessReturnFrm` — `view/returns/process_return_frm.py`

Xử lý yêu cầu trả / đổi (UC18).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember, return_request: ReturnRequest)` |
| Dùng (control) | ReturnRequestDAO, ShipmentDAO, PaymentDAO, NotificationDAO, PaymentGateway, ShippingGateway, NotificationGateway |
| Mở (view) | — |
| Dữ liệu giữ | `staff: StaffMember`, `return_request: ReturnRequest` |
| Widget | `lbl_return_no`, `lbl_order_no`, `lbl_customer`, `lbl_return_type`, `lbl_reason`, `lbl_status`, `tbl_return_item`, `cnv_evidence`, `txa_decision_note`, `btn_authorise`, `btn_reject`, `btn_create_pickup`, `btn_refund`, `btn_ship_replacement`, `btn_close` |
| `__init__` làm gì | `return_request = get_return_request_detail`; hiện thông tin, dòng trả, ảnh bằng chứng trên `cnv_evidence`; bật nút theo trạng thái (mục 10.2). |

Handler:

- **`on_authorise(self) -> None`** — Kiểm tra hạn trả (E2 quá hạn → tự từ chối); `status = AUTHORISED`, `decision_note`; `update_return_request(request, staff)`; thông báo `RETURN_AUTHORISED`.
- **`on_reject(self) -> None`** — Ghi chú bắt buộc; `status = REJECTED`; thông báo `RETURN_REJECTED`.
- **`on_create_pickup(self) -> None`** — Chỉ khi `AUTHORISED`: `Shipment(direction=RETURN, returnRequestId, stockLocationId = kho nhận, status=REQUESTED, …)` + bản ghi các dòng; `ShipmentDAO.add_shipment(shipment, order)`; `ShippingGateway.create_shipment` → tracking; `update_shipment`; `status = IN_TRANSIT`.
- **`on_refund(self) -> None`** — Chỉ khi `INSPECTED` và yêu cầu là trả tiền: tiền hoàn = Σ (đơn giá × số lượng − phần giảm giá tương ứng) của các dòng `PASSED`; `PaymentGateway.refund` → `PaymentDAO.add_payment(kind=REFUND)`; `status = REFUNDED`; thông báo `REFUND_COMPLETED`.
- **`on_ship_replacement(self) -> None`** — Chỉ khi `INSPECTED` và là đổi hàng: kiểm tra tồn biến thể thay thế (A1 — hết thì đề nghị hoàn tiền); trừ kho bằng `StockLevelDAO.adjust_stock` (`reason = SALE`, `quantity_change = −q`, cần thêm DAO); tạo kiện `OUTBOUND` có `returnRequestId`; `status = EXCHANGED`; thông báo `EXCHANGE_SHIPPED`.
- **`on_close(self) -> None`** — `REFUNDED`/`EXCHANGED`/`REJECTED` → `status = CLOSED`.

#### `SearchReturnRequestFrm` — `view/returns/search_return_request_frm.py`

Danh sách yêu cầu trả hàng (UC18).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | ReturnRequestDAO |
| Mở (view) | ProcessReturnFrm, InspectReturnFrm |
| Dữ liệu giữ | `staff: StaffMember`, `list_return_request: list[ReturnRequest]` |
| Widget | `txt_keyword`, `cbo_status`, `btn_search`, `tbl_return_request` |
| `__init__` làm gì | Vai trò WAREHOUSE: mặc định lọc `IN_TRANSIT`. |

Handler:

- **`on_search(self) -> None`** — `list_return_request = ReturnRequestDAO.search_return_request(key, status|None)`.
- **`on_open(self) -> None`** — `staff.role == WAREHOUSE` → `InspectReturnFrm(staff, request)`; còn lại → `ProcessReturnFrm(staff, request)`.

### Package `view.review`

#### `ManageReviewFrm` — `view/review/manage_review_frm.py`

Duyệt đánh giá (UC19).

| Mục | Nội dung |
|---|---|
| Constructor | `def __init__(self, staff: StaffMember)` |
| Dùng (control) | ReviewDAO |
| Mở (view) | — |
| Dữ liệu giữ | `staff: StaffMember`, `list_review: list[Review]` |
| Widget | `cbo_status`, `txt_keyword`, `spn_rating`, `btn_search`, `tbl_review`, `txa_body`, `txt_moderation_note`, `btn_approve`, `btn_reject` |
| `__init__` làm gì | Mặc định lọc `PENDING`. |

Handler:

- **`on_search(self) -> None`** — `list_review = ReviewDAO.search_review(key, status|None, rating|None)`.
- **`on_select_review(self) -> None`** — Hiện nội dung đầy đủ vào `txa_body` và ghi chú kiểm duyệt.
- **`on_approve(self) -> None`** — `status = APPROVED`; `ReviewDAO.update_review(review, staff)`; tìm lại.
- **`on_reject(self) -> None`** — `moderation_note` bắt buộc; `status = REJECTED`; `update_review`.


---

## 9. Luồng nghiệp vụ chi tiết

Ký hiệu: `Frm.handler → DAO.op` là lời gọi; **[T]** là một database transaction.

### 9.1. Khởi động, đăng nhập theo vai trò, đăng xuất (UC02)

1. `main.main()` tạo `LoginFrm()`. Nên tạo một cửa sổ gốc ẩn để `Toplevel` không kéo theo cửa sổ trống "tk":

   ```python
   # main.py (thân hàm main)
   import tkinter as tk
   root = tk.Tk()
   root.withdraw()                   # cửa sổ gốc ẩn, sống suốt chương trình
   LoginFrm()
   root.mainloop()
   ```
   Khi `LoginFrm` đóng hẳn (nút X) thì gọi `root.destroy()` (`self.protocol("WM_DELETE_WINDOW", …)`).
2. `LoginFrm.on_login` → `UserDAO.check_login(user)` → xác định loại người dùng và mở home:

   ```python
   HOME = {StaffRole.ADMINISTRATOR: AdminHomeFrm, StaffRole.MANAGER: ManagerHomeFrm,
           StaffRole.MERCHANDISER: MerchandiserHomeFrm, StaffRole.MARKETING: MarketingHomeFrm,
           StaffRole.CUSTOMER_SERVICE: CustomerServiceHomeFrm, StaffRole.WAREHOUSE: WarehouseHomeFrm}

   def on_login(self):
       user = User(email=self.txt_email.get().strip(), password=self.txt_password.get())
       if not user.email or not user.password:
           return self.lbl_message.config(text="Nhập e-mail và mật khẩu")
       if not self.user_dao.check_login(user):
           return self.lbl_message.config(text="Sai e-mail hoặc mật khẩu, hoặc tài khoản bị khoá")
       if (c := CustomerDAO().get_customer_by_user(user)):
           home = CustomerHomeFrm(c)
       elif (s := SupplierDAO().get_supplier_by_user(user)):
           home = SupplierHomeFrm(s)
       elif (m := StaffMemberDAO().get_staff_member_by_user(user)) and m.role in HOME:
           home = HOME[m.role](m)
       else:
           return self.lbl_message.config(text="Tài khoản chưa được gán vai trò")
       self.txt_password.delete(0, "end")
       self.withdraw()
       home.protocol("WM_DELETE_WINDOW", home.on_logout)
   ```
3. `XxxHomeFrm.on_logout`: đóng các cửa sổ con đang mở của phiên (giữ danh sách hoặc duyệt `self.master.winfo_children()` trừ LoginFrm), `self.destroy()`, rồi hiện lại LoginFrm (`login.deiconify()`). Cách đơn giản để home biết LoginFrm: truyền qua biến module `abc_fashion.view.account.login_frm.CURRENT_LOGIN` hoặc tìm `Toplevel` có kiểu `LoginFrm` trong `root.winfo_children()`.

### 9.2. Đăng ký (UC01)

`RegisterFrm.on_register`: kiểm tra dữ liệu → `UserDAO.is_email_used` (E1) → `CustomerDAO.add_customer` **[T]** (INSERT `User` + `Customer` + `Cart`) → báo thành công → đóng, quay về đăng nhập.

### 9.3. Đặt hàng (UC07, UC08, UC25, UC26, UC28, UC29, UC30, UC31) — luồng L1

```
CustomerHomeFrm / StyleDetailFrm
   StyleDetailFrm.on_add_to_cart ─→ CartDAO.get_cart_by_customer, CartDAO.add_cart_item
CartFrm
   __init__        ─→ CartDAO.get_cart_by_customer
   on_checkout     ─→ StockLevelDAO.check_availability            (UC29, chỉ đọc)
CheckoutFrm
   __init__        ─→ AddressDAO.get_address_by_customer, PaymentMethodDAO.get_payment_method_by_customer
                      dựng Order + OrderItem từ giỏ; _recalc()                 (UC30)
   on_apply_voucher ─→ VoucherDAO.get_voucher_by_code; tính & phân bổ giảm giá     (UC26)
   on_place_order  ─→ OrderDAO.add_order  [T]                                       (UC08, UC25, UC28)
                         ├ INSERT Order, OrderItem, OrderVoucher, used_count+1
                         ├ StockLevelDAO.reserve_stock  (SELECT … FOR UPDATE)
                         ├ INSERT Shipment + ShipmentRecord theo kho
                         └ CartDAO.clear_cart
                   ─→ PaymentGateway.charge ─→ PaymentDAO.add_payment                (UC31)
                   ─→ OrderDAO.update_order_status(CONFIRMED) [T]  trừ on_hand + sổ kho 'sale'
                   ─→ NotificationGateway.send ─→ NotificationDAO.add_notification
ConfirmOrderFrm    (on_retry_payment nếu thanh toán lỗi)
```

**Mã mẫu `OrderDAO.add_order`** (dùng kết nối chung nên gọi được các DAO khác trong cùng transaction):

```python
from datetime import datetime
import psycopg
from abc_fashion.control.dao.dao import DAO, _val
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.control.dao.cart_dao import CartDAO


class OrderDAO(DAO):
    def add_order(self, order: Order, customer: Customer) -> bool:
        try:
            with self.con.transaction():
                no = self.con.execute(
                    "SELECT 'ORD-' || to_char(now(),'YYMMDD') || '-' || "
                    "lpad((count(*)+1)::text, 3, '0') AS no FROM \"tblOrder\" "
                    "WHERE \"placed_at\"::date = current_date").fetchone()["no"]
                row = self.con.execute(
                    'INSERT INTO "tblOrder"("order_no","status","placed_at","subtotal","discount",'
                    '"shipping_fee","grand_total","delivery_service","note","customerId") '
                    'VALUES (%s,%s,now(),%s,%s,%s,%s,%s,%s,%s) RETURNING "id","placed_at"',
                    (no, "pending_payment", order.subtotal, order.discount, order.shipping_fee,
                     order.grand_total, _val(order.delivery_service), order.note, customer.id)).fetchone()
                order.id, order.order_no, order.placed_at = row["id"], no, row["placed_at"]
                order.status, order.customerId = OrderStatus.PENDING_PAYMENT, customer.id

                for it in order.items:                                         # (2) dòng đơn
                    it.id = self.con.execute(
                        'INSERT INTO "tblOrderItem"("quantity","unit_price","discount","line_total",'
                        '"orderId","productVariantId") VALUES (%s,%s,%s,%s,%s,%s) RETURNING "id"',
                        (it.quantity, it.unit_price, it.discount, it.line_total, order.id,
                         it.productVariantId)).fetchone()["id"]

                for v in getattr(order, "vouchers", []):                       # (3) voucher
                    n = self.con.execute(
                        'UPDATE "tblVoucher" SET "used_count" = "used_count" + 1 '
                        'WHERE "id" = %s AND "used_count" < "usage_limit"', (v.id,)).rowcount
                    if n != 1:
                        raise _Abort("voucher_used_up")
                    self.con.execute('INSERT INTO "tblOrderVoucher"("orderId","voucherId") VALUES (%s,%s)',
                                     (order.id, v.id))

                if not StockLevelDAO().reserve_stock(order):                   # (4) giữ hàng
                    raise _Abort("out_of_stock")

                by_location: dict[int, list[OrderItem]] = {}                # (5) tách kiện
                for it in order.items:
                    loc = self.con.execute('SELECT "stockLocationId" FROM "tblStockLevel" '
                                           'WHERE "productVariantId" = %s', (it.productVariantId,)).fetchone()
                    by_location.setdefault(loc["stockLocationId"], []).append(it)
                for loc_id, items in by_location.items():
                    sid = self.con.execute(
                        'INSERT INTO "tblShipment"("direction","service_level","fee","status","orderId",'
                        '"stockLocationId") VALUES (\'outbound\',%s,%s,\'requested\',%s,%s) RETURNING "id"',
                        (_val(order.delivery_service), order.shipping_fee if loc_id == next(iter(by_location)) else 0,
                         order.id, loc_id)).fetchone()["id"]
                    for it in items:
                        self.con.execute('INSERT INTO "tblShipmentRecord"("quantity","shipmentId","orderItemId") '
                                         'VALUES (%s,%s,%s)', (it.quantity, sid, it.id))

                cart = CartDAO().get_cart_by_customer(customer)                # (6) xoá giỏ
                CartDAO().clear_cart(cart)
            return True
        except (_Abort, psycopg.errors.CheckViolation, psycopg.errors.UniqueViolation):
            order.id = None
            return False


class _Abort(Exception):
    """Ném trong khối transaction để rollback có chủ đích."""
```

**Mã mẫu `StockLevelDAO.reserve_stock`:**

```python
def reserve_stock(self, order: Order) -> bool:
    need: dict[int, int] = {}
    for it in order.items:
        need[it.productVariantId] = need.get(it.productVariantId, 0) + it.quantity
    with self.con.transaction():                           # savepoint nếu đang trong add_order
        rows = self.con.execute(
            'SELECT "id","productVariantId","available" FROM "tblStockLevel" '
            'WHERE "productVariantId" = ANY(%s) ORDER BY "productVariantId" FOR UPDATE',
            (list(need),)).fetchall()
        if len(rows) != len(need) or any(r["available"] < need[r["productVariantId"]] for r in rows):
            return False
        for r in rows:
            q = need[r["productVariantId"]]
            self.con.execute('UPDATE "tblStockLevel" SET "reserved" = "reserved" + %s, '
                             '"available" = "available" - %s WHERE "id" = %s', (q, q, r["id"]))
    return True
```

> Đoạn `add_order` + `reserve_stock` + `dao.py` ở trên đã được chạy thử trên PostgreSQL với các bảng liên quan: đơn có hàng ở 2 kho tạo đúng 2 kiện và giữ đúng số lượng; voucher hết lượt trả `False` và không để lại dòng nào; hai tiến trình cùng mua món cuối cùng — 5/5 lần chỉ một đơn thành công, `reserved = 1`, `available = 0`.

> `return False` bên trong `with transaction()` vẫn **commit** savepoint (không có lỗi). Ở đây chưa ghi gì trước khi trả `False` nên an toàn; `add_order` sau đó ném `_Abort` để rollback cả đơn.

### 9.4. Tính tiền, phí vận chuyển, voucher (UC26, UC30)

Thực hiện trong `CheckoutFrm._recalc()` (hàm riêng tư) — đây là "phép tính thuần", có thể đặt thành hàm thuần của model nếu muốn kiểm thử độc lập.

| Đại lượng | Công thức | Ràng buộc CSDL |
|---|---|---|
| `item.unit_price` | giá biến thể lúc đặt (nếu có khuyến mãi tự động theo style thì giá sau giảm) | — |
| `item.discount` | phần giảm của voucher phân bổ cho dòng | ≥ 0 |
| `item.line_total` | `quantity × unit_price − discount` | CHECK |
| `order.subtotal` | `Σ quantity × unit_price` | — |
| `order.discount` | `Σ item.discount` | — |
| `order.shipping_fee` | theo `delivery_service` và số kiện; đề xuất STANDARD 30.000 đ, EXPRESS 50.000 đ, miễn phí khi `subtotal − discount ≥ 500.000 đ` (giả định — cấu hình trong một hằng số của Frm) | — |
| `order.grand_total` | `subtotal − discount + shipping_fee` | CHECK |

Phân bổ giảm giá voucher (giữ tổng chính xác đến từng đồng):

```python
def _apply_discount(items, eligible_style_ids: set[int], amount: int) -> None:
    elig = [i for i in items if i.styleId in eligible_style_ids]
    base = sum(i.quantity * i.unit_price for i in elig)
    amount = min(amount, base)
    left = amount
    for k, i in enumerate(elig):
        share = left if k == len(elig) - 1 else amount * i.quantity * i.unit_price // base
        i.discount = (i.discount or 0) + share
        left -= share
    for i in items:
        i.line_total = i.quantity * i.unit_price - (i.discount or 0)
```

Kiểm tra voucher hợp lệ (theo thứ tự, mỗi lỗi một thông báo): tồn tại → chương trình `active` → `starts_at ≤ now < ends_at` → `used_count < usage_limit` → `subtotal ≥ min_order_value` → giỏ có style của chương trình → chưa áp dụng mã này. `used_count` được kiểm tra **lại** trong `add_order` dưới khoá vì có thể đã hết lượt giữa lúc áp dụng và lúc đặt.

### 9.5. Thanh toán và xác nhận (UC31, BR2)

- Thanh toán **thành công**: `PaymentDAO.add_payment(status=SUCCEEDED)` → `order.status = CONFIRMED` → `OrderDAO.update_order_status` **[T]**: với mỗi dòng `on_hand −= q`, `reserved −= q` (available không đổi) và INSERT `StockMovement(quantity_change = −q, reason = 'sale', reference = order_no)`.
- **COD**: không gọi cổng thanh toán; xác nhận ngay như trên. Bản ghi `Payment` (kind charge, method cod, status pending) được tạo để thu khi giao — xem mục 13 về cột `paymentMethodId`.
- **Thất bại** (UC08 E2): `PaymentDAO.add_payment(status=FAILED)`, đơn giữ `pending_payment`, hàng vẫn được giữ; `ConfirmOrderFrm.on_retry_payment` thử lại (có thể bằng phương thức khác).
- Đơn `pending_payment` quá hạn (ví dụ 30 phút): huỷ bằng `OrderDAO.cancel_order` để nhả hàng. Có thể chạy khi khởi động ứng dụng hoặc bằng một tác vụ định kỳ — `cancel_order` tự nhận biết trường hợp chưa trừ `on_hand`.

### 9.6. Huỷ đơn (UC10, UC23)

| Trạng thái đơn | Khách (`CancelRequestFrm.on_send`) | Quản lý (`ManageOrderFrm`) |
|---|---|---|
| `pending_payment` | huỷ ngay: `cancel_order` nhả `reserved` | huỷ |
| `confirmed` | huỷ ngay: `cancel_order` cộng lại `on_hand` + sổ kho; hoàn tiền | huỷ + hoàn tiền |
| `processing` | gửi yêu cầu: lưu `cancel_reason`, chờ duyệt | `on_approve_cancel_request` → như `confirmed` |
| `partially_shipped` trở đi | không huỷ được → gợi ý trả hàng | không huỷ (theo máy trạng thái) |

Hoàn tiền: `PaymentGateway.refund(payment)` → `PaymentDAO.add_payment(kind=REFUND, amount = đã thu ròng)` → thông báo `REFUND_COMPLETED`.

### 9.7. Giao hàng và theo dõi (UC11, UC22, UC28)

1. `ManageOrderFrm.on_update_status` `confirmed → processing` (đóng gói).
2. Với mỗi kiện `requested`: `ShippingGateway.create_shipment` → `carrier`, `tracking_no` → `ShipmentDAO.update_shipment(status=PICKED_UP)`.
3. Trạng thái đơn tính từ các kiện `outbound`: có kiện đã đi và còn kiện chưa đi → `partially_shipped`; tất cả đã đi → `shipped`; tất cả `delivered` → `delivered` (đặt `delivered_at` từng kiện). Mỗi lần đổi gọi `OrderDAO.update_order_status` và gửi thông báo tương ứng.
4. Khách xem ở `TrackShipmentFrm`; `on_refresh` lấy sự kiện mới qua `ShippingGateway.get_tracking` → `ShipmentDAO.add_shipment_event` (cập nhật `Shipment.status`).
5. Khách bấm "Đã nhận hàng" (UC12) → `completed`.

### 9.8. Đánh giá (UC13, UC34, UC19, UC33)

`OrderDetailFrm.on_review` → `ReviewFrm.on_submit`: `ReviewDAO.is_reviewed` → `AssistantEngine.moderate(review)` → `APPROVED` (đăng ngay) hoặc `PENDING` (chờ `ManageReviewFrm` duyệt) → `ReviewDAO.add_review`. Đánh giá `approved` hiện ở `StyleDetailFrm` và được `AssistantEngine.summarise_reviews` tóm tắt.

### 9.9. Trả / đổi hàng (UC14, UC18) — luồng L2

```
Khách     OrderDetailFrm.on_return → ReturnRequestFrm.on_submit → ReturnRequestDAO.add_return_request [T]
                                                                   status = requested
CSKH      SearchReturnRequestFrm → ProcessReturnFrm
            on_authorise / on_reject → update_return_request          requested → authorised | rejected
            on_create_pickup → ShipmentDAO.add_shipment(direction=return) → ShippingGateway.create_shipment
                                                                       authorised → in_transit
Kho       SearchReturnRequestFrm → InspectReturnFrm
            on_save_inspection → update_return_item (passed / failed)
            on_finish [T] → StockLevelDAO.adjust_stock(+q, reason=return) cho dòng passed
                                                                       in_transit → inspected
CSKH      ProcessReturnFrm
            on_refund  → PaymentGateway.refund → PaymentDAO.add_payment(refund)   inspected → refunded
            on_ship_replacement → adjust_stock(−q, sale) + add_shipment(outbound, returnRequestId)
                                                                       inspected → exchanged
            on_close                                                   refunded | exchanged | rejected → closed
```

Số tiền hoàn của một dòng `passed` = `quantity_trả × unit_price − discount_dòng × quantity_trả / quantity_mua` (làm tròn xuống đồng), không vượt số đã thu ròng của đơn.

### 9.10. Kho và nhập hàng (UC17, UC25) — luồng L4

- **Điều chỉnh**: `StockLevelFrm.on_adjust` → `AdjustStockFrm.on_save` → `StockLevelDAO.adjust_stock(level, movement(reason=adjustment))` **[T]** + nhật ký `ADJUST_STOCK`.
- **Lập phiếu**: `ManageRestockFrm.on_create` → `EditRestockRequestFrm` (`on_add_item` → `SelectVariantFrm`) → `on_send` → `RestockRequestDAO.add_restock_request` (`sent`).
- **Nhà cung cấp**: `SupplierHomeFrm.on_open` → `ConfirmRestockFrm.on_confirm` (`confirmed`, ngày dự kiến) hoặc `on_refuse` (`cancelled`, lý do).
- **Nhận hàng**: `ManageRestockFrm.on_mark_received` → `RestockRequestDAO.receive_restock_request` **[T]** (+`on_hand`, sổ kho `restock`, `received`).
- Báo cáo hàng sắp hết: `StockLevelFrm` với `chk_below_reorder_point`.

### 9.11. Sản phẩm (UC21) — luồng L5

`ManageStyleFrm` → `EditStyleFrm.on_save` **[T]** (`add_style`/`update_style` + `save_material` + `save_size_chart` + nhật ký) → `on_add_variant` → `EditVariantFrm.on_save` **[T]** (`add_variant` + `add_stock_level`). Style mới ở `draft`; chuyển `active` khi đủ vật liệu (tổng 100%) và có ít nhất một biến thể. Ngừng bán: `deactivate_style` (`inactive`).

### 9.12. Khuyến mãi (UC15, UC27)

`ManagePromotionFrm` → `EditPromotionFrm`: `on_add_style` (`SelectStyleFrm`), `on_save` (`add_promotion`/`update_promotion` **[T]** với `PromotionStyle`), `on_add_voucher` (`VoucherDAO.add_voucher`). `on_end` → `ended`. Chương trình `active` trong thời gian hiệu lực được `PromotionDAO.get_active_promotion_by_style` dùng ở trang sản phẩm và được kiểm tra khi áp voucher.

### 9.13. Báo cáo (UC16, UC24)

`SelectReportFrm` → `SalesReportFrm.on_view` (`StyleStatDAO.get_style_stat`) → `on_open_detail` → `SalesDetailFrm` (`OrderItemDAO.get_order_item_by_style`); `on_export` ra CSV. Tương tự `ReturnReportFrm` / `ReturnDetailFrm` với `ReturnStatDAO`, `ReturnItemDAO`. Chỉ tính đơn không bị huỷ và yêu cầu trả không bị từ chối.

### 9.14. Tìm kiếm, trợ lý AI (UC05, UC32, UC33) — luồng L3

- Chữ: `StyleDAO.search_style`.
- Ảnh / giọng nói: `SearchEngine.search_by_image/voice` → danh sách id style theo độ phù hợp → `StyleDAO.search_style_by_ids` (giữ thứ tự).
- Trợ lý: `AssistantFrm.on_ask` → `AssistantEngine.ask(question, style)` → câu trả lời đã kiểm chứng với dữ liệu thật (giá, tồn kho, chất liệu, bảng cỡ); các câu bị loại được ghi `GroundingEvent` → `AssistantTurnDAO.add_assistant_turn` **[T]**. Câu hỏi được che e-mail, số điện thoại trước khi lưu và trước khi gửi cho mô hình (NFR16).

### 9.15. Quản trị tài khoản (UC20)

`AdminHomeFrm.on_manage_account` → `SearchAccountFrm.on_search` (`UserDAO.search_user`) → `EditAccountFrm`: khoá/mở (`update_user_status`), đặt lại mật khẩu (`reset_password`), đổi vai trò (`StaffMemberDAO.update_role`); mọi thao tác ghi `AuditLogEntryDAO.add_audit_log_entry`. `AuditLogFrm` xem lại nhật ký.

---

## 10. Máy trạng thái

Mỗi `update_…_status` kiểm tra chuyển trạng thái bằng bảng dưới và câu `UPDATE … WHERE "status" = <cũ>` (nếu `rowcount = 0` → người khác vừa đổi → trả `False`). Nên đặt các bảng này thành hằng số dùng chung (ví dụ trong `model/sales.py` sau các enum, vì đây là quy tắc thuần của dữ liệu).

### 10.1. Đơn hàng — `OrderStatus`

```python
ORDER_NEXT = {
    OrderStatus.PENDING_PAYMENT:   {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED:         {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING:        {OrderStatus.PARTIALLY_SHIPPED, OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.PARTIALLY_SHIPPED: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED:           {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED:         {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(), OrderStatus.CANCELLED: set(),
}
```

| Chuyển | Ai / khi nào | Tác động phụ |
|---|---|---|
| → `pending_payment` | `add_order` | giữ hàng (`reserved`), tạo kiện `requested` |
| `pending_payment → confirmed` | thanh toán thành công / COD | trừ `on_hand`, nhả `reserved`, sổ kho `sale`; thông báo `ORDER_CONFIRMED` |
| `confirmed → processing` | quản lý | — |
| `processing → partially_shipped / shipped` | kiện được giao cho hãng | thông báo `ORDER_SHIPPED` |
| `shipped → delivered` | mọi kiện đã giao | `delivered_at`; thông báo `ORDER_DELIVERED`; bắt đầu tính hạn trả |
| `delivered → completed` | khách xác nhận (UC12) hoặc tự động sau hạn trả | — |
| `* → cancelled` | `cancel_order` | trả hàng về kho, trả lượt voucher, hoàn tiền; thông báo `ORDER_CANCELLED` |

### 10.2. Yêu cầu trả — `ReturnStatus`

`requested → authorised | rejected`; `authorised → in_transit`; `in_transit → inspected`; `inspected → refunded | exchanged`; `refunded | exchanged | rejected → closed`. Quá hạn trả (30 ngày sau `delivered_at` — giả định cần ABC Fashion xác nhận) thì `authorise` tự chuyển `rejected` (UC18 E2).

### 10.3. Phiếu nhập hàng — `RestockStatus`

`draft → sent → confirmed → received`; `sent → cancelled` (nhà cung cấp từ chối); `draft → cancelled` (nhân viên huỷ nháp).

### 10.4. Các trạng thái khác

| Enum | Chuyển |
|---|---|
| `ReviewStatus` | `pending → approved / rejected`; khi tạo có thể là `approved` ngay (kiểm duyệt tự động đạt) |
| `ShipmentStatus` | `requested → picked_up → in_transit → delivered`; bất kỳ → `failed` |
| `PaymentStatus` | `pending → succeeded / failed` (chỉ một lần) |
| `PromotionStatus` | `draft → active → ended` |
| `StyleStatus` | `draft → active ⇄ inactive` |
| `VariantStatus` | `active → discontinued` |
| `AccountStatus` | `active ⇄ suspended` |
| `NotificationStatus` | `queued → sent / failed` |
| `InspectionResult` | `pending → passed / failed` |

---

## 11. Transaction và xử lý đồng thời

| Thao tác | Bảng được ghi cùng nhau | Khoá |
|---|---|---|
| `CustomerDAO.add_customer` | User, Customer, Cart | — |
| `OrderDAO.add_order` | Order, OrderItem, Voucher, OrderVoucher, StockLevel, Shipment, ShipmentRecord, CartItem | `Voucher` (UPDATE có điều kiện), `StockLevel FOR UPDATE` |
| `OrderDAO.update_order_status` (→ confirmed) | Order, StockLevel, StockMovement | `StockLevel FOR UPDATE` |
| `OrderDAO.cancel_order` | Order, StockLevel, StockMovement, Voucher, Shipment | như trên |
| `StockLevelDAO.adjust_stock` | StockLevel, StockMovement | `FOR UPDATE` dòng tồn |
| `RestockRequestDAO.receive_restock_request` | StockLevel, StockMovement, RestockRequest | `FOR UPDATE` |
| `ReturnRequestDAO.add_return_request` | ReturnRequest, ReturnItem, ReturnEvidence | UNIQUE `orderId` |
| `InspectReturnFrm.on_finish` (Frm mở transaction) | ReturnItem, StockLevel, StockMovement, ReturnRequest | `FOR UPDATE` |
| `EditStyleFrm.on_save` (Frm mở transaction) | Style, MaterialComponent, SizeChartEntry, AuditLogEntry | — |
| `EditVariantFrm.on_save` (Frm mở transaction) | ProductVariant, StockLevel | — |
| `PromotionDAO.add/update_promotion` | Promotion, PromotionStyle | — |
| `AssistantTurnDAO.add_assistant_turn` | AssistantTurn, GroundingEvent | — |

Quy tắc:

1. **Khoá theo thứ tự cố định** (`ORDER BY "productVariantId"`) để hai đơn chạy song song không deadlock.
2. **Không gọi gateway bên trong transaction** (cổng thanh toán có thể chậm hàng giây, khoá sẽ bị giữ lâu). Thứ tự đúng: transaction tạo đơn → commit → gọi `charge` → transaction ghi thanh toán và xác nhận.
3. Frm cần gộp nhiều DAO thì mở transaction trên kết nối chung: `with DAO._shared.transaction(): …` (hoặc `with self.style_dao.con.transaction():`). Đây là chỗ duy nhất view "biết" về transaction; không viết SQL ở view.
4. **Chống ghi đè đồng thời**: mọi UPDATE trạng thái kèm điều kiện trạng thái cũ.
5. **Idempotent**: callback thanh toán lặp lại không đổi gì (`UPDATE … WHERE "status" = 'pending'`).
6. **Kết nối chung chỉ dùng trong một luồng**: luồng phụ (gọi AI, cổng thanh toán) chỉ gọi gateway rồi trả kết quả về luồng giao diện bằng `after()`; mọi lời gọi DAO thực hiện ở luồng giao diện. Không chia sẻ kết nối giữa các tiến trình (fork).
7. CSDL là hàng rào cuối: CHECK `reserved ≤ on_hand`, `available = on_hand − reserved`, `used_count ≤ usage_limit`, các công thức tổng tiền — vi phạm sẽ ném `CheckViolation`, DAO bắt và trả `False`.

---

## 12. Công cụ sinh mã và kiểm tra

### 12.1. `vp2py.py` — sinh mã từ mô hình Visual Paradigm

```bash
# trong Visual Paradigm: Project > Export > XML  → project.xml
python vp2py.py project.xml out_dir
```

| Phần / hàm | Việc làm |
|---|---|
| `prop(m, name)`, `sval`, `tval`, `ftype` | Đọc thuộc tính của một phần tử XML: giá trị chuỗi, kiểu (`StringValue` hoặc tham chiếu `ModelRef`), kiểu kèm `typeModifier` (`list` + `[Address]` → `list[Address]`) |
| `kids(m, t)`, `stereos(m)` | Phần tử con theo loại (Attribute, Operation, Parameter, EnumerationLiteral); danh sách stereotype |
| khối "owner of each attribute" | Phát hiện thuộc tính bị liệt kê dưới hai lớp (đã gặp: `quantity_sold`, `revenue` dưới cả `Review` và `StyleStat`); `OWNER_FIX` bỏ chúng khỏi `Review` |
| `walk(pkg, path)` | Duyệt cây package `abc_fashion` → mỗi lớp nhớ đường dẫn package (`['view','checkout']`) |
| `is_enum(c)` | Lớp có literal hoặc stereotype «enumeration» |
| khối "relationships" | Đọc Generalization (`from` = lớp cha) → `supers`; Association (FromEnd/ToEnd, `aggregationKind`, `multiplicity`) → `assocs` |
| `entity_name`, `fix_type` | Đổi tên kiểu theo tên phân tích (`Order`) sang entity (`Order`); chuẩn hoá `list[...]`, `X \| None` |
| `names_in`, `imports_for` | Tìm các lớp được dùng trong kiểu → sinh `from … import …` đúng module (nhờ vậy import luôn theo package dependency) |
| `snake(n)` | `CheckoutFrm` → `checkout_frm` (tên module) |
| `params(op)`, `attrs_of(c, name)`, `doc(name, extra)` | Chữ ký hàm, danh sách thuộc tính, docstring (stereotype, layer, Uses / Opens / Holds / Relationships) |
| khối "model layer" | Mỗi package model → một module: enum trước, entity sau, lớp cha trước lớp con; entity là `@dataclass(kw_only=True)` với trường `= None` |
| khối "control and view layers" | Mỗi lớp → một module; Frm kế thừa `tk.Toplevel`, `__init__` gán tham số và tạo DAO/gateway theo association; `DAO.__init__` mở `psycopg.connect(DSN)` |
| `files['abc_fashion.main']` | Sinh `main.py` mở `LoginFrm` |
| khối "write" | Ghi file, tạo `__init__.py` cho mọi package; in thống kê |
| `STATS=1` | In thêm số quan hệ theo layer, package, component, interface (dùng cho bảng 4.18 của báo cáo) |

### 12.2. `check_gen.py` — kiểm tra mã

```bash
python check_gen.py <thư mục chứa abc_fashion>
```

1. Thay `tkinter` bằng module giả nếu máy không có màn hình.
2. Import **mọi** module (bắt lỗi cú pháp, import sai, vòng import).
3. Đọc câu lệnh import bằng `ast` và kiểm tra quy tắc layer (mục 2.2), cả `psycopg` chỉ trong `control` và `tkinter` chỉ trong `view`.
4. Đếm lớp theo layer, enum, operation để so với mô hình (53 / 34 / 5 / 41 / 34 enum / 329 operation).

Nên chạy lại sau mỗi lần sửa mã và đưa vào bộ kiểm thử (`pytest`).

### 12.3. Sửa thiết kế khi đã có mã thân hàm

Sinh lại sẽ **ghi đè** file. Quy trình an toàn:

1. Sửa mô hình trong VP → xuất XML → `python vp2py.py project.xml /tmp/gen_new`.
2. So sánh (`git diff --no-index code/abc_fashion /tmp/gen_new/abc_fashion` hoặc công cụ merge) và chỉ đưa sang **chữ ký / import / lớp mới**, giữ thân hàm đã viết.
3. Chạy `check_gen.py` và kiểm thử.

Dùng git cho thư mục `code/` từ trước khi bắt đầu lập trình.

---

## 13. Các điểm thiết kế cần bổ sung khi lập trình

Phân tích mô hình, mã sinh và CSDL cho thấy các chỗ sau chưa khớp hoặc còn thiếu. Mỗi dòng nêu cách xử lý đề xuất; với thay đổi mô hình, sửa trong VP rồi sinh lại để báo cáo và mã vẫn khớp.

| # | Vấn đề | Ảnh hưởng | Đề xuất |
|---|---|---|---|
| 1 | Bảng `Review` trong CSDL còn cột `verified_purchase`, `origin` với `CHECK (verified_purchase)`, `CHECK (origin = 'customer')`, trong khi mô hình đã bỏ | INSERT không ghi hai cột → vi phạm CHECK nếu cột NOT NULL/không có default | Chạy: `ALTER TABLE "tblReview" DROP COLUMN "verified_purchase", DROP COLUMN "origin";` (CHECK đi kèm tự mất). Nếu chưa muốn đổi CSDL: INSERT thêm `true, 'customer'` |
| 2 | Kiểu trả về không có trong chữ ký sinh ra | IDE không gợi ý, dễ nhầm | Thêm `-> bool`, `-> list[X]`… theo mục 7.3 (hoặc ghi Return Type trong VP) |
| 3 | `DAO.__init__` mở một kết nối / đối tượng | nhiều kết nối, không gộp được transaction | Dùng kết nối chung như mục 7.1 |
| 4 | `Order` không có địa chỉ giao hàng | không biết giao đi đâu; sửa sổ địa chỉ làm sai đơn cũ | Thêm cột chụp địa chỉ vào `Order` (`ship_recipient`, `ship_phone`, `ship_address`) hoặc `addressId` vào `Shipment`; cập nhật mô hình, ERD, DAO |
| 5 | `Payment.paymentMethodId` bắt buộc (1 : 0..*) nhưng COD / chuyển khoản không có phương thức liên kết | không lưu được thanh toán COD | Cho cột NULL: `ALTER TABLE "tblPayment" ALTER COLUMN "paymentMethodId" DROP NOT NULL;` |
| 6 | `LoginFrm` chỉ liên kết `UserDAO`, nhưng cần biết loại người dùng | chưa mở đúng home | Thêm association `LoginFrm → CustomerDAO, StaffMemberDAO, SupplierDAO` (mã ở mục 9.1) |
| 7 | Vai trò `StaffRole.SALES` không có màn hình home | nhân viên SALES đăng nhập không vào được | Gán tạm `MarketingHomeFrm` (xem báo cáo) hoặc bỏ vai trò / thêm `SalesHomeFrm` |
| 8 | Một số home chỉ có association tới một màn hình (vd. `AdminHomeFrm` → `SearchAccountFrm`) trong khi handler mở nhiều màn hình; `RegisterFrm` lại có association tới `AdminHomeFrm`; `EditAccountFrm` tới `AuditLogFrm` | sơ đồ điều hướng trong mô hình chưa đủ / có liên kết thừa | Lập trình theo handler (mục 8.2); bổ sung / xoá association trong VP cho khớp |
| 9 | Một số Frm cần DAO không có trong association: `StyleDetailFrm` (MaterialComponentDAO, SizeChartEntryDAO), `OrderDetailFrm` (ReturnRequestDAO, ReviewDAO), `ConfirmOrderFrm` (OrderDAO), `ManageRestockFrm` (SupplierDAO), `AuditLogFrm` (StaffMemberDAO), `EditAccountFrm` (AuditLogEntryDAO), `ProcessReturnFrm` (StockLevelDAO khi đổi hàng), `ManageStyleFrm`/`SelectStyleFrm` (CategoryDAO) | thiếu dữ liệu để hiển thị / ghi nhật ký | Tạo thêm đối tượng DAO trong `__init__` (được phép), rồi bổ sung association trong VP |
| 10 | Thuộc tính kiểu `DateEntry` không được import | `NameError` khi tạo widget | `from tkcalendar import DateEntry` trong các Frm có `dte_` |
| 11 | `main.py` gọi `LoginFrm().mainloop()` trên một `Toplevel` | hiện thêm cửa sổ "tk" trống | Dùng cửa sổ gốc ẩn (mục 9.1) |
| 12 | Mô hình chưa có trạng thái "khách yêu cầu huỷ" | khó phân biệt đơn có yêu cầu huỷ | Dùng `cancel_reason IS NOT NULL AND status <> 'cancelled'` (mục 9.6), hoặc thêm cột / trạng thái `cancel_requested` |
| 13 | Không có hàm tạo mã `order_no`, `return_no`, `request_no` | — | Sinh trong DAO (mẫu ở 9.3) hoặc dùng `SEQUENCE` của PostgreSQL |
| 14 | `Customer.preferred_colours` là `list[str]` trong model nhưng `varchar(255)` trong CSDL | lỗi kiểu khi ghi | Nối/tách bằng dấu phẩy trong `CustomerDAO` |
| 15 | Mật khẩu dữ liệu mẫu có thể là bản rõ | `_check_password` phải chấp nhận cả hai | Dùng hàm ở mục 7.1; khi người dùng đăng nhập thành công bằng bản rõ thì băm lại và lưu |
| 16 | Báo cáo 4.3 ghi 39 entity / 35 enum, mô hình hiện có 41 / 34 | lệch số liệu trong báo cáo | Sửa câu ở 4.3.2 |

---

## 14. Lộ trình triển khai và kiểm thử

### 14.1. Thứ tự lập trình đề xuất

| Bước | Việc | Xong khi |
|---|---|---|
| 1 | Sửa CSDL theo mục 13 (#1, #5, #4 nếu chọn) | `\d "tblReview"` không còn cột cũ |
| 2 | `dao.py` (kết nối chung + tiện ích) | `DAO().con.execute("select 1")` chạy |
| 3 | Account: UserDAO, CustomerDAO, StaffMemberDAO, SupplierDAO; LoginFrm, RegisterFrm, 7 home Frm | đăng nhập được bằng mọi vai trò, đăng xuất quay lại |
| 4 | Catalogue: CategoryDAO, StyleDAO, ProductVariantDAO, ProductMediaDAO, StockLevelDAO (đọc), ReviewDAO (đọc), PromotionDAO (đọc); BrowseStyleFrm, SearchStyleFrm (chữ), StyleDetailFrm | xem được 4 style mẫu và 8 biến thể |
| 5 | Giỏ + đặt hàng: CartDAO, VoucherDAO, OrderDAO.add_order, reserve_stock, PaymentDAO, NotificationDAO, gateway sandbox; CartFrm, CheckoutFrm, ConfirmOrderFrm | đặt được đơn tách 2 kiện, tồn kho đúng |
| 6 | Đơn của khách: OrderListFrm, OrderDetailFrm, TrackShipmentFrm, CancelRequestFrm | huỷ đơn trả lại kho |
| 7 | Quản lý đơn: SearchOrderFrm, ManageOrderFrm, ShipmentDAO | đi hết vòng đời đơn tới `completed` |
| 8 | Hồ sơ: ProfileFrm, EditAddressFrm, LinkPaymentMethodFrm | |
| 9 | Trả hàng: ReturnRequestFrm, SearchReturnRequestFrm, ProcessReturnFrm, InspectReturnFrm | hoàn tiền đúng số, hàng về kho |
| 10 | Đánh giá: ReviewFrm, ManageReviewFrm | |
| 11 | Kho & nhập hàng: StockLevelFrm, AdjustStockFrm, StockMovementFrm, ManageRestockFrm, EditRestockRequestFrm, SelectVariantFrm, SupplierHomeFrm, ConfirmRestockFrm | sổ kho khớp tồn |
| 12 | Sản phẩm, khuyến mãi | |
| 13 | Báo cáo, quản trị tài khoản, nhật ký | |
| 14 | AI: SearchEngine, AssistantEngine thật (Chương 3), AssistantFrm | chế độ cơ bản khi không có mô hình |

### 14.2. Kiểm thử

**Tự động (pytest, CSDL thử riêng `abc_fashion_test` tạo từ cùng script DDL + seed):**

| Nhóm | Ca kiểm thử |
|---|---|
| Cấu trúc | `check_gen.py`: 104 module import được, 0 vi phạm layer |
| UserDAO | đúng / sai mật khẩu; tài khoản `suspended` bị từ chối; `is_email_used` không phân biệt hoa thường |
| CustomerDAO | đăng ký tạo đủ 3 dòng; trùng e-mail trả `False` và không để lại dòng nào |
| StockLevelDAO | `check_availability` trả đúng dòng thiếu; `reserve_stock` đủ / thiếu; `adjust_stock` không cho âm |
| OrderDAO.add_order | đơn 1 kho → 1 kiện; 2 kho → 2 kiện; voucher hết lượt → `False`, không còn dòng nào; giỏ được xoá |
| Đồng thời | hai luồng cùng đặt món cuối cùng → đúng một đơn thành công (dùng hai kết nối riêng) |
| Tiền | `line_total`, `grand_total` thoả CHECK; phân bổ giảm giá cộng lại đúng `order.discount` |
| Trạng thái | mọi chuyển sai trong `ORDER_NEXT` bị từ chối; huỷ sau khi giao bị từ chối |
| Trả hàng | yêu cầu thứ hai cho cùng đơn bị từ chối (UNIQUE); số hoàn đúng khi có giảm giá; hàng FAILED không về kho |
| Sổ kho | sau mỗi kịch bản: `Σ quantity_change` theo biến thể = `on_hand` (đối soát) |

**Thủ công (kịch bản trình diễn):** khách đăng ký → tìm "áo" → thêm 2 biến thể ở 2 kho → áp voucher → thanh toán thẻ thử thất bại rồi thanh toán lại → quản lý giao 2 kiện → khách xác nhận nhận → đánh giá → yêu cầu trả 1 món → CSKH duyệt, tạo kiện lấy → kho kiểm tra đạt → CSKH hoàn tiền → báo cáo doanh số và trả hàng hiện số liệu đúng.

### 14.3. Danh sách kiểm tra trước khi nộp

- [ ] Không còn `raise NotImplementedError` ở các luồng được trình diễn.
- [ ] `check_gen.py` vẫn 0 vi phạm sau khi thêm import.
- [ ] Không có câu SQL ghép chuỗi từ dữ liệu người dùng.
- [ ] Không lưu số thẻ đầy đủ, mật khẩu bản rõ.
- [ ] Mọi thay đổi tồn kho có dòng `StockMovement`.
- [ ] Khách không mở được đơn của người khác.
- [ ] Mọi lỗi CSDL hiện thông báo, ứng dụng không tắt.
- [ ] Chữ ký hàm vẫn khớp mô hình (so bằng `vp2py.py` sinh lại vào thư mục tạm).

---

## 15. Phụ lục — Use case → màn hình → DAO

| Use case | Màn hình | DAO; gateway | Mục |
|---|---|---|---|
| UC01 Đăng ký | RegisterFrm | UserDAO, CustomerDAO | 9.2 |
| UC02 Đăng nhập | LoginFrm, 7 home Frm | UserDAO, CustomerDAO, StaffMemberDAO, SupplierDAO | 9.1 |
| UC03 Quản lý hồ sơ | ProfileFrm, EditAddressFrm, LinkPaymentMethodFrm | CustomerDAO, AddressDAO, PaymentMethodDAO, SavedSizeDAO; PaymentGateway | 8.3 |
| UC04 Duyệt danh mục | BrowseStyleFrm | CategoryDAO, StyleDAO | 8.3 |
| UC05 Tìm kiếm | SearchStyleFrm | StyleDAO; SearchEngine | 9.14 |
| UC06 Xem chi tiết, UC33 Tóm tắt đánh giá | StyleDetailFrm | StyleDAO, ProductVariantDAO, ProductMediaDAO, StockLevelDAO, ReviewDAO, PromotionDAO; AssistantEngine | 9.14 |
| UC07 Giỏ hàng | StyleDetailFrm, CartFrm | CartDAO, StockLevelDAO | 9.3 |
| UC08 Đặt hàng, UC25, UC26, UC28–UC31 | CheckoutFrm, ConfirmOrderFrm | OrderDAO, VoucherDAO, StockLevelDAO, PaymentDAO, ShipmentDAO, NotificationDAO, CartDAO; PaymentGateway, NotificationGateway | 9.3–9.5 |
| UC09 Xem đơn | OrderListFrm, OrderDetailFrm | OrderDAO | 8.3 |
| UC10 Huỷ đơn | CancelRequestFrm, ManageOrderFrm | OrderDAO, PaymentDAO, StockMovementDAO; PaymentGateway | 9.6 |
| UC11 Theo dõi | TrackShipmentFrm | ShipmentDAO; ShippingGateway | 9.7 |
| UC12 Xác nhận đã nhận | OrderDetailFrm | OrderDAO | 9.7 |
| UC13 Đánh giá, UC34 Kiểm duyệt tự động | ReviewFrm | ReviewDAO; AssistantEngine | 9.8 |
| UC14 Yêu cầu trả / đổi | ReturnRequestFrm | ReturnRequestDAO | 9.9 |
| UC15 Khuyến mãi, UC27 | ManagePromotionFrm, EditPromotionFrm, SelectStyleFrm | PromotionDAO, VoucherDAO, StyleDAO | 9.12 |
| UC16, UC24 Báo cáo | SelectReportFrm, SalesReportFrm, SalesDetailFrm, ReturnReportFrm, ReturnDetailFrm | StyleStatDAO, ReturnStatDAO, OrderItemDAO, ReturnItemDAO | 9.13 |
| UC17 Kho và nhập hàng | StockLevelFrm, AdjustStockFrm, StockMovementFrm, ManageRestockFrm, EditRestockRequestFrm, SelectVariantFrm, SupplierHomeFrm, ConfirmRestockFrm | StockLevelDAO, StockLocationDAO, StockMovementDAO, RestockRequestDAO, ProductVariantDAO, SupplierDAO | 9.10 |
| UC18 Xử lý trả / đổi | SearchReturnRequestFrm, ProcessReturnFrm, InspectReturnFrm | ReturnRequestDAO, ShipmentDAO, PaymentDAO, StockLevelDAO, StockMovementDAO, NotificationDAO; PaymentGateway, ShippingGateway, NotificationGateway | 9.9 |
| UC19 Duyệt đánh giá | ManageReviewFrm | ReviewDAO | 9.8 |
| UC20 Quản lý tài khoản | SearchAccountFrm, EditAccountFrm, AuditLogFrm | UserDAO, StaffMemberDAO, AuditLogEntryDAO | 9.15 |
| UC21 Quản lý sản phẩm | ManageStyleFrm, EditStyleFrm, EditVariantFrm | StyleDAO, ProductVariantDAO, MaterialComponentDAO, SizeChartEntryDAO, ProductMediaDAO, CategoryDAO, CollectionDAO, SupplierDAO, StockLocationDAO, StockLevelDAO, AuditLogEntryDAO | 9.11 |
| UC22 Cập nhật trạng thái đơn, UC23 Huỷ đơn (quản lý) | SearchOrderFrm, ManageOrderFrm | OrderDAO, ShipmentDAO, PaymentDAO, StockMovementDAO, NotificationDAO; PaymentGateway, ShippingGateway, NotificationGateway | 9.7 |
| UC32 Hỏi trợ lý | AssistantFrm | AssistantTurnDAO; AssistantEngine | 9.14 |

### Giá trị enum (lưu trong CSDL)

| Enum | Module | Giá trị |
|---|---|---|
| `AssistantMode` | `model/assistant.py` | `model`, `basic` |
| `GroundingCheck` | `model/assistant.py` | `price`, `stock`, `fit`, `fabric`, `popularity`, `policy`, `health` |
| `AuditAction` | `model/audit.py` | `create`, `update`, `deactivate`, `adjust_stock`, `suspend_account`, `reset_password` |
| `FitType` | `model/catalogue.py` | `slim`, `regular`, `relaxed`, `oversized` |
| `Measure` | `model/catalogue.py` | `chest`, `waist`, `hip`, `length`, `sleeve`, `inseam`, `foot_length` |
| `MediaType` | `model/catalogue.py` | `image`, `video` |
| `Season` | `model/catalogue.py` | `spring_summer`, `autumn_winter`, `all_season` |
| `StyleStatus` | `model/catalogue.py` | `draft`, `active`, `inactive` |
| `VariantStatus` | `model/catalogue.py` | `active`, `discontinued` |
| `Channel` | `model/customer_data.py` | `email`, `sms`, `app` |
| `LinkedMethodType` | `model/customer_data.py` | `card`, `e_wallet`, `bank_account` |
| `NotificationEvent` | `model/customer_data.py` | `order_confirmed`, `order_shipped`, `order_delivered`, `order_cancelled`, `return_authorised`, `return_rejected`, `refund_completed`, `exchange_shipped` |
| `NotificationStatus` | `model/customer_data.py` | `queued`, `sent`, `failed` |
| `ShipmentDirection` | `model/fulfilment.py` | `outbound`, `return` |
| `ShipmentStatus` | `model/fulfilment.py` | `requested`, `picked_up`, `in_transit`, `delivered`, `failed` |
| `MovementReason` | `model/inventory.py` | `sale`, `return`, `restock`, `adjustment` |
| `RestockStatus` | `model/inventory.py` | `draft`, `sent`, `confirmed`, `received`, `cancelled` |
| `InspectionResult` | `model/returns.py` | `pending`, `passed`, `failed` |
| `Resolution` | `model/returns.py` | `refund`, `exchange` |
| `ReturnReason` | `model/returns.py` | `too_small`, `too_large`, `defect`, `wrong_item`, `not_as_described`, `changed_mind` |
| `ReturnStatus` | `model/returns.py` | `requested`, `authorised`, `rejected`, `in_transit`, `inspected`, `refunded`, `exchanged`, `closed` |
| `ReturnType` | `model/returns.py` | `return`, `exchange` |
| `FitVote` | `model/review.py` | `runs_small`, `true_to_size`, `runs_large` |
| `ReviewStatus` | `model/review.py` | `pending`, `approved`, `rejected` |
| `DeliveryService` | `model/sales.py` | `standard`, `express` |
| `DiscountType` | `model/sales.py` | `percent`, `fixed_amount` |
| `OrderStatus` | `model/sales.py` | `pending_payment`, `confirmed`, `processing`, `partially_shipped`, `shipped`, `delivered`, `completed`, `cancelled` |
| `PaymentKind` | `model/sales.py` | `charge`, `refund` |
| `PaymentMethodType` | `model/sales.py` | `cod`, `card`, `e_wallet`, `bank_transfer` |
| `PaymentStatus` | `model/sales.py` | `pending`, `succeeded`, `failed` |
| `PromoType` | `model/sales.py` | `seasonal`, `flash_sale`, `clearance`, `loyalty` |
| `PromotionStatus` | `model/sales.py` | `draft`, `active`, `ended` |
| `AccountStatus` | `model/user.py` | `active`, `suspended` |
| `StaffRole` | `model/user.py` | `administrator`, `manager`, `merchandiser`, `marketing`, `customer_service`, `warehouse`, `sales` |
