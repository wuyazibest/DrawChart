#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : view.py
# @Time   : 2020/11/25 14:15
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import logging

from flask import request, g
from sqlalchemy import cast, text

from .model import *
from main.core import (
    ModelViewSet,
    permission_classes,
    IsLoginPermission,
    IsAdminPermission,
    RequestFromPermission,
    RET,
    ParamError,
    DataError,
    AuthenticationFailed,
    jwt_encode_handler,
    json_resp,
    )
from main.util.common import make_cache_key
from main.setting import cache
from main.config import RequestFrom

logger = logging.getLogger(__name__)


class LoginView(ModelViewSet):
    decorators = []
    resources = "登录模块"
    model = UserModel
    
    query_field = (
        "username",
        "password",
        )
    
    @property
    def queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    def login(self):
        """
        """
        logger.info(f"{self.resources}登录 user:{request.headers.get('host')} params:{self.request_data}")
        
        username = self.request_data.get("username")
        password = self.request_data.get("password")
        if not all([username, password]):
            raise ParamError(f"用户名密码不能为空", code=RET.RequiredERR)
        
        instance = self.queryset.filter_by(username=username).first()
        if not instance:
            raise AuthenticationFailed(f"用户[{username}]不存在", code=RET.UserNotExite)
        if not instance.check_password(password):
            raise AuthenticationFailed(f"用户名密码错误", code=RET.PWDERR)
        
        instance.last_login = datetime.datetime.now()
        user = instance.update()
        
        data = {
            "token": jwt_encode_handler(instance),
            "user" : user,
            }
        return json_resp(RET.OK, f"{self.resources}登录成功", data=data)


class UserView(ModelViewSet):
    resources = "用户"
    model = UserModel
    query_field = (
        "id",
        "username",
        "nickname",
        "remark",
        )
    create_field = (
        "username",
        "nickname",
        "password",
        "remark",
        )
    create_required_field = (
        "username",
        "password",
        )
    update_field = (
        "id",
        "nickname",
        "password",
        "is_active",
        "remark",
        )
    
    def perform_query(self, queryset, params):
        self.like_field = ["username", "nickname"]
        return super().perform_query(queryset, params)
    
    @cache.cached(make_cache_key=make_cache_key)
    def post_query(self):
        return super().post_query()
    
    @permission_classes([IsAdminPermission])
    def create(self):
        return super().create()
    
    @permission_classes([IsAdminPermission, RequestFromPermission(RequestFrom.web.key)])
    def delete(self):
        """必须为管理员，且通过页面请求才能访问
        """
        return super().delete()
    
    def certification(self):
        self.resources += "认证"
        params_field = (
            "id",
            "name",
            "sn",
            "typ",
            )
        required_field = (
            "id",
            "name",
            "sn",
            )
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_data}")
        params = {x: self.request_data.get(x) for x in params_field if self.request_data.get(x) is not None}
        
        if not all([x in params for x in required_field]):
            raise ParamError(f"缺少必填参数", code=RET.RequiredERR)
        
        pk = params.pop("id")
        instance = self.queryset.filter_by(id=pk).first()
        if not instance:
            raise DataError(f"用户不存在", code=RET.NODATA)
        
        customer = CustomerModel.query.filter_by(is_deleted=0, **params).first()
        if not customer:
            params["create_user"] = self.current_user.username
            params["update_user"] = self.current_user.username
            customer = CustomerModel().create(**params)
        
        instance.customer_id = customer.id
        result = instance.update()
        return json_resp(RET.OK, f"{self.resources}成功", data=result)


class CustomerView(ModelViewSet):
    decorators = [IsLoginPermission]
    resources = "客户"
    model = CustomerModel
    query_field = (
        "id",
        "name",
        "sn",
        "typ",
        )
    update_field = (
        "id",
        "name",
        "sn",
        "remark",
        )
