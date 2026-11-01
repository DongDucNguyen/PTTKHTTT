# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.user_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.user import tblUser


class UserDAO(DAO):
    """UserDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblUser
    """

    def check_login(self, user: tblUser):
        raise NotImplementedError

    def search_user(self, key: str, user_type: str, status: str):
        raise NotImplementedError

    def update_user_status(self, user: tblUser):
        raise NotImplementedError

    def reset_password(self, user: tblUser):
        raise NotImplementedError

    def is_email_used(self, email: str):
        raise NotImplementedError
