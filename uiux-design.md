# ABC Fashion — Thiết kế giao diện (UI/UX)

> Tài liệu gốc cho mọi thay đổi giao diện của ứng dụng desktop (tkinter/ttk). Mã phải bám đúng các token và thành phần dưới đây; muốn đổi màu, cỡ chữ hay khoảng cách thì sửa ở đây và trong `view/_theme.py`, không viết màu / font cứng trong từng `XxxFrm`.

## 1. Ý tưởng: "Midnight Atelier"

Một xưởng may về đêm: nền **đen ánh xanh** như vải nhung tối, các lớp **xanh dương** đậm nhạt chồng lên nhau như những dải lụa, điểm xuyết đường chỉ may và chấm sáng. Phong cách **vector art phẳng**: hình khối hình học, đường cong mượt, không bóng đổ hiện thực, không ảnh chụp trong phần khung giao diện (ảnh sản phẩm vẫn là ảnh thật).

Nguyên tắc:
1. **Dễ đọc trước, đẹp sau.** Chữ chính trên nền đạt tương phản ≥ 7:1, chữ phụ ≥ 4.5:1. Không dùng chữ xanh đậm trên nền đen.
2. **Một màu nhấn.** Xanh `blue-500` chỉ dành cho hành động chính, vùng chọn và tiêu đề. Màu đỏ / xanh lá / vàng chỉ để báo trạng thái.
3. **Lớp nền theo độ sâu.** Càng "nổi" lên thì càng sáng hơn một bậc (`ink-950` → `ink-900` → `ink-850` → `ink-800`).
4. **Không phá mô hình VP.** Chỉ đổi cách trình bày; tên lớp, tên widget (`txt_`, `btn_`, `tbl_`…), tên hàm `on_…` và association giữ nguyên (xem mục 9).

## 2. Bảng màu (token)

### 2.1 Nền và viền — dải "ink" (đen ánh xanh)
| Token | Mã | Dùng cho |
|---|---|---|
| `ink-950` | `#060A13` | đầu trang (header), nền tranh vector, thanh cuộn |
| `ink-900` | `#0A1120` | nền cửa sổ |
| `ink-850` | `#0E182B` | bề mặt: bảng, thẻ (card), khung ảnh |
| `ink-800` | `#132038` | ô nhập, tiêu đề bảng, nút phụ |
| `ink-700` | `#1B2C4B` | nút phụ khi rê chuột, dòng chẵn được đánh dấu |
| `ink-600` | `#27406A` | viền, đường kẻ |

### 2.2 Xanh dương — dải "blue" (màu nhấn)
| Token | Mã | Dùng cho |
|---|---|---|
| `blue-700` | `#173E9E` | nút chính khi bấm |
| `blue-600` | `#1F4FD1` | dòng đang chọn trong bảng |
| `blue-500` | `#2F6BFF` | **nút chính**, viền ô đang nhập |
| `blue-400` | `#5B8CFF` | nút chính khi rê chuột, dấu tích / radio |
| `sky-300` | `#8CC1FF` | tiêu đề, nhãn tiêu đề bảng, biểu tượng |
| `sky-200` | `#BCD9FF` | chữ nổi trên nền xanh đậm |
| `cyan-400` | `#36C2F0` | điểm nhấn trong tranh vector (chấm sáng, đường chỉ) |

### 2.3 Chữ
| Token | Mã | Tương phản trên `ink-900` | Dùng cho |
|---|---|---|---|
| `text-100` | `#E6EEFC` | ~15:1 | chữ chính |
| `text-300` | `#A3B4D1` | ~8:1 | nhãn ô nhập, chữ phụ |
| `text-500` | `#6E81A3` | ~4.6:1 | gợi ý, chữ bị vô hiệu hoá |

### 2.4 Trạng thái (chỉ dùng để báo hiệu)
| Token | Mã | Dùng cho |
|---|---|---|
| `success` | `#3DDC97` | lưu thành công, còn hàng, tổng đạt 100% |
| `warning` | `#F7C25C` | dòng cần chú ý (nền `#2E2610`) |
| `danger` | `#FF7A8A` | lỗi, hết hàng, nút nguy hiểm (nền `#3A1622`) |
| `promo` | `#FF9DB5` | giá khuyến mãi |
| `violet` | `#B9A6FF` | trạng thái trả / đổi hàng |

