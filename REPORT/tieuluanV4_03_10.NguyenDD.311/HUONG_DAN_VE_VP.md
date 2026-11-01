# Hướng dẫn vẽ lại các diagram của Chương 4 bằng Visual Paradigm

Tài liệu này đi kèm bài tập `design_03_10_DongDucNguyen` (Đồng Đức Nguyên, B23DCVT311, lớp 03, nhóm 10).
Tất cả hình trong Chương 4 hiện là **bản nháp** sinh tự động bằng PlantUML từ đúng mô hình thiết kế
(`design/design_model.yaml`) và đúng cơ sở dữ liệu PostgreSQL đang chạy, nên nội dung đã khớp với code và DB.
Bạn chỉ cần vẽ lại bằng Visual Paradigm (VP) theo danh sách dưới đây, xuất ảnh PNG với **đúng tên file**
rồi chép đè vào thư mục `figures/` của bài LaTeX (hoặc gửi lại để mình thay vào và biên dịch lại).

## 1. Quy ước chung khi vẽ trong VP

**Thiết lập hiển thị (Diagram > Presentation Options, hoặc chuột phải vào nền diagram):**

- *Class diagram mức phân tích (4.1):* chỉ ghi tên thuộc tính, **không** kiểu dữ liệu, **không** phương thức,
  **không** dấu visibility (Show Attribute Type: off, Show Operations: off, Visibility Style: none).
  Thuộc tính dẫn xuất (ví dụ `/grandTotal`, `/lineTotal`) → mở Specification của thuộc tính, tích **Derived**.
- *Class diagram mức thiết kế (4.3) và theo tầng (4.4):* hiện kiểu dữ liệu, visibility (`-` private, `+` public),
  tham số và kiểu trả về của phương thức. Stereotype («entity», «service», «repository», «controller»,
  «gateway», «interface», «enumeration») đặt bằng chuột phải > Stereotypes.
- **Bội số (multiplicity):** đặt ở hai đầu association (chuột phải vào đầu mút > Multiplicity), đúng như cột
  "Bội số" trong các bảng.
- **Composition / Aggregation:** hình thoi nằm ở phía **lớp toàn thể** (cột "Từ" trong bảng).
- **Generalization / Realization:** kéo từ lớp con / lớp cài đặt đến lớp cha / interface.
- **Association có hướng:** trong Specification của association, đặt Navigable = true ở đầu được trỏ tới.
- **Dependency** (nét đứt mũi tên hở): dùng cho «use» và cho lớp → enumeration.
- **Enumeration:** dùng phần tử *Enumeration* của VP, liệt kê các literal (giá trị viết thường, trùng giá trị
  CHECK trong DB).
- **ERD (4.2):** dùng *Entity Relationship Diagram*. Cột khoá chính tích **Primary Key**; khoá ngoại vẽ bằng
  *One-to-Many Relationship* (hoặc One-to-One nếu bảng con có cột FK duy nhất). Cột không tích "Nullable" là NOT NULL.

**Mẹo tiết kiệm thời gian:**

1. **ERD:** VP có thể sinh ERD trực tiếp từ DB: *Tools > DB > Reverse Database*, chọn PostgreSQL, host
   `localhost`, port `5432`, database `abc_fashion`, user/password `abc`/`abc`, schema `abc`. Sau đó chỉ cần
   chia các bảng ra 5 diagram như danh sách ở mục 4.2 (kéo bảng có sẵn trong Model Explorer vào diagram).
   (Chạy `scripts/reset_db.sh` trước để có DB.)
2. **Class diagram mức thiết kế:** có thể dựng một lần trong Model Explorer rồi kéo cùng một lớp vào nhiều
   diagram (các diagram 4.4 dùng lại lớp của 4.3) — VP giữ một mô hình duy nhất, sửa một chỗ là cập nhật mọi hình.
3. Nếu bản VP của bạn có *Tools > Code > Instant Reverse* cho Python, có thể reverse thư mục `src/abc_fashion`
   để lấy sẵn các lớp; nhưng kiểu dữ liệu và quan hệ vẫn nên chỉnh theo bảng dưới đây.

**Xuất ảnh:** *Project > Export > Active Diagram as Image* (hoặc chuột phải vào nền > Export > Image),
định dạng **PNG**, nên chọn độ phân giải cao (≥ 150 DPI hoặc scale 200%), nền trắng, **không** thêm tiêu đề
vào hình (tiêu đề đã nằm trong caption LaTeX). Đặt tên **đúng tên file** ở mỗi mục bên dưới.
Các hình 4.28–4.32 được đặt ở trang ngang (landscape), nên vẽ theo chiều ngang (tầng trình bày bên trái →
tầng tích hợp bên phải).

**Thay vào bài:** chép các file PNG vào `design_03_10_DongDucNguyen/figures/` (ghi đè), biên dịch lại
`pdflatex design_03_10_DongDucNguyen.tex` 2 lần. Không cần sửa file `.tex` vì tên file giữ nguyên.
Các ảnh chụp màn hình DB (`db1`–`db7`) là ảnh thật từ Adminer, **không cần vẽ lại**.

## 2. Danh sách file cần vẽ

| Mục | Hình | File PNG | Loại diagram trong VP |
|---|---|---|---|
| 4.1 | 4.1 | `a00_analysis_overview.png` | Class Diagram (mức phân tích) |
| 4.1 | 4.2 | `a01_analysis_customers_catalogue.png` | Class Diagram (mức phân tích) |
| 4.1 | 4.3 | `a02_analysis_sales.png` | Class Diagram (mức phân tích) |
| 4.1 | 4.4 | `a03_analysis_inventory_returns.png` | Class Diagram (mức phân tích) |
| 4.1 | 4.5 | `a04_analysis_reviews_assistant_admin.png` | Class Diagram (mức phân tích) |
| 4.2 | 4.6 | `e0_erd_overview.png` | Entity Relationship Diagram (ERD) |
| 4.2 | 4.7 | `e1_erd_accounts.png` | Entity Relationship Diagram (ERD) |
| 4.2 | 4.8 | `e2_erd_catalogue.png` | Entity Relationship Diagram (ERD) |
| 4.2 | 4.9 | `e3_erd_inventory.png` | Entity Relationship Diagram (ERD) |
| 4.2 | 4.10 | `e4_erd_sales.png` | Entity Relationship Diagram (ERD) |
| 4.2 | 4.11 | `e5_erd_returns_reviews.png` | Entity Relationship Diagram (ERD) |
| 4.3 | 4.19 | `d1_design_accounts_admin.png` | Class Diagram (mức thiết kế) |
| 4.3 | 4.20 | `d2_design_catalogue.png` | Class Diagram (mức thiết kế) |
| 4.3 | 4.21 | `d3_design_inventory.png` | Class Diagram (mức thiết kế) |
| 4.3 | 4.22 | `d4_design_sales.png` | Class Diagram (mức thiết kế) |
| 4.3 | 4.23 | `d5_design_shipping_returns.png` | Class Diagram (mức thiết kế) |
| 4.3 | 4.24 | `d6_design_reviews_assistant.png` | Class Diagram (mức thiết kế) |
| 4.3 | 4.25 | `d7_state_order.png` | State Machine Diagram |
| 4.3 | 4.26 | `d8_state_return.png` | State Machine Diagram |
| 4.4 | 4.27 | `l0_layers_overview.png` | Class Diagram có Package theo tầng |
| 4.4 | 4.28 | `l1_layers_checkout.png` | Class Diagram có Package theo tầng |
| 4.4 | 4.29 | `l2_layers_returns.png` | Class Diagram có Package theo tầng |
| 4.4 | 4.30 | `l3_layers_catalogue_search_assistant.png` | Class Diagram có Package theo tầng |
| 4.4 | 4.31 | `l4_layers_cart_orders.png` | Class Diagram có Package theo tầng |
| 4.4 | 4.32 | `l5_layers_backoffice.png` | Class Diagram có Package theo tầng |

## 3. Chi tiết từng diagram

## 4.1 Class Diagram in Analysis

Mức phân tích: chỉ tên lớp, tên thuộc tính, quan hệ và bội số. Hình tổng quan `a00` chỉ có tên lớp được nhóm trong 6 package; các hình `a01`–`a04` là chi tiết từng nhóm (lớp thuộc nhóm khác chỉ hiện tên).

### Hình 4.1 — `a00_analysis_overview.png`

*Chú thích trong bài:* Analysis class diagram — overview of the 36 classes in six groups

- **Loại diagram trong VP:** Class Diagram (mức phân tích)
- **File nháp:** `design/diagrams/a00_analysis_overview.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Accounts`; `Catalogue`; `Inventory & supply`; `Sales & fulfilment`; `Returns`; `Reviews, assistant, admin`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Accounts*: `UserAccount`, `Customer`, `StaffMember`, `Address`, `PaymentMethod`
- *Catalogue*: `Category`, `Collection`, `Style`, `MaterialComponent`, `SizeChartEntry`, `ProductVariant`, `ProductMedia`
- *Inventory & supply*: `StockLocation`, `StockLevel`, `StockMovement`, `Supplier`, `RestockRequest`, `RestockLine`
- *Sales & fulfilment*: `Cart`, `CartItem`, `Order`, `OrderLine`, `Promotion`, `Voucher`, `Payment`, `Shipment`, `ShipmentLine`, `ShipmentEvent`
- *Returns*: `ReturnRequest`, `ReturnItem`, `ReturnEvidence`
- *Reviews, assistant, admin*: `Review`, `AssistantTurn`, `GroundingEvent`, `Notification`, `AuditLogEntry`

**Association class:** vẽ association `ProductVariant` — `StockLocation` (nhiều–nhiều), rồi nối class `StockLevel` vào giữa đường association bằng *Association Class* (nét đứt).

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Customer | | Generalization (con → cha) | | UserAccount |  |
| StaffMember | | Generalization (con → cha) | | UserAccount |  |
| Customer |  | Composition (hình thoi ở phía `Customer`) |  | Address |  |
| Customer |  | Composition (hình thoi ở phía `Customer`) |  | PaymentMethod |  |
| Style |  | Association (có hướng) |  | Category |  |
| Collection |  | Aggregation (hình thoi ở phía `Collection`) |  | Style |  |
| Style |  | Association (có hướng) |  | Supplier |  |
| Style |  | Composition (hình thoi ở phía `Style`) |  | MaterialComponent |  |
| Style |  | Composition (hình thoi ở phía `Style`) |  | SizeChartEntry |  |
| Style |  | Composition (hình thoi ở phía `Style`) |  | ProductVariant |  |
| Style |  | Composition (hình thoi ở phía `Style`) |  | ProductMedia |  |
| ProductVariant |  | Association |  | StockLocation |  |
| StockMovement |  | Association (có hướng) |  | ProductVariant |  |
| RestockRequest |  | Association (có hướng) |  | Supplier |  |
| RestockRequest |  | Composition (hình thoi ở phía `RestockRequest`) |  | RestockLine |  |
| Customer |  | Association |  | Cart |  |
| Cart |  | Composition (hình thoi ở phía `Cart`) |  | CartItem |  |
| CartItem |  | Association (có hướng) |  | ProductVariant |  |
| Customer |  | Association |  | Order |  |
| Order |  | Composition (hình thoi ở phía `Order`) |  | OrderLine |  |
| OrderLine |  | Association (có hướng) |  | ProductVariant |  |
| Promotion |  | Composition (hình thoi ở phía `Promotion`) |  | Voucher |  |
| Order |  | Association (có hướng) |  | Voucher |  |
| Order |  | Association |  | Payment |  |
| Order |  | Association |  | Shipment |  |
| Shipment |  | Composition (hình thoi ở phía `Shipment`) |  | ShipmentLine |  |
| Shipment |  | Composition (hình thoi ở phía `Shipment`) |  | ShipmentEvent |  |
| Order |  | Association |  | ReturnRequest |  |
| ReturnRequest |  | Composition (hình thoi ở phía `ReturnRequest`) |  | ReturnItem |  |
| ReturnRequest |  | Composition (hình thoi ở phía `ReturnRequest`) |  | ReturnEvidence |  |
| ReturnItem |  | Association (có hướng) |  | OrderLine |  |
| Review |  | Association (có hướng) |  | Style |  |
| Customer |  | Association |  | Review |  |
| AssistantTurn |  | Composition (hình thoi ở phía `AssistantTurn`) |  | GroundingEvent |  |
| AssistantTurn |  | Association (có hướng) |  | Style |  |
| Customer |  | Association |  | Notification |  |
| StaffMember |  | Association |  | AuditLogEntry |  |

### Hình 4.2 — `a01_analysis_customers_catalogue.png`

*Chú thích trong bài:* Analysis class diagram (1/4) — accounts, customers and catalogue

- **Loại diagram trong VP:** Class Diagram (mức phân tích)
- **File nháp:** `design/diagrams/a01_analysis_customers_catalogue.puml`

**Phần tử và thuộc tính / phương thức:**

- **UserAccount** *(abstract class)*
  - `accountId`; `email`; `password`; `status`; `createdAt`; `lastLoginAt`
