#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : model.py
# @Time   : 2020/11/25 14:15
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import datetime
from email.policy import default

from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

from main.setting import db
from main.util.common import generate_md5
from main.core import ValidateModel

"""
只管理用户信息，不涉及权限相关
一个用户实体是一个客户
一个用户可以同时持有多个账户
账户认证后创建或关联到客户
权限基于账户

客户--用户
组织--用户
用户--角色--权限
"""


class UserModel(ValidateModel):
    # __bind_key__ = "management"  # 指定数据库
    __tablename__ = "sys_user"
    __table_args__ = {"comment": "用户表"}
    
    ROLE_CHOICE = {
        1: "管理员",
        2: "普通用户",
        }
    
    username = db.Column(db.String(191), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = db.Column(db.String(191), nullable=False, comment="哈希密码")
    nickname = db.Column(db.String(191), nullable=False, default="", comment="别名")
    mobile = db.Column(db.String(191), nullable=False, default="", comment="手机号")
    customer_id = db.Column(db.Integer, nullable=True, comment="客户id，认证后的用户才有")
    role = db.Column(db.Integer, nullable=False, default=2, comment="系统角色")
    last_login = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="最后登录时间")
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment="活跃标记")
    
    validates_choice = {
        "role"
        }
    
    @validates(*validates_choice)
    def validate_choice(self, key, value):
        return super().validate_choice(key, value)
    
    def get_password(self):
        return None
    
    def set_password(self, value):
        self.password_hash = generate_password_hash(value)
    
    password = property(get_password, set_password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        ret = super().to_dict()
        
        ret["customer_id_info"] = CustomerModel.get_columns_dict()
        if self.customer_id:
            ret["customer_id_info"] = CustomerModel.query.filter_by(id=self.customer_id).first().to_dict()
        
        del ret["password_hash"]
        return ret
    
    @staticmethod
    def is_admin(role):
        return role == 1


class CustomerModel(ValidateModel):
    __tablename__ = "sys_customer"
    __table_args__ = {"comment": "客户表"}
    
    TYP_CHOICE = {
        1: "内部客户",
        2: "外部客户",
        }
    
    name = db.Column(db.String(191), nullable=False, comment="客户真实姓名")
    sn = db.Column(db.String(191), unique=True, nullable=False, comment="身份证号")
    typ = db.Column(db.Integer, nullable=False, default=1, comment="客户类型")
    
    validates_choice = {
        "typ"
        }
    
    @validates(*validates_choice)
    def validate_choice(self, key, value):
        return super().validate_choice(key, value)
    
    def to_dict(self):
        ret = super().to_dict()
        for i in self.validates_choice:
            ret[f"{i}_label"] = getattr(self, f"{i}_choice".upper()).get(getattr(self, i))
        
        return ret
