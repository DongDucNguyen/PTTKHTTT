"""ProfileController — hồ sơ khách: thông tin, sổ địa chỉ, phương thức thanh toán, cỡ đã lưu (UC03)."""
from __future__ import annotations

from abc_fashion.control.dao.address_dao import AddressDAO
from abc_fashion.control.dao.category_dao import CategoryDAO
from abc_fashion.control.dao.customer_dao import CustomerDAO
from abc_fashion.control.dao.payment_method_dao import PaymentMethodDAO
from abc_fashion.control.dao.saved_size_dao import SavedSizeDAO
from abc_fashion.control.gateway.payment_gateway import PaymentGateway
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.catalogue import Category
from abc_fashion.model.customer_data import LinkedMethodType, Address, PaymentMethod, SavedSize
from abc_fashion.model.user import PHONE_RE, Customer

PROVIDERS = {LinkedMethodType.CARD: ["Visa", "Mastercard", "JCB"],
             LinkedMethodType.E_WALLET: ["MoMo", "ZaloPay", "VNPay"],
             LinkedMethodType.BANK_ACCOUNT: ["Vietcombank", "Techcombank", "BIDV"]}


class ProfileController:
    def __init__(self):
        self.customer_dao = CustomerDAO()
        self.address_dao = AddressDAO()
        self.payment_method_dao = PaymentMethodDAO()
        self.saved_size_dao = SavedSizeDAO()
        self.category_dao = CategoryDAO()
        self.payment_gateway = PaymentGateway()

    # ---------- thông tin ----------
    def update_profile(self, customer: Customer, full_name: str, phone: str, preferred_colours: list[str],
                       marketing_consent: bool) -> bool:
        full_name, phone = (full_name or "").strip(), (phone or "").strip()
        if not full_name or not PHONE_RE.match(phone):
            raise BusinessError("Nhập họ tên và số điện thoại hợp lệ")
        customer.full_name, customer.phone = full_name, phone
        customer.preferred_colours = [c.strip() for c in preferred_colours if c.strip()]
        customer.marketing_consent = bool(marketing_consent)
        return self.customer_dao.update_customer(customer)

    # ---------- sổ địa chỉ ----------
    def get_addresses(self, customer: Customer) -> list[Address]:
        return self.address_dao.get_address_by_customer(customer)

    def save_address(self, customer: Customer, address: Address) -> bool:
        """Thêm (`address.id` rỗng) hoặc sửa một địa chỉ của khách."""
        a = address
        values = [(v or "").strip() for v in (a.recipient_name, a.phone, a.street, a.ward, a.district, a.city)]
        if not all(values):
            raise BusinessError("Nhập đủ người nhận, điện thoại, đường, phường, quận, thành phố")
        if not PHONE_RE.match(values[1]):
            raise BusinessError("Số điện thoại không hợp lệ")
        a.recipient_name, a.phone, a.street, a.ward, a.district, a.city = values
        a.customerId, a.is_default = customer.id, bool(a.is_default)
        ok = self.address_dao.update_address(a) if a.id else self.address_dao.add_address(a, customer)
        if not ok:
            raise BusinessError("Không lưu được địa chỉ")
        return True

    def delete_address(self, address: Address) -> bool:
        if not self.address_dao.delete_address(address):
            raise BusinessError("Hãy chọn địa chỉ mặc định khác trước khi xoá địa chỉ mặc định")
        return True

    # ---------- phương thức thanh toán ----------
    def get_payment_methods(self, customer: Customer) -> list[PaymentMethod]:
        return self.payment_method_dao.get_payment_method_by_customer(customer)

    def get_providers(self, method_type: LinkedMethodType | None) -> list[str]:
        return list(PROVIDERS.get(method_type, []))

    def link_payment_method(self, customer: Customer, method_type: LinkedMethodType | None, provider: str,
                            is_default: bool) -> PaymentMethod:
        """Khách nhập số thẻ / tài khoản trên trang của cổng thanh toán; hệ thống chỉ lưu số đã che."""
        if method_type is None or not provider:
            raise BusinessError("Chọn loại và nhà cung cấp")
        method = self.payment_gateway.link_method(customer, method_type.value, provider)
        if method is None:
            raise BusinessError("Bạn đã huỷ liên kết")
        method.is_default = bool(is_default)
        if not self.payment_method_dao.add_payment_method(method, customer):
            raise BusinessError("Không lưu được phương thức thanh toán")
        return method

    def remove_payment_method(self, method: PaymentMethod) -> bool:
        if not self.payment_method_dao.delete_payment_method(method):
            raise BusinessError("Phương thức này đã được dùng để thanh toán nên không gỡ được")
        return True

    # ---------- cỡ đã lưu ----------
    def get_categories(self) -> list[Category]:
        return self.category_dao.get_all_category()

    def get_saved_sizes(self, customer: Customer) -> list[SavedSize]:
        return self.saved_size_dao.get_saved_size_by_customer(customer)

    def save_size(self, customer: Customer, category: Category | None, size_label: str) -> bool:
        size_label = (size_label or "").strip()
        if category is None or not size_label:
            raise BusinessError("Chọn danh mục và nhập cỡ")
        return self.saved_size_dao.save_saved_size(SavedSize(size_label=size_label, customerId=customer.id,
                                                             categoryId=category.id), customer)
