# Kế hoạch xây dựng các server mô phỏng bên liên quan

> **ĐÃ TRIỂN KHAI (2026-10-29).** Hướng dẫn vận hành nằm ở `external_services/README.md`. Phần dưới là kế hoạch gốc; các chỗ thực tế khác kế hoạch ghi ở đây.
>
> | Quyết định của bạn | Đã làm |
> |---|---|
> | Q1 FastAPI | FastAPI + uvicorn |
> | Q3 mỗi 3–5 giây cập nhật một trạng thái tới khi đã giao | vận đơn tự tiến 3–5 giây/bước; ứng dụng đồng bộ nền mỗi 3 giây, đơn tự sang "đã giao", khách nhận thư, các màn hình đơn / theo dõi kiện tự nạp lại |
> | Q4 chỉ mô phỏng ngân hàng, đủ số dư và điều kiện thì qua | ngân hàng 3 điều kiện (hạn mức, tài khoản không khoá, đủ số dư); bỏ trang liên kết thẻ và các mã ma thuật phức tạp |
> | Q5 dịch vụ nền, thư mục tách biệt, chỉ AI là thật | thư mục `external_services/` ngang hàng `code/`; `manage.py` chạy nền; AI chạy CLIP + Whisper + Ollama thật |
>
> **Khác kế hoạch gốc:** thư mục là `external_services/` (không phải `code/mocks/`); không làm trang liên kết thẻ trên trình duyệt, đối soát giao dịch, đồng hồ giả tua nhanh (vận chuyển đã chạy theo giây thật); thanh toán vẫn gọi đồng bộ (ngân hàng cục bộ trả lời dưới 50 ms) nên không đưa vào luồng phụ — chỉ tìm kiếm AI và trợ lý chạy luồng phụ, bằng hàng đợi (`run_in_thread`) vì không gọi Tk từ luồng phụ; Q2 thành "AI làm thật" (tầng B) theo yêu cầu bổ sung; `check_gen.py` bỏ qua module `_*` khi đếm gateway.

Mục tiêu: thay các gateway "sandbox trong tiến trình" hiện tại bằng gateway gọi **HTTP** tới các server mô phỏng chạy riêng, để hệ thống được chạy và trình diễn như đang nối với dịch vụ thật (cổng thanh toán, hãng vận chuyển, e-mail/SMS, dịch vụ AI) mà không cần tài khoản, tiền hay mô hình thật.

Tài liệu này là **kế hoạch**; chưa có dòng mã nào của các server được viết. Các số liệu về mã hiện tại lấy từ `code/abc_fashion/control/gateway/`.

---

## 1. Phạm vi

**Làm:**
- 4 server mô phỏng ứng với 4 hệ thống ngoài trong sơ đồ component: **Payment Service**, **Shipping Provider**, **Email/SMS Service**, **AI Model Service** (gồm tìm kiếm ảnh / giọng nói và trợ lý hỏi đáp).
- Đổi 5 gateway (`PaymentGateway`, `ShippingGateway`, `NotificationGateway`, `SearchEngine`, `AssistantEngine`) để gọi các server qua HTTP khi bật chế độ `http`, vẫn giữ chế độ `sandbox` hiện tại làm mặc định.
- Công cụ điều khiển hành vi (gây lỗi có chủ đích, tua nhanh thời gian), bộ kiểm thử hợp đồng, và tài liệu chạy.

**Không làm:** gọi dịch vụ thật (VNPay, MoMo, GHN, GHTK, nhà cung cấp SMS, OpenAI…); quản lý nhà cung cấp hàng (nhà cung cấp là người dùng của ứng dụng, không phải hệ thống ngoài); triển khai lên mạng ngoài máy dev.

**Giữ nguyên:** chữ ký của mọi hàm công khai trong gateway và Frm. Mọi việc bên dưới đều làm trong thân hàm hoặc hàm riêng `_…` để `vp2py.py --check` vẫn báo 0 lệch (xem mục 6).

---

## 2. Hiện trạng và các khoảng trống phải giải quyết

### 2.1. Hợp đồng gateway hiện có

