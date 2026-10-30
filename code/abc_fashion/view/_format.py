"""Định dạng hiển thị dùng chung cho mọi view (desktop tkinter và web) — không phụ thuộc tkinter.

Module riêng tư của view layer, không có trong mô hình VP. `_util` dùng lại các hàm này cho các Frm; ứng dụng web
(`abc_fashion_web`) dùng làm bộ lọc Jinja.
"""
from __future__ import annotations

import enum
from datetime import date, datetime


def money(x: int | None) -> str:
    return f"{x or 0:,}".replace(",", ".") + " đ"


def fmt_dt(v) -> str:
    if v is None:
        return ""
    if isinstance(v, datetime):
        return v.strftime("%d/%m/%Y %H:%M")
    if isinstance(v, date):
        return v.strftime("%d/%m/%Y")
    return str(v)


_LABELS = {
    "OrderStatus": {"pending_payment": "Chờ thanh toán", "confirmed": "Đã xác nhận", "processing": "Đang xử lý",
                    "partially_shipped": "Giao một phần", "shipped": "Đang giao", "delivered": "Đã giao",
                    "completed": "Hoàn tất", "cancelled": "Đã huỷ"},
    "ReturnStatus": {"requested": "Đã gửi yêu cầu", "authorised": "Đã duyệt", "rejected": "Từ chối",
                     "in_transit": "Đang gửi về", "inspected": "Đã kiểm tra", "refunded": "Đã hoàn tiền",
                     "exchanged": "Đã đổi hàng", "closed": "Đã đóng"},
    "RestockStatus": {"draft": "Nháp", "sent": "Đã gửi", "confirmed": "NCC xác nhận", "received": "Đã nhận",
                      "cancelled": "Đã huỷ"},
    "ShipmentStatus": {"requested": "Chờ lấy hàng", "picked_up": "Đã lấy hàng", "in_transit": "Đang vận chuyển",
                       "delivered": "Đã giao", "failed": "Thất bại"},
    "PaymentStatus": {"pending": "Chờ", "succeeded": "Thành công", "failed": "Thất bại"},
    "PaymentKind": {"charge": "Thu", "refund": "Hoàn"},
    "PaymentMethodType": {"cod": "Thanh toán khi nhận (COD)", "card": "Thẻ", "e_wallet": "Ví điện tử",
                          "bank_transfer": "Chuyển khoản"},
    "LinkedMethodType": {"card": "Thẻ", "e_wallet": "Ví điện tử", "bank_account": "Tài khoản ngân hàng"},
    "DeliveryService": {"standard": "Tiêu chuẩn", "express": "Hoả tốc"},
    "ReviewStatus": {"pending": "Chờ duyệt", "approved": "Đã duyệt", "rejected": "Từ chối"},
    "StyleStatus": {"draft": "Nháp", "active": "Đang bán", "inactive": "Ngừng bán"},
    "VariantStatus": {"active": "Đang bán", "discontinued": "Ngừng"},
    "PromotionStatus": {"draft": "Nháp", "active": "Đang chạy", "ended": "Đã kết thúc"},
    "AccountStatus": {"active": "Hoạt động", "suspended": "Bị khoá"},
    "InspectionResult": {"pending": "Chưa kiểm", "passed": "Đạt", "failed": "Không đạt"},
    "ReturnType": {"return": "Trả hàng", "exchange": "Đổi hàng"},
    "Resolution": {"refund": "Hoàn tiền", "exchange": "Đổi hàng"},
    "ReturnReason": {"too_small": "Quá chật", "too_large": "Quá rộng", "defect": "Lỗi sản phẩm",
                     "wrong_item": "Giao sai hàng", "not_as_described": "Không như mô tả",
                     "changed_mind": "Đổi ý"},
    "FitVote": {"runs_small": "Hơi chật", "true_to_size": "Đúng cỡ", "runs_large": "Hơi rộng"},
    "MovementReason": {"sale": "Bán", "return": "Trả về", "restock": "Nhập hàng", "adjustment": "Điều chỉnh"},
    "StaffRole": {"administrator": "Quản trị viên", "manager": "Quản lý", "merchandiser": "Merchandiser",
                  "marketing": "Marketing", "customer_service": "Chăm sóc khách hàng", "warehouse": "Kho",
                  "sales": "Bán hàng"},
    "ShipmentDirection": {"outbound": "Giao đi", "return": "Lấy về"},
    "PromoType": {"seasonal": "Theo mùa", "flash_sale": "Flash sale", "clearance": "Thanh lý", "loyalty": "Khách thân thiết"},
    "FitType": {"slim": "Ôm (slim)", "regular": "Vừa (regular)", "relaxed": "Rộng rãi (relaxed)", "oversized": "Oversize"},
    "Measure": {"chest": "Ngực", "waist": "Eo", "hip": "Mông", "length": "Dài", "sleeve": "Tay áo", "inseam": "Dài trong ống",
                "foot_length": "Dài bàn chân"},
}


def label(member) -> str:
    """Nhãn tiếng Việt của một giá trị enum (hoặc chuỗi rỗng)."""
    if member is None:
        return ""
    if isinstance(member, enum.Enum):
        return _LABELS.get(type(member).__name__, {}).get(member.value, member.value)
    return str(member)


def enum_choices(enum_cls, all_label: str | None = None) -> list[tuple[str, object]]:
    out = [(all_label, None)] if all_label else []
    return out + [(label(m), m) for m in enum_cls]


def to_int(text, default=None):
    try:
        return int(str(text).replace(".", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return default


def to_float(text, default=None):
    try:
        return float(str(text).replace(",", ".").strip())
    except (TypeError, ValueError):
        return default


def ship_text(order) -> str:
    """Người nhận – điện thoại – địa chỉ của đơn; đơn cũ chưa chụp địa chỉ (mục 13 #4) thì báo rõ."""
    parts = [p for p in (order.ship_recipient, order.ship_phone, order.ship_address) if p]
    return " – ".join(parts) if parts else "(đơn cũ — chưa lưu địa chỉ giao hàng)"