- **Customer**
  - `fullName`; `phone`; `marketingConsent`; `savedSizes [0..*]`; `preferredColours [0..*]`
- **StaffMember**
  - `fullName`; `role`
- **Address**
  - `recipientName`; `phone`; `street`; `ward`; `district`; `city`; `isDefault`
- **PaymentMethod**
  - `provider`; `methodType`; `maskedNumber`; `providerToken`; `isDefault`
- **Category**
  - `name`; `slug`
- **Collection**
  - `name`; `season`; `year`
- **Supplier**
  - `name`; `email`; `phone`
- **Style**
  - `code`; `name`; `description`; `brand`; `fitType`; `careInstructions`; `features`; `modelInfo`; `status`
- **MaterialComponent**
  - `material`; `percent`
- **SizeChartEntry**
  - `sizeLabel`; `measure`; `valueCm`
- **ProductVariant**
  - `sku`; `sizeLabel`; `colour`; `price`; `status`
- **ProductMedia**
  - `url`; `mediaType`; `colour`; `sortOrder`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Customer | | Generalization (con → cha) | | UserAccount |  |
| StaffMember | | Generalization (con → cha) | | UserAccount |  |
| Customer | 1 | Composition (hình thoi ở phía `Customer`) | 0..* | Address | ships to |
| Customer | 1 | Composition (hình thoi ở phía `Customer`) | 0..* | PaymentMethod | links |
| Category | 0..1 | Association | 0..* | Category | parent of |
| Style | 0..* | Association | 1 | Category | belongs to |
| Collection | 0..1 | Aggregation (hình thoi ở phía `Collection`) | 0..* | Style | groups |
| Style | 0..* | Association | 0..1 | Supplier | supplied by |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 1..* | MaterialComponent | composed of |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 0..* | SizeChartEntry | size chart |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 1..* | ProductVariant | sold as |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 0..* | ProductMedia | shown in |

### Hình 4.3 — `a02_analysis_sales.png`

*Chú thích trong bài:* Analysis class diagram (2/4) — cart, orders, promotions, payments and shipments

- **Loại diagram trong VP:** Class Diagram (mức phân tích)
- **File nháp:** `design/diagrams/a02_analysis_sales.puml`

**Phần tử và thuộc tính / phương thức:**

- **Cart**
  - `updatedAt`
- **CartItem**
  - `quantity`; `addedAt`
- **Order**
  - `orderNo`; `status`; `placedAt`; `subtotal`; `discount`; `shippingFee`; `/grandTotal`; `note`; `shippingAddress`; `deliveryService`; `cancelReason`
- **OrderLine**
  - `quantity`; `unitPrice`; `discount`; `/lineTotal`
- **Promotion**
  - `name`; `promoType`; `discountType`; `discountValue`; `minOrderValue`; `startsAt`; `endsAt`; `status`
- **Voucher**
  - `code`; `usageLimit`; `usedCount`
- **Payment**
  - `kind`; `method`; `amount`; `status`; `transactionRef`; `createdAt`
- **Shipment**
  - `direction`; `carrier`; `serviceLevel`; `trackingNo`; `fee`; `status`; `deliveredAt`
- **ShipmentLine**
  - `quantity`
- **ShipmentEvent**
  - `status`; `occurredAt`; `note`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `Customer`, `ProductVariant`, `Style`, `StockLocation`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Customer | 1 | Association | 0..1 | Cart | owns |
| Cart | 1 | Composition (hình thoi ở phía `Cart`) | 0..* | CartItem |  |
| CartItem | 0..* | Association (có hướng) | 1 | ProductVariant | refers to |
| Customer | 1 | Association | 0..* | Order | places |
| Order | 1 | Composition (hình thoi ở phía `Order`) | 1..* | OrderLine |  |
| OrderLine | 0..* | Association (có hướng) | 1 | ProductVariant | orders |
| OrderLine | 0..* | Association | 1..* | StockLocation | allocated from |
| Promotion | 1 | Composition (hình thoi ở phía `Promotion`) | 0..* | Voucher |  |
| Promotion | 0..* | Association | 0..* | Style | applies to |
| Style | 1 | Association | 1..* | ProductVariant | sold as |
| Order | 0..* | Association | 0..1 | Voucher | redeems |
| Order | 1 | Association | 0..* | Payment | paid by |
| Order | 1 | Association | 0..* | Shipment | delivered in |
| Shipment | 1 | Composition (hình thoi ở phía `Shipment`) | 1..* | ShipmentLine |  |
| ShipmentLine | 0..* | Association (có hướng) | 1 | OrderLine | carries |
| Shipment | 1 | Composition (hình thoi ở phía `Shipment`) | 0..* | ShipmentEvent | tracked by |
| Shipment | 0..* | Association (có hướng) | 1 | StockLocation | ships from |

### Hình 4.4 — `a03_analysis_inventory_returns.png`

*Chú thích trong bài:* Analysis class diagram (3/4) — inventory, restocking, returns and exchanges

- **Loại diagram trong VP:** Class Diagram (mức phân tích)
- **File nháp:** `design/diagrams/a03_analysis_inventory_returns.puml`

**Phần tử và thuộc tính / phương thức:**

- **StockLocation**
  - `name`; `address`
- **StockLevel** «association class»
  - `onHand`; `reserved`; `reorderPoint`; `/available`
- **StockMovement**
  - `quantityChange`; `reason`; `reference`; `note`; `createdAt`
- **RestockRequest**
  - `requestNo`; `status`; `createdAt`; `expectedDate`; `supplierNote`
- **RestockLine**
  - `quantity`
- **ReturnRequest**
  - `returnNo`; `returnType`; `reasonCode`; `reasonDetail`; `desiredResolution`; `status`; `requestedAt`; `decidedAt`; `decisionNote`
- **ReturnItem**
  - `quantity`; `inspectionResult`; `inspectionNote`
- **ReturnEvidence**
  - `url`; `mediaType`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `ProductVariant`, `Supplier`, `StaffMember`, `Order`, `OrderLine`, `Payment`, `Shipment`

**Association class:** vẽ association `ProductVariant` — `StockLocation` (nhiều–nhiều), rồi nối class `StockLevel` vào giữa đường association bằng *Association Class* (nét đứt).

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| ProductVariant | 0..* | Association | 0..* | StockLocation |  |
| StockMovement | 0..* | Association (có hướng) | 1 | ProductVariant | changes |
| StockMovement | 0..* | Association (có hướng) | 1 | StockLocation | at |
| StockMovement | 0..* | Association (có hướng) | 0..1 | StaffMember | made by |
| Supplier | 1 | Association | 0..* | RestockRequest | receives |
| RestockRequest | 1 | Composition (hình thoi ở phía `RestockRequest`) | 1..* | RestockLine |  |
| RestockLine | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| RestockRequest | 0..* | Association (có hướng) | 1 | StaffMember | created by |
| RestockRequest | 0..* | Association (có hướng) | 1 | StockLocation | delivered to |
| Order | 1 | Association | 0..* | ReturnRequest | concerns &lt; |
| ReturnRequest | 1 | Composition (hình thoi ở phía `ReturnRequest`) | 1..* | ReturnItem |  |
| ReturnItem | 0..* | Association (có hướng) | 1 | OrderLine | returns |
| ReturnItem | 0..* | Association (có hướng) | 0..1 | ProductVariant | exchange for |
| ReturnRequest | 1 | Composition (hình thoi ở phía `ReturnRequest`) | 0..* | ReturnEvidence |  |
| ReturnRequest | 0..* | Association (có hướng) | 0..1 | StaffMember | decided by |
| ReturnRequest | 0..1 | Association | 0..1 | Shipment | picked up by |
| ReturnRequest | 0..1 | Association | 0..* | Payment | refunded by |

### Hình 4.5 — `a04_analysis_reviews_assistant_admin.png`

*Chú thích trong bài:* Analysis class diagram (4/4) — reviews, AI assistant, notifications and audit

- **Loại diagram trong VP:** Class Diagram (mức phân tích)
- **File nháp:** `design/diagrams/a04_analysis_reviews_assistant_admin.puml`

**Phần tử và thuộc tính / phương thức:**

- **Review**
  - `rating`; `body`; `sizePurchased`; `fitVote`; `verifiedPurchase`; `origin`; `status`; `moderationNote`; `createdAt`
- **AssistantTurn**
  - `questionRedacted`; `mode`; `promptVersion`; `modelName`; `latencyMs`; `createdAt`
- **GroundingEvent**
  - `checkName`; `removedText`
- **Notification**
  - `channel`; `eventType`; `message`; `status`; `sentAt`
- **AuditLogEntry**
  - `entityType`; `entityId`; `action`; `changes`; `createdAt`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `Style`, `ProductVariant`, `Customer`, `OrderLine`, `StaffMember`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Style | 1 | Association | 0..* | Review | reviewed in |
| Review | 0..* | Association (có hướng) | 0..1 | ProductVariant | size bought |
| Customer | 0..1 | Association | 0..* | Review | writes |
| Review | 0..1 | Association (có hướng) | 0..1 | OrderLine | verifies purchase of |
| StaffMember | 0..1 | Association | 0..* | Review | moderates |
| AssistantTurn | 0..* | Association (có hướng) | 0..1 | Style | asks about |
| AssistantTurn | 0..* | Association (có hướng) | 0..1 | Customer | asked by |
| AssistantTurn | 1 | Composition (hình thoi ở phía `AssistantTurn`) | 0..* | GroundingEvent | logs |
| Customer | 1 | Association | 0..* | Notification | receives |
| StaffMember | 1 | Association | 0..* | AuditLogEntry | recorded for |


## 4.2 Data Model (ERD)

Bảng `e0` chỉ có tên bảng trong 5 package và các đường quan hệ; `e1`–`e5` có đầy đủ cột. Các ERD được đọc ngược từ DB đang chạy (41 bảng, 66 khoá ngoại), nên khớp tuyệt đối với `db/schema.sql`.

### Hình 4.6 — `e0_erd_overview.png`

*Chú thích trong bài:* Entity–relationship diagram — overview of the 41 tables

- **Loại diagram trong VP:** Entity Relationship Diagram (ERD)
- **File nháp:** `design/diagrams/e0_erd_overview.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Accounts and customers`; `Catalogue`; `Inventory and supply`; `Cart, promotions, orders, payments and shipments`; `Returns, reviews, assistant log, notifications and audit`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Accounts and customers*: `user_account`, `customer`, `staff_member`, `address`, `payment_method`, `saved_size`, `preferred_colour`
- *Catalogue*: `category`, `collection`, `supplier`, `style`, `material_component`, `size_chart_entry`, `product_variant`, `product_media`, `product_embedding`
- *Inventory and supply*: `stock_location`, `stock_level`, `stock_movement`, `restock_request`, `restock_line`
- *Cart, promotions, orders, payments and shipments*: `cart`, `cart_item`, `promotion`, `promotion_style`, `voucher`, `customer_order`, `order_line`, `order_allocation`, `payment`, `shipment`, `shipment_line`, `shipment_event`
- *Returns, reviews, assistant log, notifications and audit*: `return_request`, `return_item`, `return_evidence`, `review`, `assistant_turn`, `grounding_event`, `notification`, `audit_log`

