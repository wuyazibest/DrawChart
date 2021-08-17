#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : test_model.py
# @Time    : 2020/9/12 21:44
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import enum
from datetime import datetime

from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

from main.setting import db
from main.util import DataDict, RichBaseModel, StrChoiceType


class UserModel(RichBaseModel):
    __bind_key__ = "management"
    __tablename__ = "user"
    __table_args__ = {"comment": "用户管理"}
    
    ROLE_CHOICE = {
        "user": "general user",
        "admin": "administrator",
        }

    @enum.unique
    class RoleChoice(enum.Enum):
        """
        name 为存储值
        value 为展示值
        """
        admin = "管理员"
        user = "普通用户"
    
        @classmethod
        def choice(cls):
            return [i.name for i in cls]
    
    username = db.Column(db.String(191), unique=True, index=True, nullable=False, doc="用户名")
    nickname = db.Column(db.String(191), nullable=False, default="", doc="用户名")
    password_hash = db.Column(db.String(191), nullable=False, doc="哈希密码")
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, doc="最后登录时间")
    is_superuser = db.Column(db.Boolean, nullable=False, default=False, doc="超级管理员")
    role = db.Column(db.String(191), default=RoleChoice.user.name, nullable=False, doc="角色")
    # role = db.Column(StrChoiceType(ROLE_CHOICE), default=ROLE_CHOICE["user"], nullable=False, doc="角色")
    is_active = db.Column(db.Boolean, nullable=False, default=True, doc="活跃标记")
    
    def get_password(self):
        raise NotImplementedError()
    
    def set_password(self, value):
        self.password_hash = generate_password_hash(value)
    
    password = property(get_password, set_password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @validates("role")
    def validate_role(self, key, value):
        assert value in self.RoleChoice.choice(), "role 错误!"
        return value
    
    def to_dict(self):
        return DataDict({
            "id": self.id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            "user": self.user,
            "username": self.username,
            "nickname": self.nickname,
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S"),
            "is_superuser": bool(self.is_superuser),
            "role": self.role,
            "is_used": bool(self.is_used),
            "is_active": bool(self.is_active),
            "comment": self.comment,
            "role_label": getattr(self.RoleChoice, self.role).value,
            })


def legal_request_method(method):
    http_method_funcs = frozenset(
        ["GET", "POST", "HEAD", "OPTIONS", "DELETE", "PUT", "TRACE", "PATCH"]
        )
    return method in http_method_funcs


class UriModel(RichBaseModel):
    __bind_key__ = "management"
    __tablename__ = "open_api_uri"
    __table_args__ = (
        db.UniqueConstraint("request_method", "uri", name="uniq_open_api_uri_request_method_uri"),
        {"comment": "接口开放平台uri"}
        )
    
    request_method = db.Column(db.String(191), nullable=False, default="GET", doc="request_method")
    uri = db.Column(db.String(191), nullable=False, doc="uri")
    
    # app_name = db.Column(db.String(191), nullable=False, default="", doc="app_name")
    # app_id = db.Column(db.Integer, nullable=False, doc="app_id")
    
    @validates("request_method")
    def validate_request_method(self, key, value):
        assert legal_request_method(value), "request_method 错误!"
        return value


class UserUriModel(RichBaseModel):
    __bind_key__ = "management"
    __tablename__ = "open_api_user_uri"
    __table_args__ = (
        db.UniqueConstraint("username", "request_method", "uri", name="uniq_open_api_username_uri_request_method_uri"),
        {"comment": "接口开放平台用户的uri"}
        )
    
    username = db.Column(db.String(191), nullable=False, doc="用户名")
    request_method = db.Column(db.String(191), nullable=False, default="GET", doc="request_method")
    uri = db.Column(db.String(191), nullable=False, doc="uri")
    
    @validates("request_method")
    def validate_request_method(self, key, value):
        assert legal_request_method(value), "request_method 错误!"
        return value