## 3. Chữ (typography)

Font: **Be Vietnam Pro** (Google Fonts, giấy phép SIL OFL — `code/media/ui/fonts/OFL.txt`), thiết kế riêng cho tiếng Việt nên dấu không bị dính / cắt. Ứng dụng nạp font *riêng cho tiến trình* (không cài vào Windows). Thiếu file font thì dùng **Segoe UI** / **Segoe UI Semibold**.

| Vai trò | Font | Cỡ (pt) | Dùng cho |
|---|---|---|---|
| `display` | Be Vietnam Pro SemiBold | 22 | lời chào trên trang chủ, tên thương hiệu ở màn hình đăng nhập |
| `h1` | Be Vietnam Pro SemiBold | 16 | tiêu đề trong header của cửa sổ |
| `h2` | Be Vietnam Pro SemiBold | 13 | số đơn, tên sản phẩm, số phiếu |
| `h3` | Be Vietnam Pro SemiBold | 11 | tổng tiền, trạng thái, tiêu đề nhóm |
| `body` | Be Vietnam Pro | 10 | mọi chữ thường, ô nhập, bảng |
| `button` | Be Vietnam Pro Medium | 10 | chữ trên nút |
| `small` | Be Vietnam Pro | 9 | gợi ý, tiêu đề phụ trong header |

Chiều cao dòng bảng = 1,9 × chiều cao chữ. Tiêu đề bảng dùng `Medium`, màu `sky-300`.

## 4. Khoảng cách, bo góc, kích thước

- Thang khoảng cách: **4 · 8 · 12 · 16 · 24 · 32** px (nhân hệ số DPI).
- Lề nội dung cửa sổ: 16 px (trang chủ 24 px). Giữa các nhóm: 12 px. Giữa nhãn và ô nhập: 8 px.
- Bo góc: nút và ô trang chủ 8 px (ảnh 9 lát). Ô nhập, bảng, thẻ dùng viền 1 px góc vuông của theme `clam` — bo góc ô nhập bằng ảnh làm hỏng mũi tên của Combobox / Spinbox nên không làm.
- Nút: cao tối thiểu 32 px, đệm ngang 14 px. Ô trang chủ (tile): cao 56 px.
- Header cửa sổ: cao 64 px; header trang chủ: 132 px.
- Mọi kích thước ảnh đều vẽ theo DPI thật (`winfo_fpixels('1i') / 96`) nên sắc nét ở 100–200%.

## 5. Phần tử đồ hoạ (vector art)

Vẽ bằng Pillow ở độ phân giải gấp 4 rồi thu nhỏ (khử răng cưa), cùng một bộ hàm trong `view/_art.py`. Bản xuất sẵn (2×) nằm ở `code/media/ui/`, tạo lại bằng `python make_ui_assets.py`.

| Phần tử | File | Mô tả |
|---|---|---|
| Logo | `logo.png` | ô vuông bo góc xanh `blue-500→blue-700`, móc treo áo trắng, chấm `cyan-400` |
| Header cửa sổ | `banner.png` | nền `ink-950`, 3 dải lụa lượn sóng xanh đậm → nhạt chồng lớp ở bên phải, đường chỉ may nét đứt, chấm sáng |
| Header trang chủ | `hero_banner.png` | như trên nhưng cao hơn, thêm vòng tròn "mặt trăng" và hình móc áo lớn mờ |
| Tranh đăng nhập | `login_art.png` | 360×460: mặt trăng, dải lụa, giá treo với 3 chiếc áo vector (áo sơ mi, váy, áo thun), túi mua sắm, chấm sao |
| Biểu tượng | `icons/*.png` | 22 biểu tượng nét 2 px màu `sky-300`, 24 px: catalogue, cart, orders, profile, logout, accounts, product, review, audit, order, report, promotion, return, inspect, stock, restock, search, camera, image, play, mic, supplier |
| Nút, ô nhập | (vẽ khi chạy) | ảnh 9 lát bo góc cho từng trạng thái: thường / rê chuột / bấm / vô hiệu / có focus |

## 6. Thành phần (component)

