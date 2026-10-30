# PROGRESS — ABC Fashion E-Commerce IS

Theo dõi tiến độ triển khai theo `HUONG_DAN_CODE.md`. Cập nhật lần cuối: 2026-10-29.

## Tóm tắt

| Hạng mục | Trạng thái |
|---|---|
| CSDL: schema 39 bảng, seed, migrate cho CSDL cũ, script cài đặt | ✅ Xong |
| Model: 11 module, 41 entity, 34 enum, quy tắc thuần | ✅ Xong |
| Control: 34 DAO (gồm `DAO` gốc), 5 gateway sandbox | ✅ Xong |
| View: 53 màn hình Frm + `main.py` | ✅ Xong |
| `check_gen.py`: 104 module, 0 vi phạm layer, số lớp / operation khớp mô hình (53/34/5/41/34/329) | ✅ Đạt |
| Kiểm thử tự động: **99 đạt + 2 bỏ qua** (2 test đối chiếu VP bỏ qua khi máy này chưa có `vp_export/`) (33 thuần + 16 DAO + 2 giao diện end-to-end + 2 đối chiếu mô hình VP + 12 gateway ↔ dịch vụ ngoài + 10 luồng giao diện qua dịch vụ ngoài / lỗi giữa chừng + 19 dịch vụ AI thật / màn hình tìm kiếm / chỉ mục + 7 ghi âm micro) | ✅ Đạt |
| Dịch vụ bên ngoài tách biệt (`external_services/`): ngân hàng, vận chuyển, e-mail/SMS mô phỏng + **AI thật**, chạy nền | ✅ Xong — xem mục "Dịch vụ bên ngoài" |
| `vp2py.py`: sinh bộ khung từ `vp_export/project.xml` (104 module, 329 operation) + `--check` đối chiếu mã ↔ mô hình | ✅ Xong — **0 lệch, 0 sai khác** (4 thuộc tính đã thêm vào `project.xml`; xem mục dưới về việc đưa vào VP) |
| Xem giao diện thật (chụp 36 màn hình trên CSDL thật) | ✅ Xong — đã sửa 7 lỗi hiển thị |
| Chạy trên CSDL `abc_fashion_v2` thật của máy này | ✅ Đã migrate; 9 tài khoản đăng nhập đúng trang chủ |

## Chuyển sang MVC + web khách hàng (2026-10-30)

- **Tầng controller mới** `abc_fashion/controller/` gồm 15 lớp: Auth, Profile, AccountAdmin, Catalogue, Cart, Checkout, Order, Review, Return, OrderAdmin, Product, Promotion, Report, Inventory, Sync. Có 130 operation mới.
- **53 Frm**: không import DAO / gateway nữa, chỉ gọi controller. Tên lớp, thuộc tính widget / dữ liệu và handler `on_*` giữ nguyên.
- **Logic chuyển từ view sang controller**:
  - kiểm tra dữ liệu;
  - transaction nhiều DAO;
  - luồng thanh toán / hoàn tiền / huỷ đơn (`controller/_flows.py`);
  - đồng bộ vận chuyển nền (SyncController).
- **Lỗi nghiệp vụ**: controller ném `BusinessError`; `_util.guarded` hiển thị lỗi này.
- **`check_gen.py`** kiểm tra quy tắc MVC và đếm: 119 module, 53 / 15 / 34 / 5 / 41 / 34, 459 operation.
- **`vp2py.py`** hiểu package `controller`: sinh bộ khung và `--check` association Frm → controller → DAO.
- **Web khách hàng** `code/abc_fashion_web/` (Flask): chạy bằng `python -m abc_fashion_web`, mặc định ở cổng 8000. Ứng dụng web dùng chung controller với desktop; mỗi request có một kết nối CSDL riêng.
- **VP**: phần cần vẽ lại liệt kê trong `HUONG_DAN_VE_LAI_VP_MVC.md`. Chưa vẽ lại thì `vp2py --check` trên `project.xml` cũ sẽ báo lệch, đó là chủ ý.
- **Kiểm thử**: 85 đạt, 2 bỏ qua (hai test đối chiếu VP vì máy này không có `vp_export`). Chạy trên CSDL thử, gồm cả `test_web.py` mới. Bộ test AI thật bị bỏ qua vì dịch vụ AI / Ollama chưa chạy.
- **Sao lưu**: mã trước khi sửa nằm ở `backups/code_before_mvc_20261030_1838/`.

