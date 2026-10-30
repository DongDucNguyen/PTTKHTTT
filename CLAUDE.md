# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

ABC Fashion E-Commerce IS — a Python desktop app (tkinter.ttk) plus a customer-only web app (Flask, `abc_fashion_web/`), both on top of one MVC core talking to PostgreSQL 18 (DB `abc_fashion_v2`, 39 tables). `HUONG_DAN_CODE.md` (Vietnamese) is the authoritative spec: every class, method signature, SQL hint, flow and state machine comes from it. Section numbers below (§x.y) refer to that file. Progress is tracked in `PROGRESS.md`.

All code lives in `code/`; run every command from there. The venv is at the repo root (`.venv`).

## Commands

```bash
cd code
../.venv/Scripts/python.exe -m pip install -r requirements.txt   # psycopg[binary], tkcalendar, pillow, bcrypt, flask, pytest

# DB: create abc_fashion_v2 (from ABC_FASHION_DSN), run db/schema.sql + db/seed.sql, build media + search index
../.venv/Scripts/python.exe db/setup_db.py            # refuses to touch a DB that already has tables
../.venv/Scripts/python.exe db/setup_db.py --reset    # DROP + recreate (destroys data)
../.venv/Scripts/python.exe db/setup_db.py --index    # only regenerate media placeholders + media/search_index.json
../.venv/Scripts/python.exe db/fetch_product_photos.py   # download Unsplash product photos to media/products/, repoint ProductMedia (credits: MEDIA_CREDITS.md)
psql -d abc_fashion_v2 -f db/migrate_v2.sql           # for a DB created earlier from the report (idempotent)

# Run the app (connection string from env; default has no password)
set ABC_FASHION_DSN=dbname=abc_fashion_v2 user=postgres password=... host=localhost port=5432
../.venv/Scripts/python.exe -m abc_fashion.main
# Customer web app (same DSN; http://127.0.0.1:8000, ABC_FASHION_WEB_PORT / _HOST / _SECRET optional)
../.venv/Scripts/python.exe -m abc_fashion_web

# Structure / MVC layer check (§12.2): must print "imported modules: 119 / layer violations: 0" and exit 0
../.venv/Scripts/python.exe check_gen.py .

# VP model (vp_export/project.xml; NOT present on this machine since the model was redrawn elsewhere — copy it back before using vp2py;
# tests/test_structure.py skips the two VP tests while it is missing).
# project.xml already contains Order.ship_* and ReturnItem.replacementVariantId, added by db/vp_add_attributes.py
# (original: project.before_attrs.xml; VP-importable copy: project_import.xml). A fresh VP export that lacks them will fail --check on purpose.
../.venv/Scripts/python.exe vp2py.py ../vp_export/project.xml --check .     # code vs model: must report "lệch mô hình: 0"
../.venv/Scripts/python.exe vp2py.py ../vp_export/project.xml <tmp_dir>     # regenerate skeleton (overwrites; never into code/)

# Tests. DB tests (test_dao.py, test_views.py, test_web.py) skip unless ABC_FASHION_TEST_DSN points at a throwaway DB
# (never abc_fashion_v2 — the fixture drops and recreates the public schema before every test).
set ABC_FASHION_TEST_DSN=dbname=abc_fashion_test user=postgres password=... host=localhost port=5432
../.venv/Scripts/python.exe -m pytest -q
../.venv/Scripts/python.exe -m pytest -q tests/test_dao.py::test_two_buyers_last_item_only_one_wins
```

The live `abc_fashion_v2` on this machine holds the report's sample data (already migrated; passwords reset to `abc12345`; backup in `backups/`): logins `admin@abcfashion.vn`, `manager@abcfashion.vn`, `warehouse@abcfashion.vn`, `cs@abcfashion.vn`, customers `alex@email.com` etc., suppliers `sales@vietthread.vn`. Its schema differs slightly from `db/schema.sql` (no UNIQUE on `ShipmentEvent`, extra UNIQUE(`styleId`,`material`), looser NOT NULLs) — DAO code must work against both, so don't rely on `ON CONFLICT` targets that only exist in `schema.sql`. Never point tests at it. Product photos there are local files under `media/products/` (not the dead CDN URLs); the video row stays a dead URL, so views must filter `media_type` before drawing.

