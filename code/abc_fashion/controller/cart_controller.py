"""CartController — giỏ hàng (UC07) và kiểm tra tồn trước khi thanh toán (UC29)."""
from __future__ import annotations

from abc_fashion.control.dao.cart_dao import CartDAO
from abc_fashion.control.dao.stock_level_dao import StockLevelDAO
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.catalogue import ProductVariant
from abc_fashion.model.sales import Cart, CartItem
from abc_fashion.model.user import Customer


class CartController:
    def __init__(self):
        self.cart_dao = CartDAO()
        self.stock_level_dao = StockLevelDAO()

    def get_cart(self, customer: Customer) -> Cart:
        """Giỏ của khách, gắn `cart.items` và `cart.subtotal`."""
        return self.cart_dao.get_cart_by_customer(customer)

    def add_to_cart(self, customer: Customer | None, variant: ProductVariant | None, quantity: int) -> bool:
        if customer is None:
            raise BusinessError("Vui lòng đăng nhập để mua hàng")
        if variant is None:
            raise BusinessError("Chọn màu và cỡ")
        if quantity is None or quantity <= 0:
            raise BusinessError("Số lượng phải lớn hơn 0")
        cart = self.cart_dao.get_cart_by_customer(customer)
        if not self.cart_dao.add_cart_item(cart, CartItem(productVariantId=variant.id, quantity=quantity)):
            raise BusinessError("Không đủ hàng cho số lượng này (tính cả số đã có trong giỏ)")
        return True

    def update_quantity(self, item: CartItem, quantity: int) -> bool:
        """Đổi số lượng một dòng; 0 = xoá dòng."""
        if quantity is None or quantity < 0:
            raise BusinessError("Số lượng không hợp lệ")
        if quantity == 0:
            return self.cart_dao.delete_cart_item(item)
        item.quantity = quantity
        return self.cart_dao.update_cart_item(item)              # tồn kho được kiểm tra lại khi thanh toán (UC29)

    def remove_item(self, item: CartItem) -> bool:
        return self.cart_dao.delete_cart_item(item)

    def check_availability(self, cart: Cart) -> list[CartItem]:
        """UC29: các dòng không đủ hàng (gắn `available`); giỏ trống → BusinessError."""
        if not getattr(cart, "items", None):
            raise BusinessError("Giỏ hàng trống")
        return self.stock_level_dao.check_availability(cart.items)