| Bảng cha | Bảng con | Bản số (cha — con) | Cột khoá ngoại |
|---|---|---|---|
| customer | address | đúng 1 — 0..* |  |
| customer | assistant_turn | 0..1 — 0..* |  |
| style | assistant_turn | 0..1 — 0..* |  |
| staff_member | audit_log | đúng 1 — 0..* |  |
| customer | cart | đúng 1 — 0..1 |  |
| cart | cart_item | đúng 1 — 0..* |  |
| product_variant | cart_item | đúng 1 — 0..* |  |
| category | category | 0..1 — 0..* |  |
| user_account | customer | đúng 1 — 0..1 |  |
| customer | customer_order | đúng 1 — 0..* |  |
| voucher | customer_order | 0..1 — 0..* |  |
| assistant_turn | grounding_event | đúng 1 — 0..* |  |
| style | material_component | đúng 1 — 0..* |  |
| customer | notification | đúng 1 — 0..* |  |
| stock_location | order_allocation | đúng 1 — 0..* |  |
| order_line | order_allocation | đúng 1 — 0..* |  |
| customer_order | order_line | đúng 1 — 0..* |  |
| product_variant | order_line | đúng 1 — 0..* |  |
| customer_order | payment | đúng 1 — 0..* |  |
| return_request | payment | 0..1 — 0..* |  |
| customer | payment_method | đúng 1 — 0..* |  |
| customer | preferred_colour | đúng 1 — 0..* |  |
| product_media | product_embedding | 0..1 — 0..* |  |
| style | product_embedding | đúng 1 — 0..* |  |
| style | product_media | đúng 1 — 0..* |  |
| style | product_variant | đúng 1 — 0..* |  |
| staff_member | promotion | 0..1 — 0..* |  |
| promotion | promotion_style | đúng 1 — 0..* |  |
| style | promotion_style | đúng 1 — 0..* |  |
| restock_request | restock_line | đúng 1 — 0..* |  |
| product_variant | restock_line | đúng 1 — 0..* |  |
| staff_member | restock_request | đúng 1 — 0..* |  |
| stock_location | restock_request | đúng 1 — 0..* |  |
| supplier | restock_request | đúng 1 — 0..* |  |
| return_request | return_evidence | đúng 1 — 0..* |  |
| product_variant | return_item | 0..1 — 0..* |  |
| staff_member | return_item | 0..1 — 0..* |  |
| order_line | return_item | đúng 1 — 0..* |  |
| return_request | return_item | đúng 1 — 0..* |  |
| customer | return_request | đúng 1 — 0..* |  |
| staff_member | return_request | 0..1 — 0..* |  |
| customer_order | return_request | đúng 1 — 0..* |  |
| customer | review | 0..1 — 0..* |  |
| staff_member | review | 0..1 — 0..* |  |
| order_line | review | 0..1 — 0..1 |  |
| style | review | đúng 1 — 0..* |  |
| product_variant | review | 0..1 — 0..* |  |
| category | saved_size | đúng 1 — 0..* |  |
| customer | saved_size | đúng 1 — 0..* |  |
| stock_location | shipment | đúng 1 — 0..* |  |
| customer_order | shipment | đúng 1 — 0..* |  |
| return_request | shipment | 0..1 — 0..* |  |
| shipment | shipment_event | đúng 1 — 0..* |  |
| order_line | shipment_line | đúng 1 — 0..* |  |
| shipment | shipment_line | đúng 1 — 0..* |  |
| style | size_chart_entry | đúng 1 — 0..* |  |
| user_account | staff_member | đúng 1 — 0..1 |  |
| stock_location | stock_level | đúng 1 — 0..* |  |
| product_variant | stock_level | đúng 1 — 0..* |  |
| stock_location | stock_movement | đúng 1 — 0..* |  |
| staff_member | stock_movement | 0..1 — 0..* |  |
| product_variant | stock_movement | đúng 1 — 0..* |  |
| category | style | đúng 1 — 0..* |  |
| collection | style | 0..1 — 0..* |  |
| supplier | style | 0..1 — 0..* |  |
| promotion | voucher | đúng 1 — 0..* |  |

### Hình 4.7 — `e1_erd_accounts.png`

*Chú thích trong bài:* ERD — accounts and customers

- **Loại diagram trong VP:** Entity Relationship Diagram (ERD)
- **File nháp:** `design/diagrams/e1_erd_accounts.puml`

**Phần tử và thuộc tính / phương thức:**

- **user_account**
  - Cột: `account_id` int **PK**; `email` varchar(254); `password_hash` varchar(255); `account_type` varchar(10); `status` varchar(10); `created_at` timestamptz; `last_login_at` timestamptz (nullable)
- **customer**
  - Cột: `customer_id` int **PK, FK**; `full_name` varchar(120); `phone` varchar(20) (nullable); `marketing_consent` bool
- **staff_member**
  - Cột: `staff_id` int **PK, FK**; `full_name` varchar(120); `role` varchar(20)
- **address**
  - Cột: `address_id` int **PK**; `customer_id` int **FK**; `recipient_name` varchar(120); `phone` varchar(20); `line1` varchar(200); `ward` varchar(80) (nullable); `district` varchar(80) (nullable); `city` varchar(80); `is_default` bool
- **payment_method**
  - Cột: `payment_method_id` int **PK**; `customer_id` int **FK**; `provider` varchar(40); `method_type` varchar(15); `masked_number` varchar(25); `provider_token` varchar(255); `is_default` bool
- **saved_size**
  - Cột: `customer_id` int **PK, FK**; `category_id` int **PK, FK**; `size_label` varchar(10)
- **preferred_colour**
  - Cột: `customer_id` int **PK, FK**; `colour` varchar(40) **PK**

**Bảng tham chiếu từ nhóm khác (chỉ vẽ khoá chính, tô xám):** `category`

| Bảng cha | Bảng con | Bản số (cha — con) | Cột khoá ngoại |
|---|---|---|---|
| customer | address | đúng 1 — 0..* | customer_id |
| user_account | customer | đúng 1 — 0..1 | customer_id |
| customer | payment_method | đúng 1 — 0..* | customer_id |
| customer | preferred_colour | đúng 1 — 0..* | customer_id |
| category | saved_size | đúng 1 — 0..* | category_id |
| customer | saved_size | đúng 1 — 0..* | customer_id |
| user_account | staff_member | đúng 1 — 0..1 | staff_id |

### Hình 4.8 — `e2_erd_catalogue.png`

*Chú thích trong bài:* ERD — catalogue

- **Loại diagram trong VP:** Entity Relationship Diagram (ERD)
- **File nháp:** `design/diagrams/e2_erd_catalogue.puml`

**Phần tử và thuộc tính / phương thức:**

- **category**
  - Cột: `category_id` int **PK**; `parent_id` int **FK** (nullable); `name` varchar(60); `slug` varchar(60)
- **collection**
  - Cột: `collection_id` int **PK**; `name` varchar(80); `season` varchar(10) (nullable); `year` smallint (nullable)
- **supplier**
  - Cột: `supplier_id` int **PK**; `name` varchar(120); `email` varchar(254); `phone` varchar(20) (nullable)
- **style**
  - Cột: `style_id` int **PK**; `code` varchar(40); `name` varchar(120); `description` text; `brand` varchar(80) (nullable); `category_id` int **FK**; `collection_id` int **FK** (nullable); `supplier_id` int **FK** (nullable); `fit_type` varchar(15) (nullable); `care_instructions` text (nullable); `features` text (nullable); `model_info` varchar(200) (nullable); `status` varchar(10); `created_at` timestamptz; `updated_at` timestamptz
- **material_component**
  - Cột: `style_id` int **PK, FK**; `material` varchar(60) **PK**; `percent` smallint (nullable)
- **size_chart_entry**
  - Cột: `style_id` int **PK, FK**; `size_label` varchar(10) **PK**; `measure` varchar(30) **PK**; `value_cm` numeric(5,1)
- **product_variant**
  - Cột: `variant_id` int **PK**; `style_id` int **FK**; `sku` varchar(30); `size_label` varchar(10); `colour` varchar(40); `price_vnd` int; `status` varchar(12)
- **product_media**
  - Cột: `media_id` int **PK**; `style_id` int **FK**; `colour` varchar(40) (nullable); `url` varchar(300); `media_type` varchar(5); `sort_order` smallint
- **product_embedding**
  - Cột: `embedding_id` int **PK**; `style_id` int **FK**; `media_id` int **FK** (nullable); `kind` varchar(5); `model_name` varchar(60); `vector` real[]; `created_at` timestamptz

| Bảng cha | Bảng con | Bản số (cha — con) | Cột khoá ngoại |
|---|---|---|---|
| category | category | 0..1 — 0..* | parent_id |
| style | material_component | đúng 1 — 0..* | style_id |
| product_media | product_embedding | 0..1 — 0..* | media_id |
| style | product_embedding | đúng 1 — 0..* | style_id |
| style | product_media | đúng 1 — 0..* | style_id |
| style | product_variant | đúng 1 — 0..* | style_id |
| style | size_chart_entry | đúng 1 — 0..* | style_id |
| category | style | đúng 1 — 0..* | category_id |
| collection | style | 0..1 — 0..* | collection_id |
| supplier | style | 0..1 — 0..* | supplier_id |

### Hình 4.9 — `e3_erd_inventory.png`

*Chú thích trong bài:* ERD — inventory and supply

- **Loại diagram trong VP:** Entity Relationship Diagram (ERD)
- **File nháp:** `design/diagrams/e3_erd_inventory.puml`

**Phần tử và thuộc tính / phương thức:**

- **stock_location**
  - Cột: `location_id` int **PK**; `name` varchar(80); `address` varchar(200)
- **stock_level**
  - Cột: `variant_id` int **PK, FK**; `location_id` int **PK, FK**; `on_hand` int; `reserved` int; `reorder_point` int
- **stock_movement**
  - Cột: `movement_id` int **PK**; `variant_id` int **FK**; `location_id` int **FK**; `quantity_change` int; `reason` varchar(12); `reference_type` varchar(12) (nullable); `reference_id` int (nullable); `staff_id` int **FK** (nullable); `note` varchar(200) (nullable); `created_at` timestamptz
- **restock_request**
  - Cột: `restock_id` int **PK**; `request_no` varchar(20); `supplier_id` int **FK**; `location_id` int **FK**; `created_by` int **FK**; `status` varchar(10); `created_at` timestamptz; `expected_date` date (nullable); `supplier_note` varchar(300) (nullable)
- **restock_line**
  - Cột: `restock_id` int **PK, FK**; `variant_id` int **PK, FK**; `quantity` int

**Bảng tham chiếu từ nhóm khác (chỉ vẽ khoá chính, tô xám):** `product_variant`, `staff_member`, `supplier`

| Bảng cha | Bảng con | Bản số (cha — con) | Cột khoá ngoại |
|---|---|---|---|
| restock_request | restock_line | đúng 1 — 0..* | restock_id |
| product_variant | restock_line | đúng 1 — 0..* | variant_id |
| staff_member | restock_request | đúng 1 — 0..* | created_by |
| stock_location | restock_request | đúng 1 — 0..* | location_id |
| supplier | restock_request | đúng 1 — 0..* | supplier_id |
| stock_location | stock_level | đúng 1 — 0..* | location_id |
| product_variant | stock_level | đúng 1 — 0..* | variant_id |
| stock_location | stock_movement | đúng 1 — 0..* | location_id |
| staff_member | stock_movement | 0..1 — 0..* | staff_id |
| product_variant | stock_movement | đúng 1 — 0..* | variant_id |

### Hình 4.10 — `e4_erd_sales.png`

*Chú thích trong bài:* ERD — cart, promotions, orders, payments and shipments

- **Loại diagram trong VP:** Entity Relationship Diagram (ERD)
- **File nháp:** `design/diagrams/e4_erd_sales.puml`

**Phần tử và thuộc tính / phương thức:**

- **cart**
  - Cột: `cart_id` int **PK**; `customer_id` int **FK**; `updated_at` timestamptz
- **cart_item**
  - Cột: `cart_id` int **PK, FK**; `variant_id` int **PK, FK**; `quantity` int; `added_at` timestamptz
- **promotion**
  - Cột: `promotion_id` int **PK**; `name` varchar(120); `promo_type` varchar(12); `discount_type` varchar(12); `discount_value` int; `min_order_vnd` int; `starts_at` timestamptz; `ends_at` timestamptz; `status` varchar(8); `created_by` int **FK** (nullable)
- **promotion_style**
  - Cột: `promotion_id` int **PK, FK**; `style_id` int **PK, FK**
- **voucher**
  - Cột: `voucher_id` int **PK**; `promotion_id` int **FK**; `code` varchar(30); `usage_limit` int; `used_count` int
- **customer_order**
  - Cột: `order_id` int **PK**; `order_no` varchar(20); `customer_id` int **FK**; `status` varchar(18); `placed_at` timestamptz; `confirmed_at` timestamptz (nullable); `delivered_at` timestamptz (nullable); `cancelled_at` timestamptz (nullable); `cancel_reason` varchar(200) (nullable); `subtotal_vnd` int; `discount_vnd` int; `shipping_fee_vnd` int; `grand_total_vnd` int; `voucher_id` int **FK** (nullable); `note` varchar(300) (nullable); `delivery_service` varchar(40) (nullable); `ship_recipient` varchar(120); `ship_phone` varchar(20); `ship_line1` varchar(200); `ship_ward` varchar(80) (nullable); `ship_district` varchar(80) (nullable); `ship_city` varchar(80)
- **order_line**
  - Cột: `order_line_id` int **PK**; `order_id` int **FK**; `variant_id` int **FK**; `quantity` int; `unit_price_vnd` int; `discount_vnd` int
- **order_allocation**
  - Cột: `order_line_id` int **PK, FK**; `location_id` int **PK, FK**; `quantity` int
- **payment**
  - Cột: `payment_id` int **PK**; `order_id` int **FK**; `return_id` int **FK** (nullable); `kind` varchar(6); `method` varchar(15); `amount_vnd` int; `status` varchar(10); `transaction_ref` varchar(60) (nullable); `failure_reason` varchar(200) (nullable); `created_at` timestamptz; `updated_at` timestamptz
- **shipment**
  - Cột: `shipment_id` int **PK**; `order_id` int **FK**; `return_id` int **FK** (nullable); `direction` varchar(13); `location_id` int **FK**; `carrier` varchar(40); `service_level` varchar(40) (nullable); `tracking_no` varchar(40) (nullable); `fee_vnd` int; `status` varchar(10); `created_at` timestamptz; `delivered_at` timestamptz (nullable)
- **shipment_line**
  - Cột: `shipment_id` int **PK, FK**; `order_line_id` int **PK, FK**; `quantity` int
- **shipment_event**
  - Cột: `event_id` int **PK**; `shipment_id` int **FK**; `status` varchar(10); `occurred_at` timestamptz; `note` varchar(200) (nullable)