| Gateway | Hàm | Vào → ra | Sandbox hiện tại |
|---|---|---|---|
| `PaymentGateway` | `charge(order, method)` | → `(ok, transaction_ref)` | thẻ có số che kết thúc `0002` bị từ chối, còn lại thành công |
| | `refund(payment)` | → `(ok, ref_hoàn)` | luôn thành công |
| | `link_method(customer, type, provider)` | → `PaymentMethod \| None` | sinh số che ngẫu nhiên `**** NNNN` |
| `ShippingGateway` | `create_shipment(shipment)` | → `(carrier, tracking_no)` | `GHN-SANDBOX`, `GHN########` |
| | `get_tracking(shipment)` | → `list[ShipmentEvent]` | mỗi lần gọi tiến thêm một bước |
| `NotificationGateway` | `send(notification)` | → `bool` | ghi vào `code/outbox.log` |
| `SearchEngine` | `search_by_image(bytes)` / `search_by_voice(bytes)` | → `list[int]` id style | so màu trung bình với `media/search_index.json`; giọng nói chỉ nhận file `.txt` |
| `AssistantEngine` | `ask`, `summarise_reviews`, `moderate` | → `dict` / `str` / `(bool, str)` | chế độ cơ bản bằng mẫu câu; đã có sẵn móc `ABC_FASHION_LLM_URL` (POST `{system, prompt}` → `{text}`) |

### 2.2. Khoảng trống cần xử lý khi chuyển sang HTTP

| # | Khoảng trống | Hệ quả | Hướng xử lý |
|---|---|---|---|
| G1 | `Notification` không có địa chỉ nhận (chỉ có `customerId`) và gateway không được đọc CSDL | server e-mail / SMS không biết gửi tới đâu | `notify()` trong `view/_util.py` gắn thêm `notification.recipient` (e-mail hoặc điện thoại của khách, view đã có `customer`) trước khi gọi gateway — thuộc tính động, đúng quy ước của dự án |
| G2 | Gateway hiện không có hàm hỏi trạng thái giao dịch | không xử lý được thanh toán bất đồng bộ, và không đối soát khi ứng dụng sập giữa `charge` và `add_payment` | giai đoạn 1 giữ thanh toán đồng bộ; đối soát làm bằng hàm riêng `_find_charge(order_no)` + công cụ dòng lệnh (mục 5.1), không thêm hàm công khai |
| G3 | Ứng dụng desktop không nhận được webhook | trang liên kết thẻ / thanh toán do bên thứ ba lưu trữ cần "báo ngược" | dùng **polling**: gateway mở trình duyệt tới trang của server mô phỏng rồi hỏi kết quả theo chu kỳ |
| G4 | `ShipmentDAO.add_shipment_event` loại sự kiện trùng theo `(shipmentId, status, occurred_at)` | nếu server trả mốc thời gian khác nhau cho cùng một sự kiện mỗi lần hỏi thì sẽ tạo bản ghi trùng | server vận chuyển phải trả **lịch sử ổn định**: mỗi sự kiện có mốc thời gian cố định, tính một lần |
| G5 | `check_gen.py` đếm **mọi lớp** trong `control/gateway/` là một gateway (yêu cầu đúng 5) | lớp trợ giúp HTTP làm hỏng phép đếm | module trợ giúp dùng **hàm**, không dùng lớp; hoặc cho `check_gen.py` bỏ qua module bắt đầu bằng `_` |
| G6 | Gateway chạy trong luồng giao diện, gọi mạng chậm sẽ đứng cửa sổ | `charge`, `link_method`, tìm ảnh có thể chậm hàng giây | gọi trong luồng phụ rồi quay về luồng giao diện bằng `after()` (mẫu đã dùng ở `AssistantFrm`); DAO vẫn chỉ gọi ở luồng giao diện (mục 11 quy tắc 6) |

---

## 3. Kiến trúc đích

```
┌────────────────────────── máy dev (127.0.0.1) ───────────────────────────┐
│                                                                          │
│  ABC Fashion Desktop App                                                 │
│   view → control.dao ──► PostgreSQL abc_fashion_v2                       │
│          control.gateway ──HTTP/JSON──┬──► mock-payment    :8101         │
│            (chế độ http)              ├──► mock-shipping   :8102         │
│            (chế độ sandbox = như cũ)  ├──► mock-notify     :8103         │
│                                       └──► mock-ai         :8104         │
│                                                                          │
│  Mỗi server: FastAPI + SQLite riêng (trạng thái) + /__admin (điều khiển) │
│  mocks/run_all.py khởi động cả bốn; mỗi server chạy riêng được           │
└──────────────────────────────────────────────────────────────────────────┘
```

