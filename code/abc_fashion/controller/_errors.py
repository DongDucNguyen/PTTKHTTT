"""Ngoại lệ mà controller ném cho view (module riêng tư của controller layer, không có trong mô hình VP).

- BusinessError: thao tác không hợp lệ theo nghiệp vụ (thiếu dữ liệu, sai trạng thái…). Thông báo tiếng Việt để
  view hiện thẳng cho người dùng; view desktop (`_util.guarded`) và web đều bắt nó.
- AccessDenied: người dùng không có quyền với đối tượng (NFR03), vd. xem đơn của khách khác.
- ServiceUnavailable: dịch vụ ngoài (ngân hàng, vận chuyển, AI) không phản hồi. Là chính `GatewayUnavailable`
  của gateway, đặt lại tên ở đây để view không phải import control layer.
"""
from __future__ import annotations

from abc_fashion.control.gateway._http import GatewayUnavailable as ServiceUnavailable  # noqa: F401


class BusinessError(Exception):
    """Lỗi nghiệp vụ có thông báo cho người dùng."""


class AccessDenied(BusinessError):
    """Không có quyền với đối tượng này."""