**Bảng tham chiếu từ nhóm khác (chỉ vẽ khoá chính, tô xám):** `customer`, `product_variant`, `return_request`, `staff_member`, `stock_location`, `style`

| Bảng cha | Bảng con | Bản số (cha — con) | Cột khoá ngoại |
|---|---|---|---|
| customer | cart | đúng 1 — 0..1 | customer_id |
| cart | cart_item | đúng 1 — 0..* | cart_id |
| product_variant | cart_item | đúng 1 — 0..* | variant_id |
| customer | customer_order | đúng 1 — 0..* | customer_id |
| voucher | customer_order | 0..1 — 0..* | voucher_id |
| stock_location | order_allocation | đúng 1 — 0..* | location_id |
| order_line | order_allocation | đúng 1 — 0..* | order_line_id |
| customer_order | order_line | đúng 1 — 0..* | order_id |
| product_variant | order_line | đúng 1 — 0..* | variant_id |
| customer_order | payment | đúng 1 — 0..* | order_id |
| return_request | payment | 0..1 — 0..* | return_id |
| staff_member | promotion | 0..1 — 0..* | created_by |
| promotion | promotion_style | đúng 1 — 0..* | promotion_id |
| style | promotion_style | đúng 1 — 0..* | style_id |
| stock_location | shipment | đúng 1 — 0..* | location_id |
| customer_order | shipment | đúng 1 — 0..* | order_id |
| return_request | shipment | 0..1 — 0..* | return_id |
| shipment | shipment_event | đúng 1 — 0..* | shipment_id |
| order_line | shipment_line | đúng 1 — 0..* | order_line_id |
| shipment | shipment_line | đúng 1 — 0..* | shipment_id |
| promotion | voucher | đúng 1 — 0..* | promotion_id |

### Hình 4.11 — `e5_erd_returns_reviews.png`

*Chú thích trong bài:* ERD — returns, reviews, assistant log, notifications and audit

- **Loại diagram trong VP:** Entity Relationship Diagram (ERD)
- **File nháp:** `design/diagrams/e5_erd_returns_reviews.puml`

**Phần tử và thuộc tính / phương thức:**

- **return_request**
  - Cột: `return_id` int **PK**; `return_no` varchar(20); `order_id` int **FK**; `customer_id` int **FK**; `return_type` varchar(8); `reason_code` varchar(17); `reason_detail` varchar(500) (nullable); `desired_resolution` varchar(8); `status` varchar(10); `requested_at` timestamptz; `decided_at` timestamptz (nullable); `decided_by` int **FK** (nullable); `decision_note` varchar(300) (nullable)
- **return_item**
  - Cột: `return_item_id` int **PK**; `return_id` int **FK**; `order_line_id` int **FK**; `quantity` int; `exchange_variant_id` int **FK** (nullable); `inspection_result` varchar(7); `inspection_note` varchar(300) (nullable); `inspected_by` int **FK** (nullable); `inspected_at` timestamptz (nullable)
- **return_evidence**
  - Cột: `evidence_id` int **PK**; `return_id` int **FK**; `url` varchar(300); `media_type` varchar(5)
- **review**
  - Cột: `review_id` int **PK**; `style_id` int **FK**; `variant_id` int **FK** (nullable); `customer_id` int **FK** (nullable); `order_line_id` int **FK** (nullable); `rating` smallint; `body` text; `size_purchased` varchar(10) (nullable); `fit_vote` varchar(12) (nullable); `verified_purchase` bool; `origin` varchar(15); `source_url` varchar(300) (nullable); `status` varchar(8); `moderation_note` varchar(200) (nullable); `moderated_by` int **FK** (nullable); `content_hash` char(64); `created_at` timestamptz
- **assistant_turn**
  - Cột: `turn_id` int **PK**; `style_id` int **FK** (nullable); `customer_id` int **FK** (nullable); `question_redacted` varchar(500); `mode` varchar(5); `prompt_version` varchar(60); `model_name` varchar(60) (nullable); `latency_ms` int (nullable); `created_at` timestamptz
- **grounding_event**
  - Cột: `event_id` int **PK**; `turn_id` int **FK**; `check_name` varchar(15); `removed_text` varchar(500); `created_at` timestamptz
- **notification**
  - Cột: `notification_id` int **PK**; `customer_id` int **FK**; `channel` varchar(5); `event_type` varchar(30); `message` varchar(500); `status` varchar(7); `created_at` timestamptz; `sent_at` timestamptz (nullable)
- **audit_log**
  - Cột: `audit_id` int **PK**; `staff_id` int **FK**; `entity_type` varchar(20); `entity_id` int; `action` varchar(10); `changes` jsonb (nullable); `created_at` timestamptz

**Bảng tham chiếu từ nhóm khác (chỉ vẽ khoá chính, tô xám):** `customer`, `customer_order`, `order_line`, `product_variant`, `staff_member`, `style`

| Bảng cha | Bảng con | Bản số (cha — con) | Cột khoá ngoại |
|---|---|---|---|
| customer | assistant_turn | 0..1 — 0..* | customer_id |
| style | assistant_turn | 0..1 — 0..* | style_id |
| staff_member | audit_log | đúng 1 — 0..* | staff_id |
| assistant_turn | grounding_event | đúng 1 — 0..* | turn_id |
| customer | notification | đúng 1 — 0..* | customer_id |
| return_request | return_evidence | đúng 1 — 0..* | return_id |
| product_variant | return_item | 0..1 — 0..* | exchange_variant_id |
| staff_member | return_item | 0..1 — 0..* | inspected_by |
| order_line | return_item | đúng 1 — 0..* | order_line_id |
| return_request | return_item | đúng 1 — 0..* | return_id |
| customer | return_request | đúng 1 — 0..* | customer_id |
| staff_member | return_request | 0..1 — 0..* | decided_by |
| customer_order | return_request | đúng 1 — 0..* | order_id |
| customer | review | 0..1 — 0..* | customer_id |
| staff_member | review | 0..1 — 0..* | moderated_by |
| order_line | review | 0..1 — 0..1 | order_line_id |
| style | review | đúng 1 — 0..* | style_id |
| product_variant | review | 0..1 — 0..* | variant_id |


## 4.3 Class Diagram in Design (và 2 State Machine)

Đây là các lớp của tầng domain (37 lớp + 27 enumeration). Lớp vẽ màu xám / chỉ có tên là lớp thuộc hình khác. Hai state machine `d7`, `d8` dùng State Machine Diagram.

### Hình 4.19 — `d1_design_accounts_admin.png`

*Chú thích trong bài:* Design class diagram — accounts, notifications and audit

- **Loại diagram trong VP:** Class Diagram (mức thiết kế)
- **File nháp:** `design/diagrams/d1_design_accounts_admin.puml`

**Phần tử và thuộc tính / phương thức:**

- **UserAccount** *(abstract class)* «entity»
  - `- account_id : int`; `- email : str`; `- password_hash : str`; `- status : AccountStatus`; `- created_at : datetime`; `- last_login_at : datetime | None`; `+ set_password(raw: str) : None`; `+ verify_password(raw: str) : bool`; `+ is_active() : bool`; `+ suspend() : None`; `+ reactivate() : None`; `+ record_login(at: datetime) : None`
- **Customer** «entity»
  - `- full_name : str`; `- phone : str | None`; `- marketing_consent : bool`; `- addresses : list[Address]`; `- saved_sizes : dict[int, str]`; `- preferred_colours : list[str]`; `- payment_methods : list[PaymentMethod]`; `+ add_address(address: Address) : None`; `+ default_address() : Address | None`; `+ save_size(category_id: int, size_label: str) : None`; `+ link_payment_method(method: PaymentMethod) : None`
- **StaffMember** «entity»
  - `- full_name : str`; `- role : StaffRole`; `+ has_role(roles: set[StaffRole]) : bool`
- **Address** «entity»
  - `- address_id : int | None`; `- recipient_name : str`; `- phone : str`; `- line1 : str`; `- ward : str | None`; `- district : str | None`; `- city : str`; `- is_default : bool`; `+ one_line() : str`
- **PaymentMethod** «entity»
  - `- payment_method_id : int | None`; `- provider : str`; `- method_type : PaymentMethodType`; `- masked_number : str`; `- provider_token : str`; `- is_default : bool`
- **Notification** «entity»
  - `- notification_id : int | None`; `- customer_id : int`; `- channel : NotificationChannel`; `- event_type : str`; `- message : str`; `- status : str`; `- created_at : datetime`; `- sent_at : datetime | None`; `+ mark_sent(at: datetime) : None`; `+ mark_failed() : None`
- **AuditLogEntry** «entity»
  - `- audit_id : int | None`; `- staff_id : int`; `- entity_type : str`; `- entity_id : int`; `- action : str`; `- changes : dict`; `- created_at : datetime`
- **AccountStatus** *(enum)* «enumeration»
  - `ACTIVE`; `SUSPENDED`; `DELETED`
- **StaffRole** *(enum)* «enumeration»
  - `ADMINISTRATOR`; `MERCHANDISER`; `MARKETING`; `CUSTOMER_SERVICE`; `MANAGER`; `WAREHOUSE`; `SALES`
- **PaymentMethodType** *(enum)* «enumeration»
  - `CARD`; `E_WALLET`; `BANK_TRANSFER`
- **NotificationChannel** *(enum)* «enumeration»
  - `EMAIL`; `SMS`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `Cart`, `Order`, `Review`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Customer | | Generalization (con → cha) | | UserAccount |  |
| StaffMember | | Generalization (con → cha) | | UserAccount |  |
| Customer | 1 | Composition (hình thoi ở phía `Customer`) | 0..* | Address | addresses |
| Customer | 1 | Composition (hình thoi ở phía `Customer`) | 0..* | PaymentMethod | payment_methods |
| Cart | 0..1 | Association (có hướng) | 1 | Customer |  |
| Order | 0..* | Association (có hướng) | 1 | Customer |  |
| Order | 1 | Composition (hình thoi ở phía `Order`) | 1 | Address | shipping_address (snapshot) |
| Review | 0..* | Association (có hướng) | 0..1 | Customer |  |
| AuditLogEntry | 0..* | Association (có hướng) | 1 | StaffMember |  |
| Notification | 0..* | Association (có hướng) | 1 | Customer |  |
| UserAccount |  | Dependency |  | AccountStatus |  |
| StaffMember |  | Dependency |  | StaffRole |  |
| PaymentMethod |  | Dependency |  | PaymentMethodType |  |
| Notification |  | Dependency |  | NotificationChannel |  |

### Hình 4.20 — `d2_design_catalogue.png`

*Chú thích trong bài:* Design class diagram — catalogue

- **Loại diagram trong VP:** Class Diagram (mức thiết kế)
- **File nháp:** `design/diagrams/d2_design_catalogue.puml`

**Phần tử và thuộc tính / phương thức:**

- **Category** «entity»
  - `- category_id : int`; `- name : str`; `- slug : str`; `- parent_id : int | None`
- **Collection** «entity»
  - `- collection_id : int`; `- name : str`; `- season : str | None`; `- year : int | None`
- **Style** «entity»
  - `- style_id : int | None`; `- code : str`; `- name : str`; `- description : str`; `- brand : str | None`; `- category_id : int`; `- collection_id : int | None`; `- supplier_id : int | None`; `- fit_type : FitType | None`; `- care_instructions : list[str]`; `- features : list[str]`; `- model_info : str | None`; `- status : StyleStatus`; `- materials : list[MaterialComponent]`; `- size_chart : list[SizeChartEntry]`; `- variants : list[ProductVariant]`; `- media : list[ProductMedia]`; `+ add_variant(variant: ProductVariant) : None`; `+ find_variant(sku: str) : ProductVariant | None`; `+ missing_facts() : list[str]`; `+ publish() : None`; `+ deactivate() : None`; `+ is_published() : bool`; `+ material_summary() : str`
- **MaterialComponent** «entity»
  - `- material : str`; `- percent : int | None`
- **SizeChartEntry** «entity»
  - `- size_label : str`; `- measure : str`; `- value_cm : float`
- **ProductVariant** «entity»
  - `- variant_id : int | None`; `- style_id : int | None`; `- sku : str`; `- size_label : str`; `- colour : str`; `- price_vnd : int`; `- status : VariantStatus`; `+ change_price(new_price_vnd: int) : None`; `+ is_sellable() : bool`
- **ProductMedia** «entity»
  - `- media_id : int | None`; `- url : str`; `- media_type : MediaType`; `- colour : str | None`; `- sort_order : int`
- **StyleStatus** *(enum)* «enumeration»
  - `DRAFT`; `PUBLISHED`; `INACTIVE`
- **FitType** *(enum)* «enumeration»
  - `SLIM`; `REGULAR`; `RELAXED`; `OVERSIZED`; `STANDARD_WIDTH`
- **VariantStatus** *(enum)* «enumeration»
  - `ACTIVE`; `DISCONTINUED`