### 3.1. Cấu trúc thư mục (ngoài `abc_fashion/` để không lẫn vào phép đếm 104 module)

```
code/
├── abc_fashion/...                 (như hiện tại)
└── mocks/
    ├── common/                      dùng chung: khung FastAPI, SQLite, đồng hồ giả, admin, log
    │   ├── app.py                   tạo app, middleware (khoá API, mã yêu cầu, log JSON)
    │   ├── store.py                 SQLite một file / server, lưu trạng thái + nhật ký gọi
    │   ├── clock.py                 đồng hồ giả: nhân tốc độ, đặt / tiến thời gian
    │   └── chaos.py                 quy tắc gây lỗi: trễ, 5xx, từ chối, theo "giá trị ma thuật"
    ├── payment/   server.py  pages/  (trang liên kết thẻ HTML)
    ├── shipping/  server.py
    ├── notify/    server.py  inbox.html (xem thư / tin nhắn đã "gửi")
    ├── ai/        server.py  search.py  assistant.py  moderation.py
    ├── run_all.py                   chạy 4 server, in cổng và khoá API
    └── README.md
```

### 3.2. Cấu hình (biến môi trường; không đặt thì giữ sandbox hiện tại)

| Biến | Giá trị | Ý nghĩa |
|---|---|---|
| `ABC_FASHION_GATEWAY_MODE` | `sandbox` (mặc định) / `http` | công tắc chung |
| `ABC_FASHION_PAYMENT_URL` | `http://127.0.0.1:8101` | ghi đè từng gateway |
| `ABC_FASHION_SHIPPING_URL` | `http://127.0.0.1:8102` | |
| `ABC_FASHION_NOTIFY_URL` | `http://127.0.0.1:8103` | |
| `ABC_FASHION_AI_URL` | `http://127.0.0.1:8104` | thay cho `ABC_FASHION_LLM_URL` (vẫn đọc biến cũ) |
| `ABC_FASHION_<X>_KEY` | chuỗi bất kỳ | khoá API từng dịch vụ, gửi ở header `Authorization: Bearer …` |
| `ABC_FASHION_HTTP_TIMEOUT` | giây (mặc định 15; liên kết thẻ 120) | thời gian chờ |

### 3.3. Chính sách khi dịch vụ lỗi (khớp mục 5.5 và 7.4 của `HUONG_DAN_CODE.md`)

| Gateway | Không kết nối được / quá hạn | Bị từ chối / lỗi nghiệp vụ |
|---|---|---|
| Payment `charge`, `refund` | **ném lỗi** (hợp đồng: "chỉ ném khi không kết nối được"); view hiện hộp "Lỗi hệ thống"; đơn giữ `pending_payment` | trả `(False, ref)` |
| Payment `link_method` | ném lỗi | trả `None` (khách huỷ) |
| Shipping | ném lỗi (không tạo vận đơn, đơn giữ nguyên trạng thái) | — |
| Notification `send` | trả `False` → bản ghi `failed`, **không chặn nghiệp vụ** | trả `False` |
| Search | ném lỗi → view hiện gợi ý "tìm bằng chữ" (đã có) | trả `[]` |
| Assistant `ask` | **tự lùi về chế độ cơ bản** (đã có) | câu sai bị lọc, ghi `GroundingEvent` (đã có) |

---

## 4. Nguyên tắc thiết kế chung cho mọi server

1. **Có trạng thái, lưu bền** (SQLite): giao dịch, vận đơn, thư đã gửi vẫn còn sau khi khởi động lại; nhờ đó thử được hoàn tiền một phần, đối soát, theo dõi nhiều lần.
2. **Tất định**: cùng đầu vào → cùng kết quả. Kết quả đặc biệt kích hoạt bằng "giá trị ma thuật" trong dữ liệu vào (số thẻ, địa chỉ, câu hỏi…), được ghi trong README từng server. Không dùng ngẫu nhiên trừ khi truyền `seed`.
3. **Đồng hồ giả**: mọi tiến trình theo thời gian (vận đơn đi qua các bước, giao dịch chờ) dùng đồng hồ của server, có hệ số tua nhanh (`POST /__admin/clock {"speed": 600}` = 1 giây thật bằng 10 phút).
4. **Idempotency**: `POST` tạo giao dịch / vận đơn nhận header `Idempotency-Key`; gửi lại cùng khoá trả lại kết quả cũ, không tạo thêm. Gateway dùng khoá `"{order_no}:{lần thử}"`.
5. **Điều khiển và quan sát** qua `/__admin/*` (chỉ bind `127.0.0.1`):
   - `GET /__admin/calls` — nhật ký mọi yêu cầu đã nhận (để test khẳng định "gateway gọi đúng một lần");
   - `POST /__admin/behavior` — đặt hành vi toàn cục (vd. `{"fail_next": 2, "status": 503}`, `{"latency_ms": 3000}`);
   - `POST /__admin/reset` — xoá trạng thái;
   - `POST /__admin/clock` — chỉnh đồng hồ.
