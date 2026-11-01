# ABC Fashion E-Commerce IS

Hệ thống thông tin bán hàng thời trang ABC Fashion: ứng dụng desktop (Python/tkinter.ttk) và một web app chỉ dành cho khách hàng (Flask), dùng chung một lõi MVC nói chuyện với PostgreSQL 18 (CSDL `abc_fashion_v2`, 39 bảng).

Đặc tả gốc (tiếng Việt), là nguồn chân lý cho mọi class, method, SQL hint, luồng nghiệp vụ và máy trạng thái: [`HUONG_DAN_CODE.md`](HUONG_DAN_CODE.md). Tiến độ triển khai theo từng mục của đặc tả: [`PROGRESS.md`](PROGRESS.md). Hướng dẫn cho Claude Code khi làm việc trong repo này: [`CLAUDE.md`](CLAUDE.md).

## Tình trạng hiện tại

Toàn bộ các hạng mục trong đặc tả đã hoàn thành (xem bảng tóm tắt ở đầu `PROGRESS.md`):

- CSDL: schema 39 bảng + seed + script migrate cho CSDL cũ.
- Model: 41 entity, 34 enum, các quy tắc nghiệp vụ thuần (không phụ thuộc CSDL/UI).
- Control: 34 DAO + 5 gateway sandbox (thanh toán, vận chuyển, thông báo, tìm kiếm, trợ lý AI).
- View: 53 màn hình desktop (`Frm`) + web app khách hàng (Flask).
- `check_gen.py`: 0 vi phạm phân lớp MVC, số lớp/operation khớp mô hình Visual Paradigm.
- `vp2py.py --check`: 0 lệch mô hình ↔ mã.
- Bộ kiểm thử tự động (pytest): quy tắc thuần, DAO, giao diện, đối chiếu mô hình VP, gateway ↔ dịch vụ ngoài (kể cả khi lỗi giữa chừng), dịch vụ AI thật, ghi âm micro.
- Dịch vụ ngoài tách biệt (`external_services/`): ngân hàng/vận chuyển/e-mail mô phỏng + dịch vụ AI thật (CLIP, Whisper, LLM qua Ollama).

Các điểm khác biệt có chủ ý so với mô hình VP và lý do được liệt kê trong `PROGRESS.md` (mục "Sai khác so với mô hình VP").

## Cấu trúc repo

```
code/                   toàn bộ mã nguồn — chạy mọi lệnh từ đây
  abc_fashion/          lõi MVC: model/ control/ (dao, gateway) controller/ view/ main.py
  abc_fashion_web/       web app Flask cho khách hàng (routes, templates, static)
  db/                    schema.sql, seed.sql, setup_db.py, migrate_v2.sql, fetch_product_photos.py
  media/                 ảnh/video sản phẩm, font UI, chỉ mục tìm kiếm
  tests/                 pytest (quy tắc thuần, DAO, view, web, external services, AI)
  check_gen.py           kiểm layer MVC + đối chiếu số lớp/operation
  vp2py.py               sinh khung code từ mô hình Visual Paradigm / đối chiếu mã ↔ mô hình
external_services/       3 dịch vụ mô phỏng (bank, shipping, notify) + 1 dịch vụ AI thật, chạy tách biệt
.venv/                   virtualenv dùng chung (ở gốc repo, không phải trong code/)
```

Các file đặc tả / thiết kế ở gốc repo:

- [`HUONG_DAN_CODE.md`](HUONG_DAN_CODE.md) — đặc tả đầy đủ (class, method, SQL, luồng, state machine).
- [`HUONG_DAN_VE_LAI_VP_MVC.md`](HUONG_DAN_VE_LAI_VP_MVC.md) — hướng dẫn vẽ lại mô hình MVC trong Visual Paradigm.
- [`KE_HOACH_MOCK_SERVERS.md`](KE_HOACH_MOCK_SERVERS.md) — kế hoạch các dịch vụ ngoài mô phỏng.
- [`uiux-design.md`](uiux-design.md) — hệ thống thiết kế giao diện "Midnight Atelier".
- [`PROGRESS.md`](PROGRESS.md) — nhật ký tiến độ, sai khác so với mô hình, checklist trước khi nộp.

## Cài đặt & chạy

```bash
cd code
../.venv/Scripts/python.exe -m pip install -r requirements.txt

# CSDL: tạo abc_fashion_v2, chạy schema + seed, build ảnh + chỉ mục tìm kiếm
../.venv/Scripts/python.exe db/setup_db.py

# Chạy app desktop (chuỗi kết nối lấy từ biến môi trường)
set ABC_FASHION_DSN=dbname=abc_fashion_v2 user=postgres password=... host=localhost port=5432
../.venv/Scripts/python.exe -m abc_fashion.main

# Chạy web app khách hàng — http://127.0.0.1:8000
../.venv/Scripts/python.exe -m abc_fashion_web
```

Dịch vụ ngoài (tuỳ chọn, chế độ http — xem `external_services/README.md`):

```bash
cd external_services
python manage.py setup      # thêm --ai để cài dịch vụ AI thật (cần GPU)
python manage.py start
```

Kiểm thử (các test đụng CSDL sẽ tự bỏ qua nếu không đặt `ABC_FASHION_TEST_DSN`, và **không bao giờ** chạy trên `abc_fashion_v2`):

```bash
cd code
set ABC_FASHION_TEST_DSN=dbname=abc_fashion_test user=postgres password=... host=localhost port=5432
../.venv/Scripts/python.exe -m pytest -q
```

Kiểm layer MVC và đối chiếu mô hình:

```bash
../.venv/Scripts/python.exe check_gen.py .
../.venv/Scripts/python.exe vp2py.py ../vp_export/project.xml --check .
```

Chi tiết đầy đủ các lệnh, biến môi trường, tài khoản đăng nhập mẫu, và các điều cần lưu ý khi làm việc với CSDL thật `abc_fashion_v2` so với CSDL test: xem [`CLAUDE.md`](CLAUDE.md).

## Kiến trúc

MVC ba lớp (`view` → `controller` → `control` [dao, gateway] → `model`), được `check_gen.py` kiểm bằng cách phân tích `import` qua `ast` — view không bao giờ import trực tiếp DAO/gateway/psycopg. Hai giao diện (desktop tkinter và web Flask) dùng chung một bộ `controller`. Chi tiết đầy đủ về từng lớp, quy ước đặt tên, cơ chế transaction/stock/gateway: xem mục "Architecture (§2)" trong [`CLAUDE.md`](CLAUDE.md).