### 6.1 Khung cửa sổ — `body(win, title)`
```
┌──────────────────────────────────────────────────────────────┐
│ [logo]  Tiêu đề màn hình (h1)          ≈≈≈ dải lụa vector ≈≈≈ │  header 64 px, ink-950
│         ABC Fashion · tên nhóm (small)                       │
├──────────────────────────────────────────────────────────────┤
│  nội dung (ink-900, lề 16 px)                                │
└──────────────────────────────────────────────────────────────┘
```
Tiêu đề thanh cửa sổ vẫn là `ABC Fashion — <tiêu đề>`. Cửa sổ có biểu tượng logo.

### 6.2 Nút
| Kiểu | Style ttk | Khi nào | Hình |
|---|---|---|---|
| Chính | `Primary.TButton` | hành động chính của màn hình (Lưu, Đăng nhập, Đặt hàng, Thanh toán, Tìm, Gửi, Xác nhận, Liên kết, Thêm vào giỏ…) và nút cuối của `button_row` | nền `blue-500`, chữ trắng |
| Phụ | `TButton` | mọi nút khác | nền `ink-800`, viền `ink-600`, chữ `text-100` |
| Nguy hiểm | `Danger.TButton` | Xoá, Huỷ đơn, Từ chối, Khoá tài khoản | nền `#3A1622`, viền + chữ `danger` |
| Ô trang chủ | `Tile.TButton` | các chức năng ở trang chủ | thẻ `ink-850` + biểu tượng, chữ trái |
| Liên kết | `Link.TButton` | Đăng xuất, Đăng ký, "Quay lại" | không nền, chữ `sky-300` |

Phân loại tự động theo chữ trên nút trong `_theme.polish()` (chạy sau khi màn hình dựng xong) — màn hình không cần biết style.

### 6.3 Ô nhập
`TEntry`, `TCombobox`, `TSpinbox`, `DateEntry`, `Text`: nền `ink-800`, viền 1 px `ink-600`, có focus thì viền `blue-500`, con trỏ `text-100`, bôi đen `blue-600`. Ô chỉ đọc: chữ `text-300`. Danh sách thả xuống: nền `ink-800`, dòng chọn `blue-600`.

### 6.4 Bảng (`make_table` / `fill_table`)
- Tiêu đề: nền `ink-800`, chữ `sky-300` Medium, không viền nổi.
- Dòng: nền `ink-850`, dòng xen kẽ `#101C32` (zebra), cao 1,9× dòng chữ.
- Đang chọn: nền `blue-600`, chữ trắng. Tag `bad` → chữ `danger`; tag `mark` → nền `warning` tối.
- Số / tiền canh phải (đã có).

### 6.5 Nhãn
| Style | Dùng |
|---|---|
| `TLabel` | chữ thường `text-100` |
| `Muted.TLabel` | gợi ý / chú thích `text-300` (thay `foreground="#555"`) |
| `H2.TLabel`, `H3.TLabel` | tiêu đề trong nội dung (thay `font=("Segoe UI", 12–14, "bold")`) |
| `Display.TLabel` | lời chào lớn |
| `Price.TLabel` | giá (h3, `sky-200`) |
| `Promo.TLabel`, `Success.TLabel`, `Danger.TLabel`, `Violet.TLabel` | trạng thái |
| `Field.TLabel` | nhãn bên trái ô nhập trong `form_rows` (`text-300`) |

Dòng thông báo `message_label` / `show`: lỗi `danger`, thành công `success`.

### 6.6 Thẻ, tab, khác
- `LabelFrame` = thẻ: nền `ink-850`, viền `ink-600`, tiêu đề `sky-300` Medium.
- `Notebook`: tab `ink-850`, tab chọn `ink-800` với chữ `sky-300`; nội dung `ink-850`.
- `Checkbutton` / `Radiobutton`: ô `ink-800`, chọn `blue-400`.
- Thanh cuộn: rãnh `ink-900`, tay nắm `ink-600`, rê chuột `ink-700`; mảnh.
- Canvas ảnh sản phẩm: nền `ink-850`; không có ảnh → khung nét đứt `ink-600` + chữ `text-500`.
- Hộp thoại `messagebox` dùng hộp thoại của Windows (không đổi được màu) — chấp nhận.

## 7. Bố cục màn hình mẫu

