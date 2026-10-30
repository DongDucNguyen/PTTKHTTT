"""AuthController — đăng nhập (UC02), đăng ký khách (UC01). Dùng chung cho desktop và web."""
from __future__ import annotations

from abc_fashion.control.dao.customer_dao import CustomerDAO
from abc_fashion.control.dao.staff_member_dao import StaffMemberDAO
from abc_fashion.control.dao.supplier_dao import SupplierDAO
from abc_fashion.control.dao.user_dao import UserDAO
from abc_fashion.controller._errors import BusinessError
from abc_fashion.model.user import EMAIL_RE, PHONE_RE, password_problem, Customer, StaffMember, Supplier, User


class AuthController:
    def __init__(self):
        self.user_dao = UserDAO()
        self.customer_dao = CustomerDAO()
        self.staff_member_dao = StaffMemberDAO()
        self.supplier_dao = SupplierDAO()

    def login(self, email: str, password: str) -> Customer | Supplier | StaffMember:
        """Trả tác nhân của tài khoản (khách / nhà cung cấp / nhân viên); sai thông tin → BusinessError."""
        user = User(email=(email or "").strip(), password=password or "")
        if not user.email or not user.password:
            raise BusinessError("Nhập e-mail và mật khẩu")
        if not self.user_dao.check_login(user):
            raise BusinessError("Sai e-mail hoặc mật khẩu, hoặc tài khoản bị khoá")
        actor = (self.customer_dao.get_customer_by_user(user) or self.supplier_dao.get_supplier_by_user(user)
                 or self.staff_member_dao.get_staff_member_by_user(user))
        if actor is None:
            raise BusinessError("Tài khoản chưa được gán vai trò")
        return actor

    def register(self, customer: Customer, confirm_password: str) -> bool:
        """UC01: kiểm tra dữ liệu (E1 e-mail trùng, E2 mật khẩu không khớp) rồi tạo tài khoản khách."""
        c = customer
        c.full_name, c.email, c.phone = (c.full_name or "").strip(), (c.email or "").strip(), (c.phone or "").strip()
        if not all((c.full_name, c.email, c.phone, c.password, confirm_password)):
            raise BusinessError("Nhập đủ các trường")
        if not EMAIL_RE.match(c.email):
            raise BusinessError("E-mail không đúng dạng")
        if not PHONE_RE.match(c.phone):
            raise BusinessError("Số điện thoại gồm 10–11 chữ số, bắt đầu bằng 0")
        if (problem := password_problem(c.password)):
            raise BusinessError(problem)
        if c.password != confirm_password:
            raise BusinessError("Hai mật khẩu không trùng nhau")
        if self.user_dao.is_email_used(c.email) or not self.customer_dao.add_customer(c):
            raise BusinessError("E-mail đã được dùng")
        return True
