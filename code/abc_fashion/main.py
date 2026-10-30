"""Điểm khởi động: mở LoginFrm trên một cửa sổ gốc ẩn (mục 9.1, 13 #11).

Chạy:  cd code && python -m abc_fashion.main
"""
from __future__ import annotations

import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "abc_fashion.log")


EXPIRY_CHECK_MS = 5 * 60 * 1000


def _release_expired_orders(root: tk.Misc) -> None:
    """Mục 9.5: huỷ đơn chờ thanh toán quá hạn để nhả hàng — lúc khởi động và định kỳ khi ứng dụng mở lâu."""
    from abc_fashion.controller.sync_controller import SyncController

    try:
        expired = SyncController().release_expired_orders()
        if expired:
            logging.getLogger("abc_fashion").info("Đã huỷ %d đơn chờ thanh toán quá hạn", expired)
    except Exception:                       # noqa: BLE001 - mất kết nối thoáng qua: lần sau thử lại
        logging.getLogger("abc_fashion").exception("Không huỷ được đơn quá hạn")
    root.after(EXPIRY_CHECK_MS, lambda: _release_expired_orders(root))


def main() -> None:
    logging.basicConfig(level=logging.INFO, filename=LOG_FILE, encoding="utf-8",
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    from abc_fashion.view._util import apply_theme, enable_dpi_awareness

    enable_dpi_awareness()                  # trước khi tạo Tk
    root = tk.Tk()
    apply_theme(root)
    root.withdraw()                         # cửa sổ gốc ẩn, sống suốt chương trình
    try:
        from abc_fashion.view.account.login_frm import LoginFrm

        _release_expired_orders(root)       # nhả hàng đơn quá hạn ngay và cứ 5 phút một lần
        LoginFrm()
        from abc_fashion.control.gateway import _http
        if _http.use_http():                # nối dịch vụ ngoài: đồng bộ vận chuyển nền + đẩy chỉ mục tìm kiếm lên AI
            from abc_fashion.view._sync import ShipmentSync, push_search_index
            ShipmentSync(root).start()
            push_search_index(root)
            logging.getLogger("abc_fashion").info("Chế độ gateway: http (dịch vụ ngoài)")
    except Exception as e:                  # noqa: BLE001 - không kết nối được CSDL
        logging.getLogger("abc_fashion").exception("Không khởi động được")
        messagebox.showerror("Lỗi hệ thống",
                             f"Không kết nối được cơ sở dữ liệu.\n\n{e}\n\n"
                             "Kiểm tra PostgreSQL và biến môi trường ABC_FASHION_DSN.")
        root.destroy()
        sys.exit(1)
    root.mainloop()


if __name__ == "__main__":
    main()
