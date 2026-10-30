"""ShippingGateway — Shipping Provider (GHN / GHTK).

Chế độ `sandbox` (mặc định): giả lập trong tiến trình. Chế độ `http`: gọi dịch vụ vận chuyển mô phỏng
(external_services/shipping, cổng 8102) — mỗi vận đơn tự tiến một trạng thái sau 3–5 giây cho tới khi giao xong.
"""
from __future__ import annotations

from datetime import datetime

from abc_fashion.control.gateway import _http
from abc_fashion.model.fulfilment import ShipmentStatus, Shipment, ShipmentEvent

_NEXT = {
    ShipmentStatus.REQUESTED: (ShipmentStatus.PICKED_UP, "Sandbox: hãng đã lấy hàng"),
    ShipmentStatus.PICKED_UP: (ShipmentStatus.IN_TRANSIT, "Sandbox: đang vận chuyển"),
    ShipmentStatus.IN_TRANSIT: (ShipmentStatus.DELIVERED, "Sandbox: giao thành công"),
}


class ShippingGateway:
    """Dùng bởi: ManageOrderFrm, ProcessReturnFrm, TrackShipmentFrm."""

    def create_shipment(self, shipment: Shipment) -> tuple[str, str]:
        """Đăng ký kiện với hãng. Trả `(carrier, tracking_no)`.

        Frm có thể gắn thêm `shipment.from_location` / `shipment.to_address` (thuộc tính động) để hãng biết điểm đi, đến.
        """
        if _http.use_http():
            _, data = _http.call("shipping", "POST", "/v1/shipments", {
                "client_ref": str(shipment.id), "direction": shipment.direction.value if shipment.direction else "outbound",
                "service_level": shipment.service_level.value if shipment.service_level else "standard",
                "fee": shipment.fee or 0, "from_location": getattr(shipment, "from_location", "") or "",
                "to_address": getattr(shipment, "to_address", "") or ""})
            return data["carrier"], data["tracking_no"]
        return "GHN-SANDBOX", f"GHN{shipment.id:08d}"

    def get_tracking(self, shipment: Shipment) -> list[ShipmentEvent]:
        """Lịch sử theo dõi hiện có của kiện (chưa có `id`, có `shipmentId`)."""
        if _http.use_http():
            if not shipment.tracking_no:
                return []
            status, data = _http.call("shipping", "GET", f"/v1/shipments/{shipment.tracking_no}/events")
            if status != 200:                                  # vận đơn không do hãng này tạo (dữ liệu cũ)
                return []
            return [ShipmentEvent(status=ShipmentStatus(e["status"]), occurred_at=datetime.fromisoformat(e["occurred_at"]),
                                     note=e.get("note"), shipmentId=shipment.id) for e in data["events"]]
        step = _NEXT.get(shipment.status)
        if not shipment.tracking_no or step is None:
            return []
        status, note = step
        return [ShipmentEvent(status=status, occurred_at=datetime.now().replace(microsecond=0), note=note,
                                 shipmentId=shipment.id)]
