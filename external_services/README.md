# external_services — các bên liên quan bên ngoài hệ thống

Thư mục này **tách biệt hoàn toàn** với hệ thống chính (`../code/`): không import mã của nhau, chỉ nói chuyện qua HTTP/JSON. Các gateway của ứng dụng (`code/abc_fashion/control/gateway/`) gọi vào đây khi bật chế độ `http`.

| Dịch vụ | Thư mục | Cổng | Loại | Đóng vai |
|---|---|---|---|---|
| `payment` | `payment_bank/` | 8101 | **mô phỏng** | ngân hàng / cổng thanh toán |
| `shipping` | `shipping/` | 8102 | **mô phỏng** | hãng vận chuyển GHN / GHTK |
| `notify` | `notify/` | 8103 | **mô phỏng** | dịch vụ e-mail / SMS |
| `ai` | `ai_service/` | 8104 | **THẬT** | CLIP, Whisper, LLM chạy trên GPU / Ollama |

Chỉ có `ai` chạy mô hình thật. Ba dịch vụ còn lại cố ý giữ đơn giản.

## Cài đặt và chạy

```
cd external_services
python manage.py setup            # 3 dịch vụ mô phỏng (môi trường ảo .venv, vài MB)
python manage.py setup --ai       # dịch vụ AI: môi trường ảo riêng, torch CUDA (~4 GB). Cần Ollama + `ollama pull qwen2.5:3b`

python manage.py start            # chạy NỀN (không cửa sổ), tất cả dịch vụ đã cài
python manage.py status           # trạng thái; với ai có thêm tình trạng nạp mô hình
python manage.py stop [tên]       # restart [tên] · logs <tên> [-n 40] · reset [tên] (xoá trạng thái dịch vụ mô phỏng)
python manage.py autostart install    # (tuỳ chọn) tự chạy khi đăng nhập Windows; `remove` để gỡ — chỉ chạy khi bạn gọi
```

Lần chạy đầu của `ai` tải CLIP (~0,6 GB) và Whisper large-v3-turbo (~1,6 GB) về `~/.cache/huggingface`, mất vài phút; các lần sau nạp trong khoảng 10 giây. Log ở `run/<tên>.log`, trạng thái SQLite ở `run/<tên>.sqlite` (xoá được bất cứ lúc nào).

## Nối với ứng dụng

Ứng dụng mặc định chạy chế độ `sandbox` (giả lập trong tiến trình, như trước). Để dùng các dịch vụ này:

```powershell
$env:ABC_FASHION_GATEWAY_MODE = "http"        # lâu dài: setx ABC_FASHION_GATEWAY_MODE http
cd ..\code
..\.venv\Scripts\python.exe -m abc_fashion.main
```

Ở chế độ `http`, khi khởi động ứng dụng còn:
- **đồng bộ vận chuyển nền**: cứ 3 giây hỏi hãng về các kiện đang đi, ghi sự kiện mới, đưa đơn tới "đã giao" và báo khách;
- **đẩy danh mục sản phẩm lên dịch vụ AI** (tên, mô tả, màu, ảnh) để tìm bằng ảnh / giọng nói.

Biến môi trường ghi đè: `ABC_FASHION_<PAYMENT|SHIPPING|NOTIFY|AI>_URL` và `_KEY`, `ABC_FASHION_HTTP_TIMEOUT`. Khoá API mặc định (môi trường dev) là `dev-<tên>-key`; đổi bằng `EXT_<TÊN>_KEY` khi chạy dịch vụ.

Chính sách khi dịch vụ lỗi: thanh toán / vận chuyển → ném lỗi (hộp "Lỗi hệ thống", đơn giữ nguyên trạng thái); e-mail / SMS → trả `False` (bản ghi `failed`, không chặn nghiệp vụ); tìm kiếm → báo lỗi và gợi ý tìm bằng chữ; trợ lý → tự lùi về chế độ cơ bản.

## Hành vi từng dịch vụ

### payment — ngân hàng (mô phỏng, đơn giản)
Giao dịch qua nếu **đủ số dư và đủ điều kiện**:
1. số tiền > 0 và ≤ 100.000.000 đ một giao dịch;
2. tài khoản (xác định bằng 4 số cuối của thẻ) không bị khoá;
3. số dư ≥ số tiền (bị trừ khi qua).

Tài khoản chưa từng thấy được mở tự động với 50.000.000 đ. COD / chuyển khoản / ví chưa liên kết chỉ cần điều kiện 1. Tài khoản mẫu: `4242` (100 triệu), `0002` (bị khoá — thử thanh toán thất bại), `9995` (chỉ 100.000 đ — thử không đủ số dư). Liên kết thẻ mở tài khoản mới và chỉ trả 4 số cuối (không bao giờ nhận hay lưu số thẻ đầy đủ). Hoàn tiền: không vượt phần còn hoàn được của giao dịch thu; giao dịch ngoài ngân hàng (COD, dữ liệu cũ) coi như qua. Hỗ trợ header `Idempotency-Key`.
Xem sổ cái: http://127.0.0.1:8101/ledger · đổi số dư: `PUT /__admin/accounts/{last4}` `{"balance": 1000, "status": "blocked"}`.