Kiểm thử CSDL / giao diện chạy trên CSDL thử `abc_fashion_test` của server PostgreSQL 18 trên máy (fixture xoá và tạo lại CSDL này mỗi lần chạy).

## CSDL thật `abc_fashion_v2` (2026-10-29)

Trước khi sửa, CSDL đã được sao lưu vào `backups/abc_fashion_v2_before_migrate_20261029.dump`. Khôi phục bằng: `pg_restore -c -d abc_fashion_v2 <file>`.

1. Đã chạy `db/migrate_v2.sql`: xoá `Review.verified_purchase/origin`, thêm `Order.ship_*`, cho `Payment.paymentMethodId` NULL, thêm `ReturnItem.replacementVariantId`.
2. **Mật khẩu**: dữ liệu báo cáo lưu hash bcrypt giả (8/9 sai định dạng) nên không ai đăng nhập được. Theo yêu cầu, đã đặt lại cả 9 tài khoản thành `abc12345` (PBKDF2). Mã cũng đã hỗ trợ hash bcrypt thật (gói `bcrypt`).
3. **Sổ kho**: dữ liệu báo cáo thiếu tồn đầu kỳ. Đã thêm 8 dòng `StockMovement` (`adjustment`, `OPENING`) bằng phần chênh lệch; tồn kho không đổi, Σ sổ kho = `on_hand`.
4. Tài khoản: khách `alex@email.com`, `linh.tran@email.com`, `minh.pham@email.com`; nhân viên `admin@`, `manager@`, `warehouse@`, `cs@abcfashion.vn`; nhà cung cấp `sales@vietthread.vn`, `orders@saigondenim.vn`. Dữ liệu báo cáo không có merchandiser / marketing, nên đã **thêm** `merch@abcfashion.vn` (ST05, merchandiser) và `marketing@abcfashion.vn` (ST06, marketing), mật khẩu `abc12345` (PBKDF2). Chưa có tài khoản vai trò `sales`.
5. **Ảnh sản phẩm**: URL gốc `https://cdn.abcfashion.vn/...` không tải được. Đã tải 4 ảnh miễn phí bản quyền (Unsplash License) về `code/media/products/` và đổi `ProductMedia.url` của dòng ảnh đầu mỗi style sang đường dẫn cục bộ (`db/fetch_product_photos.py`; nguồn từng ảnh trong `code/MEDIA_CREDITS.md`). Dòng video `floral-360.mp4` giữ nguyên (không có nguồn video miễn phí hợp lệ); `StyleDetailFrm` chỉ lướt qua ảnh nên bỏ qua dòng này. Chỉ mục tìm kiếm ảnh đã sinh lại từ ảnh thật; thử tìm bằng chính 4 ảnh đều trả đúng sản phẩm đứng đầu.
   - Lưu ý: áo thun đen (`TS-BAS-04`) có chữ in nhỏ trên ngực, váy (`DR-MID-03`) là ảnh người mẫu; ảnh Unsplash/Pexels không tải tự động được qua trang chính nên tôi lấy ảnh qua trang ảnh cụ thể và CDN công khai.
6. Khác biệt schema đã xử lý trong mã: CSDL báo cáo không có UNIQUE trên `ShipmentEvent` (DAO không dùng `ON CONFLICT` nữa) và có thêm UNIQUE (`styleId`, `material`) (DAO từ chối vật liệu trùng tên).

## Đối chiếu với mô hình Visual Paradigm (2026-10-29)

Nguồn: `vp_export/project.xml` (bản xuất mới nhất; các file `*.xml` khác trong thư mục là bản trung gian, không dùng).
Mô hình: 167 lớp (53 Frm, 34 DAO, 5 gateway, 41 entity, 34 enum), 329 operation, 41 kế thừa, 348 association.

```
python vp2py.py ../vp_export/project.xml --check .        # so mô hình với mã
python vp2py.py ../vp_export/project.xml <thư_mục_tạm>    # sinh bộ khung để so (mục 12.3)
```

`--check` so: lớp và module, kế thừa, tên + thứ tự tham số của mọi operation, hàm công khai thừa, trường + kiểu của entity, literal enum, mọi thuộc tính Frm (widget / dữ liệu) có được gán, và mỗi DAO / gateway mà Frm "Uses" theo association có được tạo trong `__init__`.