6. **Bảo mật mô phỏng**: yêu cầu có khoá API, sai khoá trả 401; server **không bao giờ lưu số thẻ đầy đủ** — chỉ `last4` và token, đúng NFR04. Trang nhập thẻ của mô phỏng chỉ giữ `last4` rồi bỏ phần còn lại.
7. **Định dạng lỗi thống nhất**: `{"error": {"code": "card_declined", "message": "…"}}` kèm mã HTTP đúng (4xx nghiệp vụ, 5xx hệ thống).
8. **Chạy trên một dòng lệnh**: `python mocks/run_all.py` rồi đặt `ABC_FASHION_GATEWAY_MODE=http`.

---

## 5. Đặc tả từng server

### 5.1. Payment Service — cổng 8101 (mô phỏng VNPay / MoMo / thẻ)

**Endpoint**

| Phương thức | Đường dẫn | Dùng cho | Ghi chú |
|---|---|---|---|
| POST | `/v1/charges` | `PaymentGateway.charge` | body: `order_no`, `amount`, `currency=VND`, `method` (`card` / `e_wallet` / `bank_transfer`), `payment_method_token` (có thể rỗng); trả `{id, status, transaction_ref}` |
| POST | `/v1/refunds` | `PaymentGateway.refund` | body: `transaction_ref`, `amount`; từ chối nếu tổng hoàn vượt số đã thu |
| GET | `/v1/charges?reference={order_no}` | đối soát (G2) | liệt kê giao dịch của một đơn |
| POST | `/v1/link-sessions` | `PaymentGateway.link_method` | tạo phiên liên kết, trả `{session_id, url}` |
| GET | `/link/{session_id}` | trang HTML của "nhà cung cấp" | khách chọn loại, nhập thẻ giả, bấm Đồng ý / Huỷ |
| GET | `/v1/link-sessions/{id}` | gateway hỏi kết quả (polling, G3) | `pending` / `completed` (kèm `provider`, `type`, `last4`, `token`) / `cancelled` / `expired` |

**Luồng `link_method`:** gateway tạo phiên → `webbrowser.open(url)` → hỏi kết quả mỗi 1 giây tới khi xong hoặc hết hạn (mặc định 120 giây) → dựng `PaymentMethod(provider, method_type, masked_number="**** last4")`. Chạy trong luồng phụ (G6) để cửa sổ không đứng.

**Giá trị ma thuật theo `last4` của thẻ** (bảng chung với sandbox hiện tại để hành vi nhất quán):

| `last4` | Kết quả `charge` |
|---|---|
| bất kỳ khác | thành công |
| `0002` | từ chối `card_declined` (đã có trong sandbox, dùng thử UC08 E2) |
| `9995` | từ chối `insufficient_funds` |
| `0119` | lỗi hệ thống 502 (thử xử lý ngoại lệ) |
| `0341` | chậm 20 giây rồi thành công (thử luồng phụ, hết thời gian chờ) |

Với `bank_transfer` và `e_wallet` không có token: thành công ngay (như sandbox). `amount` ≥ 50.000.000 đ bị từ chối `amount_too_large` (thử UC08 với đơn lớn).

**Sau khi dựng xong, kiểm chứng:** thanh toán thẻ thường, thẻ `0002`, thanh toán lại bằng thẻ khác (ConfirmOrderFrm), hoàn tiền một phần hai lần rồi lần thứ ba vượt hạn mức bị từ chối, gửi lại cùng `Idempotency-Key` không tạo thêm giao dịch.

### 5.2. Shipping Provider — cổng 8102 (mô phỏng GHN / GHTK)

**Endpoint**