### shipping — hãng vận chuyển (mô phỏng)
Vận đơn tự tiến **một trạng thái sau mỗi 3–5 giây** cho tới khi giao xong: `requested → picked_up → in_transit → delivered`. `standard` → hãng `GHTK`, `express` → `GHN`. Khoảng cách giữa các bước được tính một lần khi tạo và lưu lại, nên hỏi lịch sử nhiều lần vẫn trả đúng các mốc thời gian cũ (ứng dụng loại sự kiện trùng theo mốc này). Quận / huyện nhận có chữ `FAIL` thì kiện kết thúc `failed`. Xem bảng theo dõi: http://127.0.0.1:8102/board.

### notify — e-mail / SMS (mô phỏng)
Nhận thư, lưu lại, xem tại http://127.0.0.1:8103/inbox. Người nhận lỗi bị từ chối (ứng dụng ghi `failed`): e-mail kết thúc `@bounce.test` hoặc không có `@`; số điện thoại kết thúc `0000` hoặc ngắn hơn 9 chữ số.

### ai — dịch vụ AI THẬT
| Chức năng | Mô hình | Cách làm |
|---|---|---|
| Tìm bằng ảnh | CLIP ViT-B/32 (GPU) | vector ảnh truy vấn so cosine với vector ảnh sản phẩm (85%) và mô tả chữ (15%); ~30–60 ms |
| Tìm bằng giọng nói | Whisper large-v3-turbo → LLM → CLIP | nhận dạng giọng nói → LLM đổi thành cụm từ khoá tiếng Anh → CLIP chữ↔ảnh (60%) + trùng từ khoá (40%); câu không liên quan trả rỗng (ngưỡng cosine 0,24, hiệu chỉnh trên dữ liệu thật) |
| Trợ lý hỏi đáp | Ollama `qwen2.5:3b` | trả lời từ dữ liệu sản phẩm do ứng dụng gửi; ứng dụng còn lọc lại các câu sai giá / tồn / sức khoẻ (NFR14) |
| Tóm tắt đánh giá | cùng LLM | 2–3 câu, chỉ dựa trên đánh giá thật |
| Kiểm duyệt đánh giá | quy tắc (e-mail, điện thoại, đường dẫn) + LLM | lời chê lịch sự vẫn hợp lệ; thô tục, quảng cáo, không liên quan thì bị chờ duyệt |

Đổi mô hình bằng biến môi trường trước khi chạy: `AI_CLIP_MODEL`, `AI_WHISPER_MODEL` (vd. `openai/whisper-small` cho máy yếu), `AI_LLM_MODEL` (vd. `qwen2.5:7b`), `OLLAMA_URL`. Chỉ mục sản phẩm lưu ở `run/ai_index/`; ứng dụng đẩy lại mỗi lần khởi động và dịch vụ bỏ qua nếu dữ liệu không đổi.
Tìm bằng giọng nói nhận mọi định dạng (wav, mp3, m4a, ogg…) nhờ ffmpeg đi kèm.

## Điều khiển và quan sát (mọi dịch vụ, header `Authorization: Bearer <khoá>`)
| Đường dẫn | Việc |
|---|---|
| `GET /health` | tình trạng (không cần khoá) |
| `GET /docs` | tài liệu OpenAPI tự sinh |
| `GET /__admin/calls?limit=&path_contains=` | nhật ký các yêu cầu đã nhận |
| `POST /__admin/behavior` | gây lỗi / trễ có chủ đích: `{"fail_next": 2, "status": 503}` hoặc `{"latency_ms": 3000}` (áp dụng cho `/v1/*`) |
| `POST /__admin/reset` | xoá trạng thái (`manage.py reset`) |

## Khác biệt so với dịch vụ thật và hạn chế
- Ba dịch vụ mô phỏng không có xác thực người dùng, webhook, thanh toán bất đồng bộ, 3-D Secure, giới hạn tốc độ… Đây là cố ý.
- Lịch trình vận chuyển tính theo giây (3–5 giây một bước), không theo giờ như hãng thật.
- Whisper hay nghe sai từ mượn tiếng Anh trong câu tiếng Việt (vd. "jeans" → "dinh"); kết quả tìm kiếm vẫn đúng nhờ LLM và CLIP trong các ca đã thử, nhưng không đảm bảo mọi trường hợp.
- `qwen2.5:3b` là mô hình nhỏ: có thể diễn đạt vụng; dịch vụ lọc chữ Hán lạc vào câu trả lời. Muốn tốt hơn dùng `AI_LLM_MODEL=qwen2.5:7b` (GPU 16 GB đủ).
- Mọi dịch vụ chỉ nghe `127.0.0.1`.

## Sự cố thường gặp
- `ai` báo `clip=error: NP_SUPPORTED_MODULES`: `transformers` 5.x chưa tương thích torch 2.11 → dùng `transformers<5` (đã ghim trong `ai_service/requirements-ai.txt`).
- `llm=...:khong-chay`: Ollama chưa chạy hoặc thiếu mô hình → `ollama serve` rồi `ollama pull qwen2.5:3b`.
- Cổng bị chiếm: đặt `EXT_<TÊN>_PORT` (và `ABC_FASHION_<TÊN>_URL` ở ứng dụng).
- Lỗi lạ ở dịch vụ nào: `python manage.py logs <tên>`.