Kết quả lần đầu: 5 lệch → đã sửa trong mã:
- `CheckoutFrm.on_change_payment_method` là hàm công khai không có trong mô hình → đổi thành `_on_change_payment_method` (mục 5.6).
- Thiếu đối tượng DAO theo association: `ManageOrderFrm.stock_movement_dao`, `InspectReturnFrm.stock_movement_dao`, `ManageRestockFrm.stock_level_dao`, `ManageRestockFrm.stock_movement_dao` → đã thêm.
- `check_gen.py` đếm thêm `DAO.__init__` như mô hình (329 operation = hàm công khai + constructor của Frm và DAO).

4 sai khác từng được duyệt (`Order.ship_recipient / ship_phone / ship_address`, `ReturnItem.replacementVariantId`) **đã được thêm vào `vp_export/project.xml`** bằng `db/vp_add_attributes.py` (chèn thẳng vào văn bản XML, các byte khác giữ nguyên; bản gốc lưu ở `vp_export/project.before_attrs.xml`). `KNOWN_DEVIATIONS` trong `vp2py.py` nay rỗng; `--check` báo `lệch mô hình: 0 · sai khác đã duyệt: 0`.

**Lưu ý — file `.vpp` của bạn chưa có 4 thuộc tính này.** Mới chỉ file XML được sửa. Cách đưa vào VP:
- nhanh nhất: thêm tay 4 thuộc tính theo mục A1 của `HUONG_DAN_SUA_VP_VA_BAO_CAO.md` (2 phút), hoặc
- nhập `vp_export/project_import.xml` (cùng nội dung, có khai báo namespace như các file nhập trước đây) vào VP.
Sau đó xuất lại XML đè lên `project.xml`; `--check` vẫn phải báo 0 lệch. Nếu bạn xuất từ VP mà chưa thêm thuộc tính, `--check` sẽ báo 4 lệch — đó là chủ ý.

## Dịch vụ bên ngoài (2026-10-29)

Thư mục `external_services/` (ngang hàng `code/`, không import mã của nhau, chỉ HTTP) — hướng dẫn đầy đủ ở `external_services/README.md`.

| Dịch vụ | Cổng | Loại | Ghi chú |
|---|---|---|---|
| payment (ngân hàng) | 8101 | mô phỏng | đủ số dư + đủ điều kiện thì qua; tài khoản mẫu 4242 / 0002 (khoá) / 9995 (ít tiền); hoàn tiền không vượt phần đã thu |
| shipping (GHN / GHTK) | 8102 | mô phỏng | tự tiến một trạng thái mỗi 3–5 giây tới đã giao; quận có `FAIL` thì giao thất bại |
| notify (e-mail / SMS) | 8103 | mô phỏng | hộp thư xem tại `/inbox`; `@bounce.test` bị từ chối |
| ai | 8104 | **thật** | CLIP ViT-B/32 + Whisper large-v3-turbo (GPU RTX 5070 Ti) + `qwen2.5:3b` (Ollama) |

Cách dùng: `cd external_services && python manage.py start`, đặt `ABC_FASHION_GATEWAY_MODE=http` rồi chạy ứng dụng. Mặc định vẫn là `sandbox` (các test cũ không phụ thuộc dịch vụ).

**Thay đổi trong ứng dụng** (đều trong thân hàm hoặc hàm riêng, `vp2py --check` vẫn 0 lệch):
- `control/gateway/_http.py` (hàm dùng chung, không phải gateway; `check_gen.py` bỏ qua module `_*` khi đếm) + 5 gateway có nhánh `http`;
- `view/_sync.py`: đồng bộ vận chuyển nền (`ShipmentSync`) và đẩy chỉ mục tìm kiếm lên AI; `main.py` khởi động chúng khi ở chế độ http;
- `view/_util.py`: `run_in_thread` (luồng phụ qua hàng đợi), `watch` (màn hình tự nạp lại khi dữ liệu nền đổi), `notify` gắn `recipient`, `fill_table` giữ dòng đang chọn;
- `TrackShipmentFrm`, `OrderDetailFrm`, `ManageOrderFrm` tự cập nhật khi kiện đổi trạng thái; `SearchStyleFrm` và `AssistantFrm` gọi AI ở luồng phụ;
- DAO có thêm hàm riêng tư `_get_open_shipments`, `_get_brief`, `_status_signature`, `_get_recipient`, `_get_catalogue_for_index`.