| Phương thức | Đường dẫn | Dùng cho |
|---|---|---|
| POST | `/v1/shipments` | `ShippingGateway.create_shipment`: body `direction`, `service_level`, `from` / `to` (kho, địa chỉ), `items`, `fee`, `client_ref` (id kiện của ứng dụng); trả `{carrier, tracking_no, eta}` |
| GET | `/v1/shipments/{tracking_no}/events` | `ShippingGateway.get_tracking`: trả **toàn bộ lịch sử** `[{status, occurred_at, note}]` |
| POST | `/v1/shipments/{tracking_no}/cancel` | dự phòng (huỷ kiện chưa lấy hàng) |

**Hành vi**
- Hãng chọn theo `service_level`: `standard` → `GHTK`, `express` → `GHN`; mã vận đơn có tiền tố hãng (`GHTK2000001`).
- **Lịch trình theo đồng hồ giả**, mặc định (thời gian thật, chia cho hệ số tua): `requested` → `picked_up` sau 30 phút → `in_transit` sau 2 giờ → `delivered` sau 24 giờ (`standard`) / 8 giờ (`express`). Hướng `return` (lấy hàng trả) dùng cùng lịch.
- **Lịch sử ổn định (G4):** mốc thời gian của mỗi sự kiện được tính một lần từ lúc tạo vận đơn rồi lưu; hỏi lại luôn trả đúng các mốc đó, chỉ thêm sự kiện mới khi đồng hồ đã đi qua.
- **Giá trị ma thuật theo địa chỉ nhận:** quận/huyện chứa `FAIL` → kiện giao thất bại (`failed`) sau lần lấy hàng; `SLOW` → thêm 48 giờ.
- Lỗi nhập: thiếu địa chỉ → 422 `invalid_address`.

**Nối với nghiệp vụ hiện có:** `TrackShipmentFrm.on_refresh` gọi `get_tracking` rồi `add_shipment_event` (bỏ trùng) → cập nhật `Shipment.status`. `ManageOrderFrm.on_update_status` vẫn do quản lý bấm; mô phỏng không tự đổi trạng thái đơn (xem mục 9, câu hỏi Q3).

### 5.3. Email/SMS Service — cổng 8103

**Endpoint**

| Phương thức | Đường dẫn | Dùng cho |
|---|---|---|
| POST | `/v1/messages` | `NotificationGateway.send`: body `channel` (`email` / `sms` / `app`), `to`, `event_type`, `body`, `client_ref`; trả `{id, status}`, mã 202 |
| GET | `/v1/messages?to=&event_type=` | xem / kiểm thử |
| GET | `/inbox` | trang HTML xem hộp thư giả (để trình diễn: khách "nhận" mail xác nhận đơn) |

**Hành vi:** ghi thư vào SQLite; `to` có đuôi `@bounce.test` hoặc số điện thoại kết thúc `0000` → trả 422 `invalid_recipient` (gateway trả `False` → bản ghi `failed`); giới hạn 30 thư / phút / người nhận (429); `latency_ms` điều chỉnh được.

**Thay đổi ứng dụng:** `notify()` gắn `recipient` (G1): e-mail với kênh `email`, điện thoại với kênh `sms`. `EditRestockRequestFrm.on_send` (báo nhà cung cấp) cũng truyền e-mail nhà cung cấp.

### 5.4. AI Model Service — cổng 8104 (CLIP, Whisper, LLM của Chương 3)

Hai nhóm endpoint trong cùng một server (một hệ thống ngoài trong sơ đồ component).

**Tìm kiếm (`SearchEngine`)**

| Phương thức | Đường dẫn | Ghi chú |
|---|---|---|
| POST | `/v1/search/image` | body ảnh (multipart); trả `{ids: [style_id…], scores: […]}` giảm dần, tối đa 20 |
| POST | `/v1/search/voice` | body âm thanh; trả `{transcript, ids}` |
| PUT | `/v1/search/index` | nạp lại chỉ mục từ `media/search_index.json` (script `db/setup_db.py --index` gọi) |

**Trợ lý (`AssistantEngine`)**

| Phương thức | Đường dẫn | Ghi chú |
|---|---|---|
| POST | `/v1/assistant/chat` | `{system, prompt}` → `{text, model}` (tương thích móc `ABC_FASHION_LLM_URL` hiện có) |
| POST | `/v1/assistant/summarise` | `{reviews: […]}` → `{summary}` |
| POST | `/v1/assistant/moderate` | `{text}` → `{approved, reason}` |