- **MediaType** *(enum)* «enumeration»
  - `IMAGE`; `VIDEO`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `AssistantTurn`, `CartItem`, `OrderLine`, `Promotion`, `RestockLine`, `ReturnItem`, `Review`, `StockLevel`, `StockMovement`, `Supplier`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Category | 0..1 | Association (có hướng) | 0..* | Category | parent |
| Style | 0..* | Association (có hướng) | 1 | Category | category_id |
| Collection | 0..1 | Aggregation (hình thoi ở phía `Collection`) | 0..* | Style |  |
| Style | 0..* | Association (có hướng) | 0..1 | Supplier | supplier_id |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 1..* | MaterialComponent | materials |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 0..* | SizeChartEntry | size_chart |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 1..* | ProductVariant | variants |
| Style | 1 | Composition (hình thoi ở phía `Style`) | 0..* | ProductMedia | media |
| StockLevel | 0..* | Association (có hướng) | 1 | ProductVariant | variant_id |
| StockMovement | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| RestockLine | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| CartItem | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| OrderLine | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| Promotion | 0..* | Association (có hướng) | 0..* | Style | style_ids |
| ReturnItem | 0..* | Association (có hướng) | 0..1 | ProductVariant | exchange to |
| Review | 0..* | Association (có hướng) | 1 | Style |  |
| AssistantTurn | 0..* | Association (có hướng) | 0..1 | Style |  |
| Style |  | Dependency |  | FitType |  |
| Style |  | Dependency |  | StyleStatus |  |
| ProductVariant |  | Dependency |  | VariantStatus |  |
| ProductMedia |  | Dependency |  | MediaType |  |

### Hình 4.21 — `d3_design_inventory.png`

*Chú thích trong bài:* Design class diagram — inventory and restocking

- **Loại diagram trong VP:** Class Diagram (mức thiết kế)
- **File nháp:** `design/diagrams/d3_design_inventory.puml`

**Phần tử và thuộc tính / phương thức:**

- **StockLocation** «entity»
  - `- location_id : int`; `- name : str`; `- address : str`
- **StockLevel** «entity»
  - `- variant_id : int`; `- location_id : int`; `- on_hand : int`; `- reserved : int`; `- reorder_point : int`; `+ available() : int`; `+ reserve(quantity: int) : None`; `+ release(quantity: int) : None`; `+ commit_sale(quantity: int) : None`; `+ receive(quantity: int) : None`; `+ adjust(delta: int) : None`; `+ needs_reorder() : bool`
- **StockMovement** «entity»
  - `- movement_id : int | None`; `- variant_id : int`; `- location_id : int`; `- quantity_change : int`; `- reason : MovementReason`; `- reference_type : str | None`; `- reference_id : int | None`; `- staff_id : int | None`; `- note : str | None`; `- created_at : datetime`
- **Supplier** «entity»
  - `- supplier_id : int`; `- name : str`; `- email : str`; `- phone : str | None`
- **RestockRequest** «entity»
  - `- restock_id : int | None`; `- request_no : str`; `- supplier_id : int`; `- location_id : int`; `- created_by : int`; `- status : RestockStatus`; `- created_at : datetime`; `- expected_date : date | None`; `- supplier_note : str | None`; `- lines : list[RestockLine]`; `+ add_line(variant_id: int, quantity: int) : None`; `+ confirm(expected_date: date) : None`; `+ reject(reason: str) : None`; `+ mark_received() : None`
- **RestockLine** «entity»
  - `- variant_id : int`; `- quantity : int`
- **MovementReason** *(enum)* «enumeration»
  - `INITIAL`; `SALE`; `RETURN`; `RESTOCK`; `ADJUSTMENT`
- **RestockStatus** *(enum)* «enumeration»
  - `SENT`; `CONFIRMED`; `REJECTED`; `RECEIVED`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `Allocation`, `ProductVariant`, `Shipment`, `Style`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Style | 0..* | Association (có hướng) | 0..1 | Supplier | supplier_id |
| StockLevel | 0..* | Association (có hướng) | 1 | ProductVariant | variant_id |
| StockLevel | 0..* | Association (có hướng) | 1 | StockLocation | location_id |
| StockMovement | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| StockMovement | 0..* | Association (có hướng) | 1 | StockLocation |  |
| RestockRequest | 1 | Composition (hình thoi ở phía `RestockRequest`) | 1..* | RestockLine | lines |
| RestockRequest | 0..* | Association (có hướng) | 1 | Supplier |  |
| RestockLine | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| Allocation | 0..* | Association (có hướng) | 1 | StockLocation |  |
| Shipment | 0..* | Association (có hướng) | 1 | StockLocation |  |
| StockMovement |  | Dependency |  | MovementReason |  |
| RestockRequest |  | Dependency |  | RestockStatus |  |

### Hình 4.22 — `d4_design_sales.png`

*Chú thích trong bài:* Design class diagram — cart, order, promotion and payment

- **Loại diagram trong VP:** Class Diagram (mức thiết kế)
- **File nháp:** `design/diagrams/d4_design_sales.puml`

**Phần tử và thuộc tính / phương thức:**

- **Cart** «entity»
  - `- cart_id : int | None`; `- customer_id : int`; `- items : list[CartItem]`; `- updated_at : datetime`; `+ add_item(variant: ProductVariant, quantity: int) : None`; `+ update_quantity(variant_id: int, quantity: int) : None`; `+ remove_item(variant_id: int) : None`; `+ subtotal() : int`; `+ is_empty() : bool`; `+ clear() : None`
- **CartItem** «entity»
  - `- variant_id : int`; `- sku : str`; `- style_id : int`; `- unit_price_vnd : int`; `- quantity : int`; `+ line_total() : int`
- **Order** «entity»
  - `- order_id : int | None`; `- order_no : str`; `- customer_id : int`; `- status : OrderStatus`; `- placed_at : datetime`; `- lines : list[OrderLine]`; `- subtotal_vnd : int`; `- discount_vnd : int`; `- shipping_fee_vnd : int`; `- grand_total_vnd : int`; `- voucher_id : int | None`; `- note : str | None`; `- shipping_address : Address`; `- delivery_service : str | None`; `- confirmed_at : datetime | None`; `- delivered_at : datetime | None`; `- cancelled_at : datetime | None`; `- cancel_reason : str | None`; `+ add_line(variant: ProductVariant, quantity: int) : OrderLine`; `+ set_delivery(service: str, fee_vnd: int) : None`; `+ apply_discount(amount_vnd: int) : None`; `+ calculate_totals() : None`; `+ confirm_payment(at: datetime) : None`; `+ change_status(new_status: OrderStatus, at: datetime) : None`; `+ can_cancel() : bool`; `+ cancel(reason: str, at: datetime) : None`; `+ is_paid() : bool`
- **OrderLine** «entity»
  - `- order_line_id : int | None`; `- variant_id : int`; `- sku : str`; `- quantity : int`; `- unit_price_vnd : int`; `- discount_vnd : int`; `- allocations : list[Allocation]`; `+ line_total() : int`; `+ allocate(location_id: int, quantity: int) : None`
- **Allocation** «entity»
  - `- location_id : int`; `- quantity : int`
- **Promotion** «entity»
  - `- promotion_id : int | None`; `- name : str`; `- promo_type : PromotionType`; `- discount_type : DiscountType`; `- discount_value : int`; `- min_order_vnd : int`; `- starts_at : datetime`; `- ends_at : datetime`; `- status : PromotionStatus`; `- style_ids : set[int]`; `+ is_active(at: datetime) : bool`; `+ applies_to(style_id: int) : bool`; `+ discount_for(eligible_subtotal_vnd: int, order_subtotal_vnd: int) : int`
- **Voucher** «entity»
  - `- voucher_id : int | None`; `- promotion_id : int`; `- code : str`; `- usage_limit : int`; `- used_count : int`; `+ is_redeemable() : bool`; `+ redeem() : None`
- **Payment** «entity»
  - `- payment_id : int | None`; `- order_id : int`; `- return_id : int | None`; `- kind : PaymentKind`; `- method : PaymentMethodType`; `- amount_vnd : int`; `- status : PaymentStatus`; `- transaction_ref : str | None`; `- failure_reason : str | None`; `- created_at : datetime`; `+ mark_succeeded(transaction_ref: str) : None`; `+ mark_failed(reason: str) : None`
- **OrderStatus** *(enum)* «enumeration»
  - `PENDING_PAYMENT`; `CONFIRMED`; `PROCESSING`; `PARTIALLY_SHIPPED`; `SHIPPED`; `DELIVERED`; `COMPLETED`; `CANCELLED`
- **PaymentKind** *(enum)* «enumeration»
  - `CHARGE`; `REFUND`
- **PaymentStatus** *(enum)* «enumeration»
  - `PENDING`; `SUCCEEDED`; `FAILED`
- **PromotionType** *(enum)* «enumeration»
  - `CLEARANCE`; `FLASH_SALE`; `LOYALTY`
- **DiscountType** *(enum)* «enumeration»
  - `PERCENT`; `FIXED_AMOUNT`
- **PromotionStatus** *(enum)* «enumeration»
  - `DRAFT`; `ACTIVE`; `ENDED`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `Address`, `Customer`, `ProductVariant`, `ReturnItem`, `ReturnRequest`, `Review`, `Shipment`, `ShipmentLine`, `StockLocation`, `Style`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Cart | 1 | Composition (hình thoi ở phía `Cart`) | 0..* | CartItem | items |
| Cart | 0..1 | Association (có hướng) | 1 | Customer |  |
| CartItem | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| Order | 0..* | Association (có hướng) | 1 | Customer |  |
| Order | 1 | Composition (hình thoi ở phía `Order`) | 1..* | OrderLine | lines |
| OrderLine | 1 | Composition (hình thoi ở phía `OrderLine`) | 0..* | Allocation | allocations |
| Allocation | 0..* | Association (có hướng) | 1 | StockLocation |  |
| OrderLine | 0..* | Association (có hướng) | 1 | ProductVariant |  |
| Order | 1 | Composition (hình thoi ở phía `Order`) | 1 | Address | shipping_address (snapshot) |
| Order | 0..* | Association (có hướng) | 0..1 | Voucher |  |
| Promotion | 1 | Composition (hình thoi ở phía `Promotion`) | 0..* | Voucher |  |
| Promotion | 0..* | Association (có hướng) | 0..* | Style | style_ids |
| Payment | 0..* | Association (có hướng) | 1 | Order |  |
| Payment | 0..* | Association (có hướng) | 0..1 | ReturnRequest | refund for |
| Shipment | 0..* | Association (có hướng) | 1 | Order |  |
| ShipmentLine | 0..* | Association (có hướng) | 1 | OrderLine |  |
| ReturnRequest | 0..* | Association (có hướng) | 1 | Order |  |
| ReturnItem | 0..* | Association (có hướng) | 1 | OrderLine |  |
| Review | 0..1 | Association (có hướng) | 0..1 | OrderLine | verifies |
| Order |  | Dependency |  | OrderStatus |  |
| Promotion |  | Dependency |  | PromotionType |  |
| Promotion |  | Dependency |  | DiscountType |  |
| Promotion |  | Dependency |  | PromotionStatus |  |
| Payment |  | Dependency |  | PaymentKind |  |
| Payment |  | Dependency |  | PaymentStatus |  |

### Hình 4.23 — `d5_design_shipping_returns.png`

*Chú thích trong bài:* Design class diagram — shipments, returns and exchanges

- **Loại diagram trong VP:** Class Diagram (mức thiết kế)
- **File nháp:** `design/diagrams/d5_design_shipping_returns.puml`

**Phần tử và thuộc tính / phương thức:**

- **Shipment** «entity»
  - `- shipment_id : int | None`; `- order_id : int`; `- return_id : int | None`; `- direction : ShipmentDirection`; `- location_id : int`; `- carrier : str`; `- service_level : str | None`; `- tracking_no : str | None`; `- fee_vnd : int`; `- status : ShipmentStatus`; `- lines : list[ShipmentLine]`; `- events : list[ShipmentEvent]`; `- delivered_at : datetime | None`; `+ record_event(status: ShipmentStatus, at: datetime, note: str | None) : ShipmentEvent`; `+ is_delivered() : bool`
- **ShipmentLine** «entity»
  - `- order_line_id : int`; `- quantity : int`
- **ShipmentEvent** «entity»
  - `- status : ShipmentStatus`; `- occurred_at : datetime`; `- note : str | None`
- **ReturnRequest** «entity»
  - `- return_id : int | None`; `- return_no : str`; `- order_id : int`; `- customer_id : int`; `- return_type : ReturnType`; `- reason_code : ReturnReason`; `- reason_detail : str | None`; `- desired_resolution : Resolution`; `- status : ReturnStatus`; `- requested_at : datetime`; `- decided_at : datetime | None`; `- decided_by : int | None`; `- decision_note : str | None`; `- items : list[ReturnItem]`; `- evidence : list[ReturnEvidence]`; `+ is_within_period(delivered_at: datetime, now: datetime, days: int) : bool`; `+ authorise(staff_id: int, at: datetime) : None`; `+ reject(staff_id: int, reason: str, at: datetime) : None`; `+ mark_in_transit() : None`; `+ record_inspection(order_line_id: int, passed: bool, note: str | None, staff_id: int, at: datetime) : ReturnItem`; `+ all_inspected() : bool`; `+ resolve() : Resolution`; `+ close(note: str) : None`