**Kết quả đo với AI thật:**
- tìm bằng ảnh: 4/4 ảnh gốc ra đúng sản phẩm đầu; 5/5 ảnh *khác* của cùng loại (váy hoa dài / ngắn, áo thun khác, jeans màu sáng…) cũng ra đúng; 20–60 ms/lần;
- tìm bằng giọng nói (6 file âm thanh mẫu): 5/5 yêu cầu liên quan ra đúng sản phẩm đầu, câu không liên quan ("đi ăn phở") trả rỗng; Whisper hay nghe sai từ mượn ("jeans" → "dinh") nhưng LLM + CLIP vẫn tìm đúng; ~0,4 s/lần sau khi nóng máy (lần đầu 39 s do nạp mô hình);
- trợ lý: trả lời đúng giá khuyến mãi, chất liệu, chính sách; che số điện thoại; kiểm duyệt phân biệt được lời chê lịch sự với thô tục / quảng cáo / không liên quan. Đã lọc chữ Hán lạ mà `qwen2.5:3b` thỉnh thoảng chèn.

**Lưu ý khi chạy thật:** ở chế độ http, ứng dụng khi khởi động vẫn huỷ đơn `pending_payment` quá 30 phút (mục 9.5) — trên CSDL báo cáo có đơn `ORD-261020` ở trạng thái này nên nó sẽ bị huỷ ở lần chạy đầu (hành vi này có cả ở chế độ sandbox). Vận đơn của dữ liệu báo cáo (`GHTK200001`…) không do hãng mô phỏng tạo nên bị bỏ qua (404), không đổi trạng thái.

## Giao diện mới "Midnight Atelier" (2026-10-29)

Thiết kế ở `uiux-design.md` (vector art, tông xanh dương – đen, font Be Vietnam Pro). Đã áp dụng cho cả 53 màn hình:
- `view/_art.py` vẽ bằng Pillow theo DPI thật: logo móc áo, header dải lụa, tranh đăng nhập (giá treo 3 chiếc áo, mặt trăng, túi), 20 biểu tượng nét, nút bo góc 9 lát; `make_ui_assets.py` xuất bản 2× ra `media/ui/`.
- `view/_theme.py`: token màu, nạp font riêng cho tiến trình, style ttk cho mọi widget, header, tự phân loại nút (chính / phụ / nguy hiểm / liên kết) theo chữ.
- `_util.body` có header vector; `home_window` thành lưới ô có biểu tượng; đăng nhập và trang chủ khách dựng lại bố cục; 24 màn hình bỏ font / màu viết cứng để dùng style.
- Không đổi tên widget / hàm / association: `vp2py --check` 0 lệch, `check_gen` 0 vi phạm, 91/91 test đạt (test giờ chạy với theme thật).

## Kiểm thử khi dịch vụ ngoài lỗi (2026-10-29)

`tests/test_http_flows.py` chạy giao diện ở chế độ http và dùng `/__admin/behavior` của dịch vụ mô phỏng để gây lỗi giữa chừng. Kèm theo: kịch bản trình diễn 14.2 chạy hết qua ngân hàng / hãng vận chuyển / e-mail (đối chiếu sổ cái ngân hàng với `Payment`, 3 vận đơn, thư trong hộp thư), ngân hàng chậm 1,5 giây, liên kết thẻ mở tài khoản ngân hàng, màn hình theo dõi kiện tự nạp lại, tìm kiếm ảnh qua màn hình với AI thật và khi AI tắt, `manage.py status`.

Các test này tìm ra 4 lỗi, đã sửa (chỉ đổi thân hàm / hàm riêng, `vp2py --check` vẫn 0 lệch):

| Tình huống | Trước khi sửa | Bây giờ |
|---|---|---|
| Ngân hàng không phản hồi lúc bấm "Đặt hàng" | đơn đã tạo và giữ hàng nhưng màn hình thanh toán vẫn mở → bấm lại tạo **đơn trùng**, giữ hàng hai lần | sang `ConfirmOrderFrm` với đơn `pending_payment` + cảnh báo; thanh toán lại ở đó |
| Ngân hàng không phản hồi lúc huỷ đơn đã thu tiền | đơn đã huỷ nhưng hoàn tiền mất dấu (không có bản ghi), chỉ hiện "Lỗi hệ thống" | ghi lần hoàn `failed`, cảnh báo "chưa hoàn được tiền", vẫn báo khách; nhân viên hoàn lại bằng "Hoàn tiền…" ở `ManageOrderFrm` |
| Hãng không phản hồi lúc tạo kiện lấy hàng trả | kiện đã ghi vào CSDL; bấm lại tạo **kiện thứ hai** | dùng lại kiện chưa có vận đơn |
| Hãng không phản hồi lúc gửi hàng đổi | kho đã trừ, kiện đã tạo; bấm lại **trừ kho lần hai** | chỉ bàn giao lại các kiện chưa có vận đơn, không trừ kho nữa |