**Hai tầng triển khai, chọn theo máy:**

| Tầng | Cách làm | Dùng khi |
|---|---|---|
| **A — mô phỏng tất định** (mặc định) | ảnh: so màu trung bình + lược đồ màu với chỉ mục; giọng nói: chấp nhận bản ghi `.txt` hoặc file âm thanh có tên chứa từ khoá (`ao-so-mi.wav`); chat: sinh câu từ **dữ liệu trong `prompt`**; moderate / summarise: quy tắc như trong gateway hiện tại | không cần GPU, không tải mô hình, chạy ngay |
| **B — mô hình nhẹ thật** (tuỳ chọn) | `open_clip` (ViT-B/32) cho ảnh, `faster-whisper` (tiny) cho giọng nói | máy có Python ≥ 3.11 và vài GB đĩa; cần `pip install` thêm, nên tách `requirements-ai.txt` |

**Chế độ gây lỗi riêng của trợ lý** — mục đích: **kiểm thử bộ lọc grounding (NFR14)**. Đặt `POST /__admin/behavior {"assistant_mode": "hallucinate"}` thì `chat` cố ý chèn các câu sai: giá không có trong dữ liệu, "còn hàng" khi hết hàng, tác dụng sức khoẻ, "mẫu bán chạy nhất". Gateway phải loại các câu này và ghi `GroundingEvent` (kiểm tra `price`, `stock`, `health`, `popularity`). Chế độ `slow` thử luồng phụ; `down` thử việc lùi về chế độ cơ bản.

---

## 6. Thay đổi cần làm trong ứng dụng

Mọi thay đổi nằm trong thân hàm hoặc hàm riêng, **không đổi chữ ký công khai** (nên `vp2py.py --check` vẫn 0 lệch).

| Thành phần | Thay đổi |
|---|---|
| `control/gateway/_http.py` (mới) | chỉ chứa **hàm** (G5): `post_json`, `get_json`, `post_file`, đọc cấu hình, đặt khoá API / timeout / `Idempotency-Key`, chuyển lỗi mạng thành `GatewayUnavailable(Exception)` — lớp ngoại lệ duy nhất; nếu `check_gen.py` đếm nó thì thêm quy tắc bỏ qua `Exception` hoặc module `_*` |
| 5 gateway | mỗi hàm công khai: nếu chế độ `http` thì gọi qua `_http`, ngược lại chạy sandbox như cũ. Đặt logic sandbox thành hàm riêng `_charge_sandbox`… để đọc dễ |
| `view/_util.py::notify` | gắn `notification.recipient` (G1) |
| `LinkPaymentMethodFrm.on_link`, `ConfirmOrderFrm.on_retry_payment`, `CheckoutFrm.on_place_order`, `SearchStyleFrm.on_search_by_image/voice` | gọi gateway trong luồng phụ (G6): hiện nút "Đang xử lý…" rồi dùng `after()` để cập nhật; DAO vẫn chỉ ở luồng giao diện |
| `check_gen.py` | giữ phép đếm gateway = 5 (xem G5); thêm kiểm tra: gateway không import `psycopg` (đã có) |
| `requirements.txt` | không thêm gì cho ứng dụng (dùng `urllib`); `mocks/requirements.txt` riêng: `fastapi`, `uvicorn`, `python-multipart`; `requirements-ai.txt` tuỳ chọn |
| `main.py` | in một dòng log chế độ gateway đang dùng; nếu `http` mà dịch vụ không phản hồi `GET /health` thì cảnh báo ở màn hình đăng nhập (không chặn) |

**Không cần sửa mô hình VP:** các hàm mới đều riêng tư; thuộc tính `recipient` là thuộc tính động (cùng quy ước với `order.items`…).

---

## 7. Kiểm thử

### 7.1. Kiểm thử hợp đồng dùng chung cho hai chế độ

Một bộ test tham số hoá chạy **cả hai** triển khai (sandbox trong tiến trình và HTTP tới server mô phỏng) với cùng khẳng định:

| Gateway | Ca kiểm thử |
|---|---|
| Payment | thẻ thường thành công; `0002` bị từ chối; COD / chuyển khoản không có token; hoàn tiền; hoàn vượt hạn mức → `False`; liên kết thẻ trả số đã che 4 chữ số cuối, không lộ số đầy đủ |
| Shipping | `create_shipment` trả tiền tố hãng đúng; `get_tracking` trả lịch sử không đổi khi hỏi hai lần liên tiếp; sau khi tua đồng hồ có thêm sự kiện và `delivered` |
| Notification | gửi thành công; người nhận lỗi → `False`; vượt giới hạn → `False` |
| Search | ảnh quần jeans trả đúng style đứng đầu (đã kiểm với 4 ảnh thật); giọng nói `.txt` |
| Assistant | trả lời từ dữ liệu; chế độ `hallucinate` bị lọc đúng 3 loại sự kiện; dịch vụ tắt → chế độ cơ bản |

Server chạy trong test bằng `uvicorn` ở luồng riêng trên cổng ngẫu nhiên, trạng thái SQLite ở thư mục tạm; không cần bật tay.

### 7.2. Kịch bản lỗi và nơi kiểm chứng

| Kịch bản | Điều khiển bằng | Kỳ vọng | UC / NFR |
|---|---|---|---|
| thẻ bị từ chối rồi thanh toán lại | thẻ `0002` | đơn giữ `pending_payment`, hàng vẫn giữ, thanh toán lại bằng thẻ khác thành công | UC08 E2 |
| cổng thanh toán sập khi bấm Đặt hàng | tắt server 8101 | hộp "Lỗi hệ thống", không mất đơn, ứng dụng không tắt | NFR07 |
| thanh toán chậm 20 giây | thẻ `0341` | cửa sổ không đứng; hết thời gian chờ báo rõ | G6 |
| hoàn tiền vượt số đã thu | `/v1/refunds` | `refund_order` chặn trước khi gọi, server cũng từ chối | UC10, UC18 |
| gửi lại cùng yêu cầu | `Idempotency-Key` | không thu hai lần | G2 |
| e-mail báo xác nhận thất bại | người nhận `@bounce.test` | `Notification.status = failed`, đơn vẫn xác nhận | UC08 |
| hãng giao thất bại | quận `FAIL` | kiện `failed`, đơn không tự `delivered` | UC11 |
| tìm ảnh khi AI tắt | tắt server 8104 | thông báo gợi ý tìm bằng chữ | UC05 |
| trợ lý bịa giá | `assistant_mode=hallucinate` | câu sai bị loại, ghi `GroundingEvent` | UC32, NFR14 |

### 7.3. Kịch bản trình diễn khép kín

Bật cả 4 server → đăng ký khách → tìm bằng ảnh → hỏi trợ lý → đặt đơn 2 kho, thẻ `0002` thất bại rồi thanh toán lại → mở `/inbox` thấy thư xác nhận → quản lý giao 2 kiện → tua đồng hồ 10 phút/giây → khách bấm "Cập nhật" thấy kiện `delivered` → trả hàng → hoàn tiền → mở `/v1/charges?reference=…` thấy đủ lần thu và hoàn.

---

## 8. Lộ trình

Ước lượng là ngày làm việc của một người, đã gồm viết test.

| GĐ | Nội dung | Sản phẩm | Tiêu chí hoàn thành | Ước lượng |
|---|---|---|---|---|
| 0 | Nền tảng: `mocks/common`, `_http.py`, công tắc chế độ, `run_all.py`, test hợp đồng cho chế độ sandbox | khung chạy được, 5 gateway vẫn mặc định sandbox | toàn bộ 53 test hiện có vẫn đạt; test hợp đồng đạt ở chế độ sandbox | 1,5 |
| 1 | **Notification** (đơn giản nhất, dựng quy trình) | server 8103, `/inbox`, G1 | 3 ca hợp đồng đạt ở cả hai chế độ; thư xác nhận đơn hiện trong `/inbox` | 0,5 |
| 2 | **Shipping** | server 8102, đồng hồ giả, lịch sử ổn định (G4) | `TrackShipmentFrm` cập nhật đúng nhiều lần không sinh sự kiện trùng; kiện đi tới `delivered` khi tua giờ | 1,5 |
| 3 | **Payment** | server 8101, trang liên kết thẻ, idempotency, hoàn một phần, luồng phụ (G6) | kịch bản UC08 E2; liên kết thẻ qua trình duyệt; hoàn vượt hạn mức bị chặn | 3 |
| 4A | **AI tầng A** | server 8104: tìm ảnh, tìm giọng nói, chat / moderate / summarise, chế độ `hallucinate` | 4 ảnh thật trả đúng sản phẩm đầu; bộ lọc grounding loại đủ 3 loại câu sai | 2 |
| 4B | AI tầng B (tuỳ chọn) | CLIP + Whisper nhẹ | ảnh chụp khác góc vẫn ra đúng sản phẩm; nói "áo sơ mi" ra đúng style | 2 |
| 5 | Hoàn thiện: README từng server, kịch bản trình diễn 7.3 chạy tự động, cập nhật tài liệu và báo cáo | `mocks/README.md`, mục dưới | cả bộ test + kịch bản 7.3 đạt; `check_gen.py` và `vp2py.py --check` vẫn sạch | 1 |