- **ReturnItem** «entity»
  - `- return_item_id : int | None`; `- order_line_id : int`; `- variant_id : int`; `- quantity : int`; `- exchange_variant_id : int | None`; `- inspection_result : InspectionResult`; `- inspection_note : str | None`; `- inspected_by : int | None`; `+ passed() : bool`
- **ReturnEvidence** «entity»
  - `- url : str`; `- media_type : MediaType`
- **ShipmentDirection** *(enum)* «enumeration»
  - `OUTBOUND`; `RETURN_PICKUP`
- **ShipmentStatus** *(enum)* «enumeration»
  - `REQUESTED`; `PICKED_UP`; `IN_TRANSIT`; `DELIVERED`; `FAILED`
- **ReturnType** *(enum)* «enumeration»
  - `RETURN`; `EXCHANGE`
- **ReturnReason** *(enum)* «enumeration»
  - `TOO_SMALL`; `TOO_LARGE`; `DEFECT`; `NOT_AS_DESCRIBED`; `WRONG_ITEM`; `CHANGED_MIND`
- **Resolution** *(enum)* «enumeration»
  - `REFUND`; `EXCHANGE`
- **ReturnStatus** *(enum)* «enumeration»
  - `SUBMITTED`; `REJECTED`; `AUTHORISED`; `IN_TRANSIT`; `INSPECTED`; `REFUNDED`; `EXCHANGED`; `CLOSED`
- **InspectionResult** *(enum)* «enumeration»
  - `PENDING`; `PASSED`; `FAILED`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `Order`, `OrderLine`, `Payment`, `ProductVariant`, `StockLocation`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Payment | 0..* | Association (có hướng) | 0..1 | ReturnRequest | refund for |
| Shipment | 0..* | Association (có hướng) | 1 | Order |  |
| Shipment | 1 | Composition (hình thoi ở phía `Shipment`) | 1..* | ShipmentLine | lines |
| Shipment | 1 | Composition (hình thoi ở phía `Shipment`) | 0..* | ShipmentEvent | events |
| ShipmentLine | 0..* | Association (có hướng) | 1 | OrderLine |  |
| Shipment | 0..* | Association (có hướng) | 1 | StockLocation |  |
| ReturnRequest | 0..* | Association (có hướng) | 1 | Order |  |
| ReturnRequest | 1 | Composition (hình thoi ở phía `ReturnRequest`) | 1..* | ReturnItem | items |
| ReturnRequest | 1 | Composition (hình thoi ở phía `ReturnRequest`) | 0..* | ReturnEvidence | evidence |
| ReturnItem | 0..* | Association (có hướng) | 1 | OrderLine |  |
| ReturnItem | 0..* | Association (có hướng) | 0..1 | ProductVariant | exchange to |
| Shipment |  | Dependency |  | ShipmentDirection |  |
| Shipment |  | Dependency |  | ShipmentStatus |  |
| ShipmentEvent |  | Dependency |  | ShipmentStatus |  |
| ReturnRequest |  | Dependency |  | ReturnType |  |
| ReturnRequest |  | Dependency |  | ReturnReason |  |
| ReturnRequest |  | Dependency |  | Resolution |  |
| ReturnRequest |  | Dependency |  | ReturnStatus |  |
| ReturnItem |  | Dependency |  | InspectionResult |  |

### Hình 4.24 — `d6_design_reviews_assistant.png`

*Chú thích trong bài:* Design class diagram — reviews and assistant log

- **Loại diagram trong VP:** Class Diagram (mức thiết kế)
- **File nháp:** `design/diagrams/d6_design_reviews_assistant.puml`

**Phần tử và thuộc tính / phương thức:**

- **Review** «entity»
  - `- review_id : int | None`; `- style_id : int`; `- variant_id : int | None`; `- customer_id : int | None`; `- order_line_id : int | None`; `- rating : int`; `- body : str`; `- size_purchased : str | None`; `- fit_vote : FitVote | None`; `- verified_purchase : bool`; `- origin : ReviewOrigin`; `- status : ReviewStatus`; `- moderation_note : str | None`; `- content_hash : str`; `- created_at : datetime`; `+ approve(staff_id: int | None) : None`; `+ reject(staff_id: int, note: str) : None`; `+ hold(note: str) : None`; `+ is_counted(origins: set[ReviewOrigin]) : bool`
- **AssistantTurn** «entity»
  - `- turn_id : int | None`; `- style_id : int | None`; `- customer_id : int | None`; `- question_redacted : str`; `- mode : AnswerMode`; `- prompt_version : str`; `- model_name : str | None`; `- latency_ms : int`; `- events : list[GroundingEvent]`; `- created_at : datetime`; `+ log_intervention(check_name: str, removed_text: str) : None`
- **GroundingEvent** «entity»
  - `- check_name : str`; `- removed_text : str`
- **FitVote** *(enum)* «enumeration»
  - `RUNS_SMALL`; `TRUE_TO_SIZE`; `RUNS_LARGE`
- **ReviewOrigin** *(enum)* «enumeration»
  - `CUSTOMER`; `IMPORTED_SOURCE`; `INTERNAL_TEST`
- **ReviewStatus** *(enum)* «enumeration»
  - `PENDING`; `APPROVED`; `REJECTED`
- **AnswerMode** *(enum)* «enumeration»
  - `MODEL`; `BASIC`

**Phần tử chỉ hiển thị tên (thuộc nhóm khác, không cần liệt kê thuộc tính):** `Customer`, `OrderLine`, `Style`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| Review | 0..* | Association (có hướng) | 1 | Style |  |
| Review | 0..* | Association (có hướng) | 0..1 | Customer |  |
| Review | 0..1 | Association (có hướng) | 0..1 | OrderLine | verifies |
| AssistantTurn | 1 | Composition (hình thoi ở phía `AssistantTurn`) | 0..* | GroundingEvent | events |
| AssistantTurn | 0..* | Association (có hướng) | 0..1 | Style |  |
| Review |  | Dependency |  | FitVote |  |
| Review |  | Dependency |  | ReviewOrigin |  |
| Review |  | Dependency |  | ReviewStatus |  |
| AssistantTurn |  | Dependency |  | AnswerMode |  |

### Hình 4.25 — `d7_state_order.png`

*Chú thích trong bài:* State machine of Order

- **Loại diagram trong VP:** State Machine Diagram
- **File nháp:** `design/diagrams/d7_state_order.puml`

**Các trạng thái (State):** `CANCELLED`, `COMPLETED`, `CONFIRMED`, `DELIVERED`, `PARTIALLY_SHIPPED`, `PENDING_PAYMENT`, `PROCESSING`, `SHIPPED`

Thêm 1 *Initial Pseudo State* và 1 *Final State*.

| Từ | Đến | Transition (trigger [guard] / effect) |
|---|---|---|
| Initial | PENDING_PAYMENT | place_order() [stock reserved] |
| PENDING_PAYMENT | CONFIRMED | confirm_payment() [payment succeeded] / commit stock, request shipments |
| PENDING_PAYMENT | CANCELLED | cancel() / expire_unpaid_orders() / release reservation |
| CONFIRMED | PROCESSING | verify_order() (Sales Staff) or first carrier event |
| CONFIRMED | CANCELLED | cancel() / stock back, refund |
| PROCESSING | PARTIALLY_SHIPPED | some parcels picked up |
| PROCESSING | SHIPPED | all parcels picked up |
| PROCESSING | CANCELLED | cancel() / stock back, refund |
| PARTIALLY_SHIPPED | SHIPPED | last parcel picked up |
| SHIPPED | DELIVERED | all parcels delivered |
| DELIVERED | COMPLETED | confirm_received() (UC12) |
| COMPLETED | Final |  |
| CANCELLED | Final |  |

### Hình 4.26 — `d8_state_return.png`

*Chú thích trong bài:* State machine of ReturnRequest

- **Loại diagram trong VP:** State Machine Diagram
- **File nháp:** `design/diagrams/d8_state_return.puml`

**Các trạng thái (State):** `AUTHORISED`, `CLOSED`, `EXCHANGED`, `INSPECTED`, `IN_TRANSIT`, `REFUNDED`, `REJECTED`, `SUBMITTED`

Thêm 1 *Initial Pseudo State* và 1 *Final State*.

| Từ | Đến | Transition (trigger [guard] / effect) |
|---|---|---|
| Initial | SUBMITTED | submit_request() |
| SUBMITTED | REJECTED | reject() [outside return period or not eligible] |
| SUBMITTED | AUTHORISED | authorise() |
| AUTHORISED | IN_TRANSIT | mark_in_transit() / pickup requested |
| IN_TRANSIT | INSPECTED | record_inspection() [all items inspected] / passed items restocked |
| INSPECTED | REFUNDED | resolve() [refund, &gt;= 1 item passed] / refund via Payment Service |
| INSPECTED | EXCHANGED | resolve() [exchange, replacement available] / replacement shipped |
| INSPECTED | CLOSED | close() [no item passed] |
| REJECTED | Final |  |
| REFUNDED | Final |  |
| EXCHANGED | Final |  |
| CLOSED | Final |  |


## 4.4 Layers + Classes + Relations

`l0` là tổng quan 5 package-tầng với tên các lớp và các phụ thuộc giữa tầng (presentation → application → domain/data/integration; data → domain; integration → domain). `l1`–`l5` là các lát cắt theo use case, mỗi lớp chỉ hiện phương thức liên quan (tham số chỉ ghi tên). Association có hướng ghi tên thuộc tính tham chiếu (ví dụ `CheckoutService --> OrderRepository : orders`), dependency ghi các lớp domain được dùng.

### Hình 4.27 — `l0_layers_overview.png`

*Chú thích trong bài:* Layered architecture — packages, classes and allowed dependencies

- **Loại diagram trong VP:** Class Diagram có Package theo tầng
- **File nháp:** `design/diagrams/l0_layers_overview.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Presentation layer / abc_fashion.presentation`; `Application layer (use-case services and intelligence) / abc_fashion.application`; `Data access layer / abc_fashion.data`; `Integration layer (external systems and AI models) / abc_fashion.integration`; `Domain layer (problem domain) / abc_fashion.domain`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Presentation layer / abc_fashion.presentation*: `AccountController`, `CatalogController`, `CartController`, `CheckoutController`, `OrderController`, `ReturnController`, `ReviewController`, `BackOfficeController`
- *Application layer (use-case services and intelligence) / abc_fashion.application*: `AccountService`, `CatalogService`, `SearchService`, `QueryService`, `RankingService`, `CartService`, `CheckoutService`, `OrderService`, `InventoryService`, `ShippingService`, `ReturnService`, `ReviewService`, `ReviewModerator`, `ReviewSummariser`, `PromotionService`, `ReportService`, `NotificationService`, `AssistantService`, `AssistantEngine`, `BasicAssistantEngine`
- *Data access layer / abc_fashion.data*: `Database`, `AccountRepository`, `CatalogRepository`, `InventoryRepository`, `CartRepository`, `OrderRepository`, `ReturnRepository`, `ReviewRepository`, `PromotionRepository`, `ReportRepository`, `LogRepository`, `VectorIndex`
- *Integration layer (external systems and AI models) / abc_fashion.integration*: `PaymentGateway`, `SandboxPaymentGateway`, `ShippingGateway`, `SandboxShippingGateway`, `NotificationGateway`, `OutboxNotificationGateway`, `SupplierGateway`, `EmailSupplierGateway`, `SpeechRecognizer`, `ImageEncoder`, `LanguageModelClient`
- *Domain layer (problem domain) / abc_fashion.domain*: `UserAccount`, `Customer`, `StaffMember`, `Address`, `PaymentMethod`, `Category`, `Collection`, `Style`, `MaterialComponent`, `SizeChartEntry`, `ProductVariant`, `ProductMedia`, `StockLocation`, `StockLevel`, `StockMovement`, `Supplier`, `RestockRequest`, `RestockLine`, `Cart`, `CartItem`, `Order`, `OrderLine`, `Allocation`, `Promotion`, `Voucher`, `Payment`, `Shipment`, `ShipmentLine`, `ShipmentEvent`, `ReturnRequest`, `ReturnItem`, `ReturnEvidence`, `Review`, `AssistantTurn`, `GroundingEvent`, `AuditLogEntry`, `Notification`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| package Presentation layer |  | Dependency |  | package Application layer (use-case services and intelligence) | «use» |
| package Presentation layer |  | Dependency |  | package Domain layer (problem domain) | «use» |
| package Application layer (use-case services and intelligence) |  | Dependency |  | package Domain layer (problem domain) | «use» |
| package Application layer (use-case services and intelligence) |  | Dependency |  | package Data access layer | «use» |
| package Application layer (use-case services and intelligence) |  | Dependency |  | package Integration layer (external systems and AI models) | «use» |
| package Data access layer |  | Dependency |  | package Domain layer (problem domain) | «use» |
| package Integration layer (external systems and AI models) |  | Dependency |  | package Domain layer (problem domain) | «use» |