### 7.1 Đăng nhập
```
┌────────────────────────┬─────────────────────────────┐
│                        │  [logo] ABC Fashion (display)│
│   tranh vector         │  Thời trang cho mọi ngày     │
│   (login_art)          │                              │
│   mặt trăng, lụa,      │  E-mail      [____________]  │
│   giá treo 3 chiếc áo  │  Mật khẩu    [____________]  │
│                        │  thông báo lỗi               │
│                        │  [      Đăng nhập (chính)  ] │
│                        │  Đăng ký tài khoản khách →   │
└────────────────────────┴─────────────────────────────┘
```

### 7.2 Trang chủ (mọi vai trò)
```
┌──────────────────────────────────────────────┐
│ hero 132 px: "Xin chào …" (display)          │
│ vai trò (small)              ≈ lụa + móc áo ≈ │
├──────────────────────────────────────────────┤
│ [icon] Quản lý tài khoản  [icon] Quản lý SP   │  ô 2 cột, Tile.TButton
│ [icon] Duyệt đánh giá     [icon] Nhật ký      │
│                                 Đăng xuất →   │  Link.TButton
└──────────────────────────────────────────────┘
```
Trang chủ khách giữ ô tìm kiếm (Entry + nút Tìm chính + nút Tìm bằng ảnh có biểu tượng máy ảnh) phía trên lưới ô.

### 7.3 Màn hình danh sách / chi tiết
Header 64 px → thanh lọc (nhãn `Field`, ô nhập, nút Tìm chính) → bảng → thanh nút phải (nút chính ở cuối). Tiêu đề nội dung (số đơn, tên SP) dùng `H2`, trạng thái dùng `H3`.

## 8. Trải nghiệm (UX)

- Phím **Enter** ở ô tìm kiếm / đăng nhập vẫn kích hoạt hành động (đã có).
- Nút đang chờ (tìm bằng AI) chuyển sang trạng thái vô hiệu — style vô hiệu phải nhìn rõ là "mờ" (`text-500` trên `ink-800`).
- Thông báo lỗi luôn ngay dưới vùng nhập, không chỉ bằng màu: luôn có chữ.
- Con trỏ chuột "hand2" trên nút và ô trang chủ.
- Không đổi kích thước / vị trí widget theo trạng thái để tránh nhảy bố cục.

## 9. Ràng buộc với mô hình VP và kiểm thử

- Không đổi: tên lớp `XxxFrm`, tên widget có trong mô hình, tên và tham số `__init__` / `on_…`, các dòng `self.x_dao = XDAO()`.
- Được làm: thêm widget trang trí, thêm hàm riêng `_…`, đổi `font=` / `foreground=` thành `style=`, đổi bố cục.
- Toàn bộ theme nằm trong module riêng `view/_theme.py` và `view/_art.py` (bắt đầu bằng `_`, không tính vào 104 module thiết kế).
- Sau khi sửa: `python check_gen.py .`, `python vp2py.py ../vp_export/project.xml --check .` (0 lệch) và `pytest` phải đạt.

## 10. Triển khai (file nào làm gì)

| File | Việc |
|---|---|
| `view/_art.py` | hàm vẽ Pillow: logo, banner, hero, tranh đăng nhập, 22 biểu tượng, ảnh 9 lát cho nút / ô nhập |
| `view/_theme.py` | token màu, nạp font, `apply(root)` cấu hình toàn bộ style ttk + `option_add` cho Text / Listbox, `header()`, `polish(win)`, `icon()` |
| `view/_util.py` | `apply_theme` gọi `_theme.apply`; `body` vẽ header; `home_window` dựng lưới ô; `form_rows`, `button_row`, `message_label`, `make_table`, `show_image` dùng token |
| các `XxxFrm` | thay font / màu viết cứng bằng `style=`; màn hình đăng nhập và trang chủ khách dựng lại bố cục theo mục 7 |
| `make_ui_assets.py` | xuất phần tử đồ hoạ ra `media/ui/` (bản 2×) để xem và đưa vào báo cáo |

## 11. Trạng thái

Đã áp dụng cho cả 53 màn hình (2026-10-29). Ảnh chụp mẫu: `code/media/ui/screens/` (đăng nhập, trang chủ khách, chi tiết sản phẩm, trang chủ quản trị, xử lý đơn, tồn kho). Hai chỗ khác bản vẽ ban đầu: ô nhập góc vuông (mục 4); lời chào trang chủ nhân viên giữ nguyên chữ của từng màn hình (vd. "Xin chào … (quản lý)"), dòng phụ là tên vai trò.