Tổng: **khoảng 9,5 ngày** (11,5 nếu làm cả 4B). Thứ tự 1 → 2 → 3 → 4A nhằm làm sớm phần đơn giản để chốt khuôn (cấu hình, test hợp đồng, luồng phụ), rồi tới phần phức tạp.

---

## 9. Rủi ro và quyết định cần bạn chọn

### Quyết định

| # | Câu hỏi | Gợi ý |
|---|---|---|
| Q1 | Khung web cho server: **FastAPI + uvicorn** (thêm 3 gói, có tài liệu OpenAPI tự sinh) hay **`http.server` thuần** (không gói nào, nhưng phải tự viết định tuyến, multipart) | FastAPI. Tài liệu OpenAPI còn dùng được làm phụ lục báo cáo mô tả giao diện với hệ thống ngoài |
| Q2 | Có làm tầng AI **B** (mô hình thật) không | Không bắt buộc. Nên nói rõ trong báo cáo: mô phỏng tầng A thể hiện đúng hợp đồng giao diện; mô hình thật là phần Chương 3 |
| Q3 | Khi kiện `delivered`, có tự chuyển đơn sang `delivered` không | Hiện do quản lý bấm (đúng mục 9.7). Tự động cần một tác vụ nền hoặc nút "Đồng bộ vận chuyển"; nên để sau |
| Q4 | Thanh toán **bất đồng bộ** thật (ví điện tử trả kết quả sau vài phút) có cần không | Giai đoạn này không: giữ đồng bộ. Làm được cần thêm trạng thái chờ và cách hỏi lại — có thể phải sửa mô hình VP (hàm công khai mới) |
| Q5 | Chạy các server bằng một dòng lệnh hay thành dịch vụ nền | Một dòng lệnh (`run_all.py`) là đủ cho trình diễn |

### Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Cổng trùng hoặc bị tường lửa chặn khi trình diễn | thấp | cổng cấu hình được; chỉ bind `127.0.0.1`; `run_all.py` kiểm cổng trước khi chạy |
| Luồng phụ truy cập DAO / widget gây lỗi khó tái hiện | **trung bình** | quy tắc cứng: luồng phụ chỉ gọi gateway, kết quả trả về qua `after()`; thêm test mở cửa sổ + gọi qua luồng phụ |
| Hành vi mô phỏng khác dịch vụ thật khiến báo cáo bị hỏi "thật thì sao" | thấp | mỗi server có mục "Khác biệt so với dịch vụ thật" trong README; không tuyên bố tích hợp thật |
| Giữ hai triển khai (sandbox và http) làm tăng bảo trì | thấp | test hợp đồng chạy cả hai; sandbox giữ nguyên, chỉ sửa khi hợp đồng đổi |
| Mô hình AI tầng B nặng, cài lỗi trên máy khác | trung bình | tách `requirements-ai.txt`; tầng A luôn là mặc định |
| Đổi mã gateway làm lệch mô hình VP | thấp | `vp2py.py --check` nằm trong bộ test, chạy mỗi lần |

---

## 10. Cập nhật báo cáo sau khi làm xong

- **Hình 4.43 (component):** giữ nguyên bốn hệ thống ngoài; thêm chú thích "được mô phỏng bằng các server HTTP cục bộ khi phát triển và trình diễn".
- **Mục 4.4:** thêm bảng giao diện với hệ thống ngoài (mục 5 của tài liệu này, lấy từ OpenAPI sinh tự động) và sơ đồ triển khai (mục 3).
- **Phần kiểm thử:** thêm bảng kịch bản lỗi (mục 7.2) và ghi nhận NFR07 / NFR14 được kiểm chứng bằng cách gây lỗi có chủ đích.
- **Phần hạn chế:** nêu rõ đây là mô phỏng; chưa nối dịch vụ thật.