### Hình 4.28 — `l1_layers_checkout.png`

*Chú thích trong bài:* Layered class diagram — UC08 Place Order / Checkout

- **Loại diagram trong VP:** Class Diagram có Package theo tầng
- **File nháp:** `design/diagrams/l1_layers_checkout.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Presentation layer`; `Application layer (use-case services and intelligence)`; `Data access layer`; `Integration layer (external systems and AI models)`; `Domain layer (problem domain)`

**Phần tử và thuộc tính / phương thức:**

- **CheckoutController** «controller» — package *Presentation layer*
  - `+ validate(token) : dict`; `+ delivery_options(token, address_id) : list[dict]`; `+ place_order(token, body) : dict`; `+ payment_callback(body) : dict`
- **CheckoutService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ validate_cart(customer_id) : AvailabilityCheck`; `+ delivery_options(customer_id, address_id) : list[DeliveryQuote]`; `+ preview_totals(customer_id, voucher_code, shipping_fee_vnd) : Totals`; `+ place_order(customer_id, address_id, delivery, method, voucher_code, note) : PaymentRedirect`; `+ confirm_payment(transaction_ref, succeeded, reason) : Order`; `+ retry_payment(customer_id, order_no, method) : PaymentRedirect`; `+ expire_unpaid_orders(older_than) : int`
- **InventoryService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ reserve_for_order(order) : None`; `+ commit_order(order) : None`; `+ release_order(order) : None`
- **PromotionService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ evaluate(code, items, at) : Discount`
- **ShippingService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ quote(address, item_count) : list[DeliveryQuote]`; `+ create_outbound_shipments(order) : list[Shipment]`
- **NotificationService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ notify(customer_id, event_type, message) : Notification`
- **CartRepository** «repository» — package *Data access layer*
  - `+ get_or_create(customer_id) : Cart`; `+ save(cart) : None`
- **OrderRepository** «repository» — package *Data access layer*
  - `+ add(order) : Order`; `+ get_by_no(order_no, for_update) : Order | None`; `+ save(order) : None`; `+ add_payment(payment) : Payment`; `+ get_payment_by_ref(transaction_ref, for_update) : Payment | None`; `+ save_payment(payment) : None`; `+ add_shipment(shipment) : Shipment`
- **InventoryRepository** «repository» — package *Data access layer*
  - `+ levels_for_variant(variant_id, for_update) : list[StockLevel]`; `+ get_level(variant_id, location_id, for_update) : StockLevel | None`; `+ save_level(level) : None`; `+ add_movement(movement) : None`; `+ availability(variant_ids) : dict[int, int]`
- **PromotionRepository** «repository» — package *Data access layer*
  - `+ get_voucher_by_code(code, for_update) : Voucher | None`; `+ save_voucher(voucher) : None`
- **PaymentGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ create_payment(order_no, amount_vnd, method) : PaymentRedirect`; `+ refund(transaction_ref, amount_vnd) : str`; `+ tokenize_method(provider, method_type, card_number) : tuple[str, str]`
- **ShippingGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ quote(city, item_count) : list[DeliveryQuote]`; `+ create_shipment(reference, from_location, to_address, service_level) : str`; `+ request_pickup(reference, from_address, to_location) : str`
- **NotificationGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ send(channel, to, message) : bool`
- **Order** «entity» — package *Domain layer (problem domain)*
  - `+ add_line(variant, quantity) : OrderLine`; `+ set_delivery(service, fee_vnd) : None`; `+ apply_discount(amount_vnd) : None`; `+ confirm_payment(at) : None`
- **StockLevel** «entity» — package *Domain layer (problem domain)*
  - `+ reserve(quantity) : None`; `+ release(quantity) : None`; `+ commit_sale(quantity) : None`
- **Payment** «entity» — package *Domain layer (problem domain)*
  - `+ mark_succeeded(transaction_ref) : None`; `+ mark_failed(reason) : None`
- **Voucher** «entity» — package *Domain layer (problem domain)*
  - `+ redeem() : None`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Domain layer (problem domain)*: `Cart`, `Shipment`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| CheckoutController |  | Association (có hướng) |  | CheckoutService | checkout |
| CheckoutService |  | Association (có hướng) |  | CartRepository | carts |
| CheckoutService |  | Association (có hướng) |  | OrderRepository | orders |
| CheckoutService |  | Association (có hướng) |  | InventoryService | inventory |
| CheckoutService |  | Association (có hướng) |  | PromotionService | promotions |
| CheckoutService |  | Association (có hướng) |  | PromotionRepository | promotion_repo |
| CheckoutService |  | Association (có hướng) |  | ShippingService | shipping |
| CheckoutService |  | Association (có hướng) |  | PaymentGateway | payments |
| CheckoutService |  | Association (có hướng) |  | NotificationService | notifier |
| InventoryService |  | Association (có hướng) |  | InventoryRepository | inventory |
| PromotionService |  | Association (có hướng) |  | PromotionRepository | promotions |
| ShippingService |  | Association (có hướng) |  | OrderRepository | orders |
| ShippingService |  | Association (có hướng) |  | InventoryRepository | inventory |
| ShippingService |  | Association (có hướng) |  | ShippingGateway | gateway |
| NotificationService |  | Association (có hướng) |  | NotificationGateway | gateway |
| CheckoutService |  | Dependency |  | Order |  |
| InventoryService |  | Dependency |  | Order |  |
| InventoryService |  | Dependency |  | StockLevel |  |
| PromotionService |  | Dependency |  | Voucher |  |
| ShippingService |  | Dependency |  | Order |  |
| ShippingService |  | Dependency |  | Shipment |  |

### Hình 4.29 — `l2_layers_returns.png`

*Chú thích trong bài:* Layered class diagram — UC14 Request and UC18 Process Return / Exchange

- **Loại diagram trong VP:** Class Diagram có Package theo tầng
- **File nháp:** `design/diagrams/l2_layers_returns.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Presentation layer`; `Application layer (use-case services and intelligence)`; `Data access layer`; `Integration layer (external systems and AI models)`; `Domain layer (problem domain)`

**Phần tử và thuộc tính / phương thức:**

- **ReturnController** «controller» — package *Presentation layer*
  - `+ submit(token, body) : dict`; `+ pending(token) : list[dict]`; `+ authorise(token, return_no) : dict`; `+ inspect(token, return_no, body) : dict`; `+ resolve(token, return_no) : dict`
- **ReturnService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ submit_request(customer_id, order_no, items, return_type, reason_code, detail, evidence_urls) : ReturnRequest`; `+ list_pending(staff) : list[ReturnRequest]`; `+ authorise(staff, return_no) : ReturnRequest`; `+ reject(staff, return_no, reason) : ReturnRequest`; `+ record_inspection(staff, return_no, order_line_id, passed, note) : ReturnRequest`; `+ resolve(staff, return_no) : ReturnRequest`; `+ close(staff, return_no, note) : ReturnRequest`
- **InventoryService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ restock_returned_item(variant_id, location_id, quantity, return_id) : None`; `+ reserve_and_commit(variant_id, quantity, reference_type, reference_id) : int`
- **ShippingService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ request_return_pickup(request, order) : Shipment`; `+ ship_replacements(order, request, lines_by_location) : list[Shipment]`
- **NotificationService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ notify(customer_id, event_type, message) : Notification`
- **ReturnRepository** «repository» — package *Data access layer*
  - `+ add(request) : ReturnRequest`; `+ get_by_no(return_no, for_update) : ReturnRequest | None`; `+ list_by_status(statuses) : list[ReturnRequest]`; `+ save(request) : None`; `+ returned_quantity(order_line_id) : int`
- **OrderRepository** «repository» — package *Data access layer*
  - `+ get(order_id) : Order | None`; `+ add_payment(payment) : Payment`; `+ payments_for(order_id) : list[Payment]`; `+ shipments_for(order_id) : list[Shipment]`
- **InventoryRepository** «repository» — package *Data access layer*
  - `+ get_level(variant_id, location_id, for_update) : StockLevel | None`; `+ save_level(level) : None`; `+ add_movement(movement) : None`
- **PaymentGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ refund(transaction_ref, amount_vnd) : str`
- **ShippingGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ create_shipment(reference, from_location, to_address, service_level) : str`; `+ request_pickup(reference, from_address, to_location) : str`
- **ReturnRequest** «entity» — package *Domain layer (problem domain)*
  - `+ is_within_period(delivered_at, now, days) : bool`; `+ authorise(staff_id, at) : None`; `+ reject(staff_id, reason, at) : None`; `+ record_inspection(order_line_id, passed, note, staff_id, at) : ReturnItem`; `+ resolve() : Resolution`; `+ close(note) : None`
- **ReturnItem** «entity» — package *Domain layer (problem domain)*
  - `+ passed() : bool`
- **StockLevel** «entity» — package *Domain layer (problem domain)*
  - `+ receive(quantity) : None`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Domain layer (problem domain)*: `Payment`, `Order`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| ReturnController |  | Association (có hướng) |  | ReturnService | returns |
| ReturnService |  | Association (có hướng) |  | ReturnRepository | returns |
| ReturnService |  | Association (có hướng) |  | OrderRepository | orders |
| ReturnService |  | Association (có hướng) |  | InventoryService | inventory |
| ReturnService |  | Association (có hướng) |  | ShippingService | shipping |
| ReturnService |  | Association (có hướng) |  | PaymentGateway | payments |
| ReturnService |  | Association (có hướng) |  | NotificationService | notifier |
| InventoryService |  | Association (có hướng) |  | InventoryRepository | inventory |
| ShippingService |  | Association (có hướng) |  | OrderRepository | orders |
| ShippingService |  | Association (có hướng) |  | InventoryRepository | inventory |
| ShippingService |  | Association (có hướng) |  | ShippingGateway | gateway |
| ReturnRequest | 1 | Composition (hình thoi ở phía `ReturnRequest`) | 1..* | ReturnItem | items |
| ReturnService |  | Dependency |  | ReturnRequest |  |
| InventoryService |  | Dependency |  | Order |  |
| InventoryService |  | Dependency |  | StockLevel |  |
| ShippingService |  | Dependency |  | Order |  |
| ShippingService |  | Dependency |  | ReturnRequest |  |

### Hình 4.30 — `l3_layers_catalogue_search_assistant.png`

*Chú thích trong bài:* Layered class diagram — catalogue (UC04, UC06), search (UC05) and AI assistant (UC32)

- **Loại diagram trong VP:** Class Diagram có Package theo tầng
- **File nháp:** `design/diagrams/l3_layers_catalogue_search_assistant.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Presentation layer`; `Application layer (use-case services and intelligence)`; `Data access layer`; `Integration layer (external systems and AI models)`; `Domain layer (problem domain)`

**Phần tử và thuộc tính / phương thức:**

- **CatalogController** «controller» — package *Presentation layer*
  - `+ browse(category, colour, size, max_price) : list[dict]`; `+ product(code) : dict`; `+ search(q) : dict`; `+ ask_assistant(code, body) : dict`
- **CatalogService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ browse(category_slug, collection_id, colour, size_label, max_price_vnd) : list[ProductCard]`; `+ get_product_detail(style_code) : ProductDetail`
- **SearchService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ search_text(text) : SearchResult`; `+ search_voice(pcm16k) : SearchResult`; `+ search_image(image_bytes, text, lam_t, lam_i) : SearchResult`
- **QueryService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ parse(text, query_type) : SearchQuery`
- **RankingService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ business_score(in_stock, price_vnd) : float`; `+ rank(candidates, lam_t, lam_i, top_k) : list[Candidate]`
- **ReviewService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ summarise(style_id) : ReviewSummary`
- **ReviewSummariser** «service» — package *Application layer (use-case services and intelligence)*
  - `+ summarise(reviews) : ReviewSummary`; `+ fit_consensus(reviews) : FitConsensus`
- **ReviewModerator** «service» — package *Application layer (use-case services and intelligence)*
  - `+ check(body) : tuple[bool, str | None]`; `+ redact(text) : str`
- **AssistantService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ ask(style_code, question, customer_id) : AssistantAnswer`
- **AssistantEngine** *(interface)* — package *Application layer (use-case services and intelligence)*
  - `+ answer(style, summary, question) : AssistantAnswer`
- **CatalogRepository** «repository» — package *Data access layer*
  - `+ get_style_by_code(code) : Style | None`; `+ list_styles(category_slug, collection_id, colour, size_label, max_price_vnd, published_only) : list[Style]`; `+ get_category_by_slug(slug) : Category | None`
- **InventoryRepository** «repository» — package *Data access layer*
  - `+ availability(variant_ids) : dict[int, int]`
- **ReviewRepository** «repository» — package *Data access layer*
  - `+ list_for_style(style_id, statuses) : list[Review]`
- **VectorIndex** «repository» — package *Data access layer*
  - `+ vectors(kind) : dict[int, list[list[float]]]`
- **LogRepository** «repository» — package *Data access layer*
  - `+ add_assistant_turn(turn) : AssistantTurn`