Giao hàng (`ManageOrderFrm`) khi hãng lỗi vốn đã đúng: đơn và kiện giữ nguyên, làm lại được. E-mail lỗi không chặn huỷ / hoàn tiền (bản ghi `failed`).

## Kiểm tra giao diện (2026-10-29)

Chụp 36 màn hình (đủ 7 vai trò) từ ứng dụng chạy trên CSDL thật, chế độ chỉ đọc, rồi xem từng ảnh. Chức năng đều chạy, không có lỗi; đã sửa 7 lỗi hiển thị:

| # | Lỗi | Cách sửa |
|---|---|---|
| 1 | Nhiều cột bị cắt chữ (SKU, ngày giờ, "Chờ thanh toán", số thẻ…) | `fill_table` tự giãn cột vừa nội dung (không hẹp hơn độ rộng gợi ý, tối đa 420 px) |
| 2 | Cột số / tiền canh lệch | tự canh phải cột nào toàn số, tiền, % |
| 3 | Đơn cũ hiện `Giao tới: – –`, `None, None, None` (dữ liệu báo cáo chưa có địa chỉ chụp) | `ship_text()` hiện "(đơn cũ — chưa lưu địa chỉ giao hàng)" |
| 4 | Ô văn bản nhiều dòng dùng phông đơn cách (Courier) | `apply_theme()` đặt phông hệ thống |
| 5 | Loại khuyến mãi, dáng áo hiện giá trị tiếng Anh thô | thêm nhãn tiếng Việt cho `PromoType`, `FitType`, `Measure` |
| 6 | Tiêu đề cửa sổ nhỏ bị cắt (`ABC Fashion —...`) | `minsize(420, 120)` cho mọi cửa sổ |
| 7 | Chữ bị mờ trên màn hình scale 125–200% | `enable_dpi_awareness()` trước khi tạo Tk (chỉ Windows) |

Còn lại (không phải lỗi mã): dữ liệu mẫu của báo cáo bằng tiếng Anh (tên sản phẩm, mô tả); ảnh trong cửa sổ có kích thước cố định theo pixel nên trông nhỏ hơn ở màn hình scale cao.

## Lộ trình (mục 14.1)

