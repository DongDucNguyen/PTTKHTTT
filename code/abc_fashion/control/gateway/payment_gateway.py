"""PaymentGateway — Payment Service (ngân hàng / cổng thanh toán).

Chế độ `sandbox` (mặc định): giả lập trong tiến trình. Chế độ `http`: gọi dịch vụ ngân hàng mô phỏng
(external_services/payment_bank, cổng 8101) — đủ số dư và đủ điều kiện thì thanh toán qua.
"""
from __future__ import annotations

import re
import uuid

from abc_fashion.control.gateway import _http
from abc_fashion.model.customer_data import LinkedMethodType, PaymentMethod
from abc_fashion.model.sales import Order, Payment
from abc_fashion.model.user import Customer

DECLINED_SUFFIX = "0002"          # sandbox: thẻ có số che kết thúc 0002 luôn bị từ chối (thử UC08 E2)


def _last4(method: PaymentMethod | None) -> str | None:
    digits = re.sub(r"\D", "", (method.masked_number if method else "") or "")
    return digits[-4:] if digits else None


class PaymentGateway:
    """Dùng bởi: CheckoutFrm, ConfirmOrderFrm, LinkPaymentMethodFrm, ManageOrderFrm, ProcessReturnFrm."""

    def charge(self, order: Order, method: PaymentMethod) -> tuple[bool, str]:
        """Thu `order.grand_total`. Trả `(thành_công, transaction_ref)`; không ném lỗi khi bị từ chối."""
        if _http.use_http():
            kind = method.method_type.value if method and method.method_type else "bank_transfer"
            _, data = _http.call("payment", "POST", "/v1/charges",
                                 {"order_no": order.order_no, "amount": order.grand_total, "method": kind,
                                  "last4": _last4(method)})
            return data.get("status") == "succeeded", data.get("transaction_ref", "")
        ok = not (method and (method.masked_number or "").endswith(DECLINED_SUFFIX))
        return ok, "SBX-" + uuid.uuid4().hex[:12].upper()

    def refund(self, payment: Payment) -> tuple[bool, str]:
        """Hoàn `payment.amount` cho giao dịch `payment.transaction_ref`."""
        if _http.use_http():
            _, data = _http.call("payment", "POST", "/v1/refunds",
                                 {"transaction_ref": payment.transaction_ref, "amount": payment.amount})
            return data.get("status") == "succeeded", data.get("transaction_ref", "")
        return True, "SBX-R-" + uuid.uuid4().hex[:10].upper()

    def link_method(self, customer: Customer, type: str, provider: str) -> PaymentMethod | None:
        """Ngân hàng mở tài khoản liên kết; chỉ trả số đã che (không bao giờ có số đầy đủ)."""
        if _http.use_http():
            status, data = _http.call("payment", "POST", "/v1/accounts", {"type": type, "provider": provider})
            if status != 200:
                return None
            return PaymentMethod(provider=provider, method_type=LinkedMethodType(type),
                                    masked_number=data["masked_number"], is_default=False, customerId=customer.id)
        return PaymentMethod(provider=provider, method_type=LinkedMethodType(type),
                                masked_number="**** " + f"{uuid.uuid4().int % 10000:04d}", is_default=False,
                                customerId=customer.id)