Project seed logins (`db/seed.sql`, used for `abc_fashion_test`; password `abc12345`, stored plaintext, re-hashed on first login; bcrypt hashes are also accepted): `admin@abc.vn`, `manager@abc.vn`, `merch@abc.vn`, `marketing@abc.vn`, `cs@abc.vn`, `warehouse@abc.vn`, `sales@abc.vn`, suppliers `supplier@vaidep.vn` / `supplier@denimviet.vn`, customers `an.nguyen@gmail.com` / `binh.tran@gmail.com` (`khoa.le@gmail.com` is suspended). Sandbox card `**** 0002` always declines.

## External services (`external_services/`, sibling of `code/`)

Strictly separate from the app (no cross-imports, HTTP only). Three **simulated** services (bank 8101, shipping 8102, e-mail/SMS 8103; FastAPI + SQLite) and one **real** AI service (8104: CLIP + Whisper on GPU, LLM via Ollama `qwen2.5:3b`), run as background processes by `external_services/manage.py` (`setup [--ai]`, `start`, `stop`, `status`, `logs`, `reset`). Full docs: `external_services/README.md`. The AI service has its own venv (`ai_service/.venv`, torch cu128, `transformers<5`).

- Gateways run in `sandbox` mode by default (in-process, what the older tests use). `ABC_FASHION_GATEWAY_MODE=http` switches all five to the services via `control/gateway/_http.py` (functions only — `check_gen.py` skips `_*` modules when counting gateways; the only class there is `GatewayUnavailable`). Per-service `ABC_FASHION_<PAYMENT|SHIPPING|NOTIFY|AI>_URL/_KEY`.
- Gateway failure policy: payment/shipping raise `GatewayUnavailable`; notify returns `False`; search raises (view suggests text search); assistant falls back to basic/rule mode.
- `Notification` has no address, so `controller/_flows.notify` attaches `notification.recipient` (dynamic attribute) from `NotificationDAO._get_recipient`.
- In http mode `main.py` starts `view/_sync.ShipmentSync` (Tk scheduling only; logic in `SyncController`: polls open shipments every 3 s, writes events, advances order status via `ORDER_NEXT` steps, notifies on delivery) and pushes the catalogue to the AI service. The web app does the same in a daemon thread (`abc_fashion_web/_background.py`). The shipping simulator advances one status every 3–5 s and returns a *stable* event history (ShipmentDAO dedups on `(shipment, status, occurred_at)`).
- Threading: never call Tk or DAOs from a worker thread. Use `_util.run_in_thread(win, work, done)` (queue polled by `after`) and only pass it controller methods documented "an toàn ở luồng phụ" (gateway-only: `find_style_ids_by_*`, `ask_assistant`, `fetch_tracking`); use `_util.watch(win, signature, reload)` for screens that must refresh when background data changes.
- Tests: `tests/test_external.py` (bank/shipping/notify contracts + background sync), `tests/test_http_flows.py` (UI flows in http mode incl. the demo scenario, and failure injection via `/__admin/behavior` — resets the simulators before each test) and `tests/test_ai_service.py` (real models) auto-start the services via `manage.py` and skip if they cannot run. Don't run the app or tests with `ABC_FASHION_GATEWAY_MODE=http` against `abc_fashion_v2` unless you accept it mutating sample data (startup cancels stale `pending_payment` orders).

## Architecture (§2) — MVC

Layers under `code/abc_fashion/`, enforced by `check_gen.py` via `ast` on import statements: `view` → `controller` → `control` (dao, gateway) → `model`. Views (desktop Frms and the web app) may import only `controller` + `model` — never DAOs, gateways or psycopg. MVC mapping: Model = `model` + `control.dao` + `control.gateway`; View = `view/` (tkinter) and `abc_fashion_web/` (Flask templates); Controller = `controller/`. What must be redrawn in Visual Paradigm for this is in `HUONG_DAN_VE_LAI_VP_MVC.md` (repo root).