| Bước | Việc | Trạng thái | Kiểm chứng |
|---|---|---|---|
| 1 | Sửa CSDL theo mục 13 (#1, #4, #5) | ✅ | `db/schema.sql` đã áp; `db/migrate_v2.sql` cho CSDL cũ (chạy lại 2 lần không lỗi) |
| 2 | `dao.py`: kết nối chung + tiện ích | ✅ | mọi test DAO dùng chung một kết nối, transaction lồng = savepoint |
| 3 | Account: đăng nhập mọi vai trò, đăng xuất | ✅ | `test_login_*`, kịch bản end-to-end đăng nhập qua `LoginFrm.on_login` |
| 4 | Catalogue: duyệt, tìm chữ, chi tiết | ✅ | mở được mọi màn hình catalogue với 4 style / 8 biến thể mẫu |
| 5 | Giỏ + đặt hàng: tách 2 kiện, tồn kho đúng | ✅ | `test_order_two_locations_two_shipments`, voucher hết lượt → rollback, 2 tiến trình tranh món cuối → đúng 1 đơn |
| 6 | Đơn của khách, huỷ đơn trả lại kho | ✅ | `test_confirm_then_cancel_restores_stock_and_voucher`, `test_pending_cancel_releases_reservation` |
| 7 | Quản lý đơn tới `completed` | ✅ | end-to-end: processing → giao 1 phần → shipped → delivered → khách xác nhận |
| 8 | Hồ sơ, địa chỉ, liên kết thanh toán | ✅ | mở màn hình; DAO địa chỉ giữ đúng 1 mặc định |
| 9 | Trả hàng: hoàn đúng số, hàng về kho | ✅ | end-to-end: duyệt → kiện lấy → kho kiểm đạt → hoàn đúng `đơn giá − giảm phân bổ` |
| 10 | Đánh giá + kiểm duyệt | ✅ | `test_moderation`, end-to-end gửi đánh giá |
| 11 | Kho & nhập hàng: sổ kho khớp tồn | ✅ | `test_receive_restock_updates_stock_and_ledger`, đối soát Σ sổ kho = `on_hand` sau mọi kịch bản |
| 12 | Sản phẩm, khuyến mãi | ✅ | mở màn hình; style chỉ `active` khi vật liệu 100% + có biến thể |
| 13 | Báo cáo, quản trị tài khoản, nhật ký | ✅ | `test_reports_have_data`; xuất CSV UTF-8 BOM |
| 14 | AI: SearchEngine, AssistantEngine, AssistantFrm | ✅ | sandbox mặc định; `ABC_FASHION_GATEWAY_MODE=http` dùng dịch vụ AI thật (CLIP, Whisper, LLM) — `tests/test_ai_service.py` |

## Danh sách kiểm tra trước khi nộp (mục 14.3)

- [x] Không còn `raise NotImplementedError`.
- [x] `check_gen.py` 0 vi phạm (còn kiểm thêm: không có câu SQL trong view).
- [x] Không có câu SQL ghép chuỗi từ dữ liệu người dùng (chỉ ghép tên bảng / cột hằng trong mã).
- [x] Không lưu số thẻ đầy đủ (`add_payment_method` từ chối số có > 4 chữ số), mật khẩu băm PBKDF2; bản rõ của seed được băm lại ở lần đăng nhập đầu.
- [x] Mọi thay đổi tồn kho có dòng `StockMovement` (đã kiểm bằng đối soát trong test).
- [x] Khách không mở được đơn của người khác (`OrderDetailFrm` kiểm `customerId`; DAO luôn lọc theo khách).
- [x] Lỗi CSDL hiện hộp "Lỗi hệ thống", ứng dụng không tắt (`@guarded` trên mọi handler; `main.py` báo lỗi kết nối).
- [x] Chữ ký hàm khớp mô hình: `vp2py.py --check` báo 0 lệch (4 sai khác đã duyệt, cần cập nhật VP); bộ khung sinh lại qua `check_gen.py` sạch.

## Xử lý các điểm ở mục 13

| # | Xử lý |
|---|---|
| 1 | `Review` không có `verified_purchase`/`origin`; migrate xoá cột cũ |
| 2 | Đã thêm kiểu trả về cho mọi hàm DAO / gateway / handler |
| 3 | Kết nối chung `DAO._shared`, tự mở lại khi mất kết nối |
| 4 | Thêm `Order.ship_recipient / ship_phone / ship_address` (chụp địa chỉ lúc đặt) |
| 5 | `Payment.paymentMethodId` cho phép NULL (COD, chuyển khoản, ví chưa liên kết) |
| 6 | `LoginFrm` dùng thêm CustomerDAO, StaffMemberDAO, SupplierDAO |
| 7 | Vai trò `SALES` tạm dùng `MarketingHomeFrm` (chỉ xem báo cáo) |
| 8 | Điều hướng lập trình theo handler mục 8.2 |
| 9 | Đã thêm các DAO còn thiếu vào Frm (liệt kê ở "Sai khác so với mô hình") |
| 10 | `DateEntry` từ tkcalendar (bọc trong `view/_util.py`, có bản thay thế nếu thiếu thư viện) |
| 11 | `main.py` dùng cửa sổ gốc ẩn |
| 12 | Yêu cầu huỷ = `cancel_reason IS NOT NULL` và trạng thái chưa `cancelled`; `SearchOrderFrm` tô vàng |
| 13 | Mã `ORD-/RET-/RST-YYMMDD-NNN` sinh trong DAO (`_next_no`) |
| 14 | `preferred_colours` nối / tách dấu phẩy trong `CustomerDAO` |
| 15 | `_check_password` nhận cả bản rõ, đăng nhập thành công thì băm lại |
| 16 | (sửa câu trong báo cáo — ngoài phạm vi mã) |

## Sai khác so với mô hình VP (cần cập nhật mô hình / báo cáo cho khớp)

- **Cột mới**: `Order.ship_*` (#4); `ReturnItem.replacementVariantId` — biến thể thay thế khi đổi hàng (mô hình chưa có chỗ lưu).
- **UNIQUE bổ sung**: `SavedSize(customerId, categoryId)`, `CartItem(cartId, productVariantId)`, `RestockItem(restockRequestId, productVariantId)`, `ReturnItem(returnRequestId, orderItemId)`, `SizeChartEntry(styleId, size_label, measure)`, `ShipmentEvent(shipmentId, status, occurred_at)`; index không phân biệt hoa thường cho e-mail và mã voucher.
- **DAO thêm vào Frm**: StyleDetailFrm (MaterialComponentDAO, SizeChartEntryDAO, ProductMediaDAO); OrderDetailFrm (ReturnRequestDAO, ReviewDAO); ConfirmOrderFrm (OrderDAO, PaymentMethodDAO, NotificationDAO/Gateway); CheckoutFrm (PromotionDAO — giá khuyến mãi tự động); ManageRestockFrm (SupplierDAO); AuditLogFrm (StaffMemberDAO); EditAccountFrm, ManageStyleFrm, AdjustStockFrm, ManageOrderFrm (AuditLogEntryDAO); ProcessReturnFrm, InspectReturnFrm (StockLevelDAO, ShipmentDAO); CancelRequestFrm (PaymentDAO, PaymentGateway, Notification* — hoàn tiền khi huỷ); ProfileFrm, ManageStyleFrm, SelectStyleFrm, SalesReportFrm (CategoryDAO); ReturnRequestFrm (ProductVariantDAO — chọn biến thể đổi).
- **Widget thêm**: `ConfirmOrderFrm.cbo_method` (chọn phương thức khi thanh toán lại); `EditAddressFrm.txt_city`; bảng dòng trả + `cbo_replacement` ở `ReturnRequestFrm`; nút xoá dòng vật liệu / bảng cỡ / media ở `EditStyleFrm`.
- **Hàm riêng tư thêm vào DAO**: `OrderDAO._request_cancel` (khách gửi yêu cầu huỷ đơn `processing`), `OrderDAO._cancel_expired_pending` (huỷ đơn chờ thanh toán quá 30 phút khi khởi động), `StyleDAO._is_complete`, `ShipmentDAO._attach_records`.
- **Quy ước khuyến mãi**: chương trình *không có voucher* = tự động giảm giá trên trang sản phẩm và lúc đặt (`unit_price` đã giảm); chương trình *có voucher* chỉ giảm khi nhập mã. Có thể áp nhiều mã khác nhau cho một đơn.
- **Quyền**: chỉ vai trò WAREHOUSE được điều chỉnh tồn trong `StockLevelFrm` (marketing mở màn hình này để xem hàng sắp hết).
- `view/_util.py` là module tiện ích riêng của view (không có trong mô hình; `check_gen.py` không tính vào 104 module).

## Gateway sandbox (mục 7.4)

| Gateway | Hành vi sandbox | Bản thật |
|---|---|---|
| PaymentGateway | thẻ có số che kết thúc `0002` luôn bị từ chối; còn lại thành công | dịch vụ ngân hàng mô phỏng (`external_services/`, chế độ http) |
| ShippingGateway | `GHN-SANDBOX`, mã `GHN########`; mỗi lần "Cập nhật" kiện tiến một bước tới `delivered` | dịch vụ vận chuyển mô phỏng, tự tiến 3–5 giây/bước (chế độ http) |
| NotificationGateway | ghi vào `code/outbox.log` | dịch vụ e-mail / SMS mô phỏng (chế độ http) |
| SearchEngine | ảnh: so màu trung bình với `media/search_index.json`; giọng nói: chấp nhận file bản ghi `.txt` | **AI thật**: CLIP + Whisper + LLM (chế độ http) |
| AssistantEngine | chế độ cơ bản trả lời từ dữ liệu thật; đặt `ABC_FASHION_LLM_URL` để dùng LLM (POST `{system,prompt}` → `{text}`) kèm lọc câu sai giá / tồn / sức khoẻ / chất liệu / độ phổ biến | **AI thật**: Ollama `qwen2.5:3b` qua dịch vụ AI (chế độ http) |

## Việc tiếp theo

1. ~~Thêm tài khoản merchandiser / marketing~~ — xong (ST05, ST06).
2. ~~Tải ảnh sản phẩm về máy~~ — xong cho 4 style; muốn đổi ảnh thì sửa `PHOTOS` trong `db/fetch_product_photos.py` rồi chạy lại. Cân nhắc quay video thật cho `floral-360.mp4` hoặc xoá dòng video.
3. ~~Xem giao diện thật~~ — xong (xem mục "Kiểm tra giao diện").
4. ~~Thêm 4 thuộc tính vào mô hình~~ — xong ở `project.xml`; còn việc đưa vào file `.vpp` (xem trên).
3b. Cần người dùng thử: kịch bản trình diễn mục 14.2 bằng chuột (đã chạy tự động và đã xem ảnh chụp từng màn hình, nhưng chưa ai thao tác tay).
5. ~~Nối mô hình AI (CLIP, Whisper, LLM)~~ — xong, chạy thật. Còn lại: REST API thật của cổng thanh toán / vận chuyển / e-mail (hiện là mô phỏng, theo yêu cầu).
6. ~~Ghi âm trực tiếp (`sounddevice`) cho tìm kiếm giọng nói~~ — xong (xem "Hoàn thiện ghi âm và các phần còn dang dở").
7. ~~Chỉ mục tìm kiếm AI chỉ đẩy khi khởi động~~ — xong: lưu sản phẩm / biến thể / ảnh, ngừng bán đều cập nhật chỉ mục.

## Đổi tên lớp bỏ tiền tố `tbl` (2026-10-29)

39 lớp entity (`tblOrder` → `Order`, `tblUser` → `User`, …) đổi tên trong mã (`model/`, DAO, gateway, view, test), `vp_export/project.xml` (+ `project_import.xml`, `project.before_attrs.xml`), `HUONG_DAN_CODE.md`, `HUONG_DAN_SUA_VP_VA_BAO_CAO.md`, `KE_HOACH_MOCK_SERVERS.md`, `CLAUDE.md`. **Tên bảng trong CSDL giữ nguyên** (`"tblOrder"` trong SQL, schema.sql, seed.sql, CSDL thật). Các file XML trung gian khác trong `vp_export/` (full_import.xml, t2.xml…) không đổi. Kết quả: `check_gen` 0 vi phạm, `vp2py --check` 0 lệch, 91/91 test đạt.

## Hoàn thiện ghi âm và các phần còn dang dở (2026-10-29)

- **Tìm bằng giọng nói qua micro** (đúng mục `SearchStyleFrm.on_search_by_voice` của `HUONG_DAN_CODE.md`): nút "Nói để tìm" ghi âm 5 giây bằng `sounddevice` (`view/_util.record_wav`, luồng phụ), đếm ngược "Đang nghe…", rồi gửi tìm như file. Không có micro / thiếu thư viện / ghi toàn khoảng lặng thì báo lý do và mở hộp chọn file; nút "File âm thanh…" vẫn dùng được trực tiếp. Biểu tượng nút "Tìm bằng ảnh" đổi từ máy ảnh sang ảnh (không có camera trong tài liệu). Micro của máy này (NVIDIA Broadcast) mở được; ghi thử khi im lặng cho đỉnh biên độ 1 → báo "không nghe thấy tiếng nói".
- **Chỉ mục AI tự cập nhật** (`_sync.refresh_search_index`): sau khi lưu sản phẩm (`EditStyleFrm`), thêm / xoá ảnh, lưu biến thể (`EditVariantFrm`) hoặc ngừng bán (`ManageStyleFrm`), chỉ mục lên dịch vụ AI được đẩy lại (chỉ ở chế độ http; không đổi thì dịch vụ bỏ qua).
- **Huỷ đơn quá hạn định kỳ** (mục 9.5): trước chỉ chạy lúc khởi động; nay cứ 5 phút một lần (`main._release_expired_orders`) để ứng dụng mở lâu vẫn nhả hàng.
- **Video sản phẩm / bằng chứng**: `StyleDetailFrm` có nút "Xem video" (chỉ hiện khi style có video là file trong `media/`, mở bằng trình phát của hệ điều hành); `ProcessReturnFrm` nhấp đúp vào bằng chứng dạng video để mở. Video trên CDN cũ trong CSDL báo cáo (`floral-360.mp4`) không tải được nên nút không hiện.
- Máy này không còn thư mục `vp_export/` (mô hình VP đã vẽ lại ở máy khác): `vp2py --check` đã chạy trên bản sao tạm của mô hình cũ đã đổi tên lớp → 0 lệch; 2 test đối chiếu VP bỏ qua cho tới khi chép `vp_export/project.xml` mới về. Khi đó chạy `python vp2py.py ../vp_export/project.xml --check .` — nếu VP vẽ lại có tên khác (kiểu, widget, hàm) thì sửa mã hoặc ghi vào `KNOWN_DEVIATIONS`.