- **SpeechRecognizer** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ transcribe(pcm16k) : str`
- **ImageEncoder** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ encode_image(image_bytes) : list[float]`; `+ classify_group(vector) : str | None`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Application layer (use-case services and intelligence)*: `BasicAssistantEngine`
- *Domain layer (problem domain)*: `Style`, `Review`, `AssistantTurn`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| CatalogController |  | Association (có hướng) |  | CatalogService | catalog |
| CatalogController |  | Association (có hướng) |  | SearchService | search_service |
| CatalogController |  | Association (có hướng) |  | AssistantService | assistant |
| CatalogService |  | Association (có hướng) |  | CatalogRepository | catalog |
| CatalogService |  | Association (có hướng) |  | InventoryRepository | inventory |
| CatalogService |  | Association (có hướng) |  | ReviewService | reviews |
| CatalogService |  | Association (có hướng) |  | LogRepository | logs |
| SearchService |  | Association (có hướng) |  | CatalogRepository | catalog |
| SearchService |  | Association (có hướng) |  | InventoryRepository | inventory |
| SearchService |  | Association (có hướng) |  | QueryService | queries |
| SearchService |  | Association (có hướng) |  | RankingService | ranking |
| SearchService |  | Association (có hướng) |  | SpeechRecognizer | speech |
| SearchService |  | Association (có hướng) |  | ImageEncoder | images |
| SearchService |  | Association (có hướng) |  | VectorIndex | index |
| ReviewService |  | Association (có hướng) |  | ReviewRepository | reviews |
| ReviewService |  | Association (có hướng) |  | CatalogRepository | catalog |
| ReviewService |  | Association (có hướng) |  | ReviewModerator | moderator |
| ReviewService |  | Association (có hướng) |  | ReviewSummariser | summariser |
| AssistantService |  | Association (có hướng) |  | CatalogRepository | catalog |
| AssistantService |  | Association (có hướng) |  | ReviewService | reviews |
| AssistantService |  | Association (có hướng) |  | ReviewModerator | moderator |
| AssistantService |  | Association (có hướng) |  | AssistantEngine | engine |
| AssistantService |  | Association (có hướng) |  | LogRepository | logs |
| BasicAssistantEngine | | Realization (lớp cài đặt → interface) | | AssistantEngine |  |
| CatalogService |  | Dependency |  | Style |  |
| ReviewService |  | Dependency |  | Review |  |
| ReviewSummariser |  | Dependency |  | Review |  |
| AssistantEngine |  | Dependency |  | Style |  |
| BasicAssistantEngine |  | Dependency |  | Style |  |

### Hình 4.31 — `l4_layers_cart_orders.png`

*Chú thích trong bài:* Layered class diagram — shopping cart (UC07) and order management (UC09–UC12, UC22, UC23)

- **Loại diagram trong VP:** Class Diagram có Package theo tầng
- **File nháp:** `design/diagrams/l4_layers_cart_orders.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Presentation layer`; `Application layer (use-case services and intelligence)`; `Data access layer`; `Integration layer (external systems and AI models)`; `Domain layer (problem domain)`

**Phần tử và thuộc tính / phương thức:**

- **CartController** «controller» — package *Presentation layer*
  - `+ view(token) : dict`; `+ add(token, body) : dict`; `+ update(token, sku, body) : dict`; `+ remove(token, sku) : dict`
- **OrderController** «controller» — package *Presentation layer*
  - `+ list_orders(token) : list[dict]`; `+ detail(token, order_no) : dict`; `+ cancel(token, order_no, body) : dict`; `+ confirm_received(token, order_no) : dict`; `+ update_status(token, order_no, body) : dict`; `+ shipping_callback(body) : dict`
- **AccountService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ authenticate(token) : Session`
- **CartService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ get_cart(customer_id) : Cart`; `+ add_item(customer_id, sku, quantity) : Cart`; `+ update_quantity(customer_id, sku, quantity) : Cart`; `+ remove_item(customer_id, sku) : Cart`
- **OrderService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ list_orders(customer_id) : list[Order]`; `+ get_order(customer_id, order_no) : Order`; `+ track_order(customer_id, order_no) : list[Shipment]`; `+ request_cancellation(customer_id, order_no, reason) : Order`; `+ cancel_order(staff, order_no, reason) : Order`; `+ verify_order(staff, order_no) : Order`; `+ update_status(staff, order_no, new_status) : Order`; `+ record_delivery_event(tracking_no, status, occurred_at, note) : Shipment`; `+ confirm_received(customer_id, order_no) : Order`
- **InventoryService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ release_order(order) : None`
- **CartRepository** «repository» — package *Data access layer*
  - `+ get_or_create(customer_id) : Cart`; `+ save(cart) : None`
- **CatalogRepository** «repository» — package *Data access layer*
  - `+ get_variant_by_sku(sku) : ProductVariant | None`
- **InventoryRepository** «repository» — package *Data access layer*
  - `+ availability(variant_ids) : dict[int, int]`
- **OrderRepository** «repository» — package *Data access layer*
  - `+ get_by_no(order_no, for_update) : Order | None`; `+ list_by_customer(customer_id) : list[Order]`; `+ save(order) : None`; `+ get_shipment_by_tracking(tracking_no) : Shipment | None`; `+ save_shipment(shipment) : None`; `+ shipments_for(order_id) : list[Shipment]`
- **PaymentGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ refund(transaction_ref, amount_vnd) : str`
- **Cart** «entity» — package *Domain layer (problem domain)*
  - `+ add_item(variant, quantity) : None`; `+ update_quantity(variant_id, quantity) : None`; `+ remove_item(variant_id) : None`
- **Order** «entity» — package *Domain layer (problem domain)*
  - `+ change_status(new_status, at) : None`; `+ can_cancel() : bool`; `+ cancel(reason, at) : None`
- **Shipment** «entity» — package *Domain layer (problem domain)*
  - `+ record_event(status, at, note) : ShipmentEvent`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Application layer (use-case services and intelligence)*: `NotificationService`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| CartController |  | Association (có hướng) |  | CartService | carts |
| CartController |  | Association (có hướng) |  | AccountService | accounts |
| OrderController |  | Association (có hướng) |  | OrderService | orders |
| OrderController |  | Association (có hướng) |  | AccountService | accounts |
| AccountService |  | Association (có hướng) |  | PaymentGateway | payments |
| CartService |  | Association (có hướng) |  | CartRepository | carts |
| CartService |  | Association (có hướng) |  | CatalogRepository | catalog |
| CartService |  | Association (có hướng) |  | InventoryRepository | inventory |
| OrderService |  | Association (có hướng) |  | OrderRepository | orders |
| OrderService |  | Association (có hướng) |  | InventoryService | inventory |
| OrderService |  | Association (có hướng) |  | PaymentGateway | payments |
| OrderService |  | Association (có hướng) |  | NotificationService | notifier |
| InventoryService |  | Association (có hướng) |  | InventoryRepository | inventory |
| InventoryService |  | Association (có hướng) |  | CatalogRepository | catalog |
| CartService |  | Dependency |  | Cart |  |
| OrderService |  | Dependency |  | Order |  |
| OrderService |  | Dependency |  | Shipment |  |
| InventoryService |  | Dependency |  | Order |  |

### Hình 4.32 — `l5_layers_backoffice.png`

*Chú thích trong bài:* Layered class diagram — accounts (UC01–UC03, UC20), inventory (UC17), promotions (UC15) and reports (UC16, UC24)

- **Loại diagram trong VP:** Class Diagram có Package theo tầng
- **File nháp:** `design/diagrams/l5_layers_backoffice.puml`

**Package (vẽ bằng Package trong VP, mỗi package một màu như bản nháp):** `Presentation layer`; `Application layer (use-case services and intelligence)`; `Data access layer`; `Integration layer (external systems and AI models)`; `Domain layer (problem domain)`

**Phần tử và thuộc tính / phương thức:**

- **AccountController** «controller» — package *Presentation layer*
  - `+ register(body) : dict`; `+ login(body) : dict`; `+ add_address(token, body) : dict`
- **BackOfficeController** «controller» — package *Presentation layer*
  - `+ stock(token, location_id) : list[dict]`; `+ adjust_stock(token, body) : dict`; `+ restock(token, body) : dict`; `+ sales_report(token, date_from, date_to) : list[dict]`
- **AccountService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ register(email, password, full_name, phone) : Customer`; `+ login(email, password) : Session`; `+ authenticate(token) : Session`; `+ update_profile(customer_id, full_name, phone) : Customer`; `+ add_address(customer_id, address) : Address`; `+ save_size(customer_id, category_id, size_label) : None`; `+ link_payment_method(customer_id, provider, method_type, card_number) : PaymentMethod`; `+ suspend_account(staff, account_id) : None`; `+ reactivate_account(staff, account_id) : None`; `+ reset_password(staff, account_id) : str`; `+ search_customers(staff, text) : list[Customer]`
- **Session** «dto» — package *Application layer (use-case services and intelligence)*
  - `- token : str`; `- account_id : int`; `- account_type : str`; `- role : StaffRole | None`; `- expires_at : datetime`; `+ require_role(roles: set[StaffRole]) : None`
- **InventoryService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ view_stock(location_id, style_id) : list[StockLevel]`; `+ low_stock() : list[StockLevel]`; `+ adjust_stock(staff, sku, location_id, delta, note) : StockLevel`; `+ create_restock_request(staff, supplier_id, location_id, lines) : RestockRequest`; `+ confirm_restock(request_no, expected_date) : RestockRequest`; `+ receive_restock(staff, request_no) : RestockRequest`
- **PromotionService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ create_promotion(staff, promotion) : Promotion`; `+ set_eligible_styles(staff, promotion_id, style_codes) : Promotion`; `+ create_voucher(staff, promotion_id, code, usage_limit) : Voucher`; `+ activate(staff, promotion_id) : Promotion`
- **ReportService** «service» — package *Application layer (use-case services and intelligence)*
  - `+ sales_report(staff, date_from, date_to) : list[dict]`; `+ inventory_report(staff, location_id) : list[dict]`; `+ return_report(staff, date_from, date_to) : list[dict]`
- **AccountRepository** «repository» — package *Data access layer*
  - `+ email_exists(email) : bool`; `+ add_customer(customer) : Customer`; `+ get_account_by_email(email) : UserAccount | None`; `+ update_status(account_id, status) : None`
- **InventoryRepository** «repository» — package *Data access layer*
  - `+ get_level(variant_id, location_id, for_update) : StockLevel | None`; `+ save_level(level) : None`; `+ add_movement(movement) : None`; `+ add_restock(request) : RestockRequest`; `+ get_restock(request_no) : RestockRequest | None`; `+ save_restock(request) : None`
- **PromotionRepository** «repository» — package *Data access layer*
  - `+ add(promotion, created_by) : Promotion`; `+ save(promotion) : None`; `+ add_voucher(voucher) : Voucher`
- **ReportRepository** «repository» — package *Data access layer*
  - `+ sales_by_variant(date_from, date_to) : list[dict]`; `+ stock_by_variant(location_id) : list[dict]`; `+ returns_by_reason(date_from, date_to) : list[dict]`
- **SupplierGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ send_restock_request(supplier_email, request_no, lines) : None`
- **PaymentGateway** *(interface)* — package *Integration layer (external systems and AI models)*
  - `+ tokenize_method(provider, method_type, card_number) : tuple[str, str]`
- **StockLevel** «entity» — package *Domain layer (problem domain)*
  - `+ receive(quantity) : None`; `+ adjust(delta) : None`
- **RestockRequest** «entity» — package *Domain layer (problem domain)*
  - `+ confirm(expected_date) : None`; `+ reject(reason) : None`; `+ mark_received() : None`

**Các lớp trong từng package (chỉ hiển thị tên lớp):**

- *Domain layer (problem domain)*: `Customer`, `Promotion`

| Từ | Bội số | Quan hệ (VP) | Bội số | Đến | Tên / vai trò |
|---|---|---|---|---|---|
| AccountController |  | Association (có hướng) |  | AccountService | accounts |
| BackOfficeController |  | Association (có hướng) |  | InventoryService | inventory |
| BackOfficeController |  | Association (có hướng) |  | PromotionService | promotions |
| BackOfficeController |  | Association (có hướng) |  | ReportService | reports |
| BackOfficeController |  | Association (có hướng) |  | AccountService | accounts |
| AccountService |  | Association (có hướng) |  | AccountRepository | accounts |
| AccountService |  | Association (có hướng) |  | PaymentGateway | payments |
| InventoryService |  | Association (có hướng) |  | InventoryRepository | inventory |
| InventoryService |  | Association (có hướng) |  | SupplierGateway | suppliers |
| PromotionService |  | Association (có hướng) |  | PromotionRepository | promotions |
| ReportService |  | Association (có hướng) |  | ReportRepository | reports |
| AccountService |  | Dependency |  | Customer |  |
| InventoryService |  | Dependency |  | RestockRequest |  |
| InventoryService |  | Dependency |  | StockLevel |  |
| PromotionService |  | Dependency |  | Promotion |  |