- `model/` — one file per package: enums (values = DB CHECK values, stored via `.value`) then `@dataclass(kw_only=True)` entities named after tables **without** the `tbl` prefix (class `Order` ↔ DB table `"tblOrder"`; the prefix was dropped from class names / VP model / docs, the physical table names keep it); every field defaults to `None`. Pure business rules also live here so they are testable without DB/UI: `ORDER_NEXT`, `recalc_order`, `apply_discount`, `voucher_error`, `net_paid` (sales.py); `RETURN_NEXT`, `refund_amount`, `within_return_window` (returns.py); `RESTOCK_NEXT` (inventory.py); `order_status_from_shipments` (fulfilment.py). Imports only stdlib + `model`.
- `control/dao/` — one DAO per table; the only place with SQL / `psycopg`. `control/gateway/` — 5 sandbox gateways for external systems (payment, shipping, email, search, AI); may not touch the DB, so callers attach real data to entities first (e.g. `CatalogueController.get_style_detail` sets `style.variants/materials/size_chart/reviews/promotion` before `AssistantEngine`).
- `controller/` — 15 `XxxController` classes (one per use-case group: Auth, Profile, AccountAdmin, Catalogue, Cart, Checkout, Order, Review, Return, OrderAdmin, Product, Promotion, Report, Inventory, Sync), one per file. They own the DAOs/gateways (`self.order_dao = OrderDAO()`), validate input, run multi-DAO transactions, call gateways outside transactions, notify. No tkinter/Flask. Business failures raise `BusinessError(message)` (Vietnamese, shown to the user); `AccessDenied` for NFR03 ownership checks; `ServiceUnavailable` is `GatewayUnavailable` re-exported. Results the views need for enabling buttons are attached as dynamic attributes (`order.can_cancel`, `item.can_review`, `request.can_refund`, `order.next_statuses`…). Private modules: `_errors`, `_flows` (pay_order, refund_order, cancel_with_refund, notify, push_search_index), `_media` (media_path, save_media), `_connection` (per-thread DB switch for the web).
- `view/` — 53 `XxxFrm(tk.Toplevel)` screens, one per file; no SQL, no DAO/gateway imports. Each Frm holds its controller(s) (`self.checkout_controller = CheckoutController()`). `view/_format.py` (no tkinter; shared with the web): `money`, `fmt_dt`, `label`, `ship_text`, `to_int`. `view/_util.py` is a private helper module (not in the VP model, excluded from the 119 count): `ChoiceBox`, `make_table`/`fill_table` (auto-fits column widths and right-aligns numeric columns — don't hardcode alignment or add suffixes to headings for it)/`selected`, `apply_theme`/`enable_dpi_awareness` (called from `main.py` before/after `tk.Tk()`), `guarded` (BusinessError → `lbl_message` or warning box; AccessDenied → error box + close; anything else → "Lỗi hệ thống" box), `logout`, `modal`, `read_file`, `DateEntry` (tkcalendar).
- `abc_fashion_web/` (sibling of `abc_fashion/`) — customer-only Flask app: `routes.py` (thin: request → controller → template; one controller instance per request), `templates/` (Jinja, filters `money/label/dt/ship_text`), `static/style.css` (same palette/font as the desktop), CSRF token on every POST, `BusinessError` → flash + redirect back via `app.errorhandler`. It calls `_connection.use_connection_per_thread()` so each request thread gets its own DB connection (`DAO._per_thread`), closed in `teardown_request`. Staff/supplier logins are refused. Not part of the VP class model.

Key cross-cutting mechanics:

- **One shared connection** (`DAO._shared`, autocommit, `dict_row`; per thread when `DAO._per_thread`, i.e. the web). Atomic groups use `with self.con.transaction():`; nesting becomes savepoints, so a controller can wrap several DAOs in one transaction (`with self.some_dao.con.transaction():`). Views have no transaction knowledge. To roll back from a controller, raise inside the block (controllers define a local `_Rollback`, then re-raise as `BusinessError`); inside DAOs raise `_Abort`. A `return False` inside a `with transaction()` *commits* the savepoint, so only return early before writing.
- DAO methods that catch `BUSINESS_ERRORS` (Unique/FK/Check/NotNull) must wrap their statements in their own `with self.con.transaction()` so the failure doesn't poison an outer transaction.
- `_to_entity(cls, row)` converts strings to enums by type hint and attaches non-field columns (JOIN extras like `style_name`, `sku`, `location_name`) as dynamic attributes. Child lists are also dynamic attributes by convention: `order.items/payments/shipments/vouchers`, `cart.items`, `request.items/evidence/shipments`, `promotion.styles/vouchers`, `turn.grounding_events`, `shipment.records`.
- Inheritance trap (§6.2): subclass dataclasses redeclare `id`, so `Customer.id` is the customer row (account id is `userId`), `OrderItem.id` is the order line (variant is `productVariantId`). Don't select a JOINed column named `status` into `CartItem`/`OrderItem`/`ReturnItem` unless it really is the variant status — it is converted to `VariantStatus`.
- Always quote identifiers (`"tblOrder"`, `"customerId"`), use `%s` params, and cast nullable params (`%s::int IS NULL`, `%s::text`) — psycopg 3 can't infer types for bare NULLs. Use `localtimestamp`, not `now()`, when a server time is brought back into Python (columns are `timestamp without time zone`).
- Stock: `available = on_hand − reserved` is a CHECK, so every UPDATE changes both. Every stock change writes a `StockMovement` row; tests assert Σ `quantity_change` = `on_hand`. Lock stock rows `ORDER BY "productVariantId" FOR UPDATE`. Order lifecycle: `add_order` reserves → `pending_payment→confirmed` deducts `on_hand` + `sale` movement → `cancel_order` reverses whichever applied.
- Never call a gateway inside a DB transaction (§11 rule 2): commit, call gateway, then write the result. Because of that, a gateway failure leaves the committed part behind, so a retry must resume it rather than redo it (CheckoutFrm / web checkout open the order-result page on `ServiceUnavailable`; `ReturnController` reuses shipments without a tracking number; `_flows.refund_order` records a failed refund).
- All writes of state go through "old state" checks (`UPDATE … WHERE "status" = old`) and the `*_NEXT` tables.

## Conventions (§5)

- `vp2py.py --check` is the source of truth for signature conformance: any new public method on a Frm/controller/DAO/gateway, renamed parameter, missing Frm attribute, or missing `self.<x>_controller = XController()` (Frm) / `self.<x>_dao = XDAO()` (controller) for a modelled association fails it (and `tests/test_structure.py`). `check_gen.py` expects 53 Frm / 15 controller / 34 DAO / 5 gateway / 41 entity / 34 enum / 459 operations (public methods incl. staticmethods; constructors only for Frm and the `DAO` base). A new public controller method therefore changes the expected count and must be added to the VP model (and `HUONG_DAN_VE_LAI_VP_MVC.md`). Intentional deviations go in `KNOWN_DEVIATIONS` in `vp2py.py` and in `PROGRESS.md`.
- Don't change generated names/signatures (class, method, parameter names/order). Allowed: return types, private `_helpers`, extra imports that respect layers.
- Validation and business messages belong in controllers (raise `BusinessError`), not in Frms or routes; Frms only parse widget input (e.g. `int(spinbox)`) and show results.
- Widget attribute prefixes: `txt_` Entry, `txa_` Text, `btn_`, `lbl_`, `cbo_`, `chk_`, `rdo_`, `spn_`, `tbl_`/`tree_` Treeview, `dte_` DateEntry, `cnv_` Canvas; `list_x` holds the rows shown in a table; Treeview `iid = str(entity.id)`. DAO attributes are snake_case of the class (`self.order_dao`). Handlers are `on_<action>` and decorated with `@guarded`.
- DAO returns: `add_/update_/delete_/cancel_/save_/…` → `bool` and fill the new `id`; `get_x_by_y` → entity or `None`; lists → `list`. Expected business failures return `False`; connection/programming errors propagate.
- Voice search records the microphone itself: `_util.record_wav` (sounddevice RawInputStream, WAV bytes; raises RuntimeError → the screen falls back to a file dialog). Tests stub `search_style_frm.record_wav`; never record in tests.
- `ProductController` pushes the AI search index after every product / variant / media change (http mode only). Expired `pending_payment` orders are released at startup and every 5 min (`main._release_expired_orders` → `SyncController.release_expired_orders`).
- Money is `int` VND; display with `_format.money()` (re-exported by `_util`; `|money` in templates). UI text is Vietnamese.
- Tests that need the search screen without a DB monkeypatch `search_style_frm.CatalogueController` (see `tests/test_voice.py`).
- Look & feel follows `uiux-design.md` ("Midnight Atelier": dark navy/blue, Be Vietnam Pro from `media/ui/fonts`). Colours, fonts and ttk styles live only in `view/_theme.py` (art drawn by `view/_art.py`); Frms use style names (`H2.TLabel`, `Muted.TLabel`, `Primary.TButton`, `Tile.TButton`…) or `_util.ERROR_FG/OK_FG`, never hex colours or `font=("Segoe UI", …)`. Buttons without a style are classified by their text in `_theme.polish` (run via `after_idle` from `body`); the last button of `button_row` becomes primary.
- Design deviations from the VP model are documented in `PROGRESS.md` (e.g. `Order.ship_*`, `ReturnItem.replacementVariantId`, `SALES` role → `MarketingHomeFrm`, `PromotionDAO` in `CheckoutFrm`). Keep that list current when adding more.
