#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : view.py
# @Time    : 2020/9/12 21:45
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import logging

from flask import request

from .model import *
from main.util.meta import BaseViewSet
from main.util.common import json_resp, make_cache_key
from main.util.response_code import RET
from main.setting import cache
from main.util.auth import user_required, SignAdminPermission
from main.util.error import PlusException
from ..util import jwt_encode_handler

logger = logging.getLogger(__name__)


class UserView(BaseViewSet):
    model = UserModel
    decorators = ()
    resources = "用户"
    query_field = (
        "username",
        "nickname",
        "role",
        )
    create_field = (
        "username",
        "nickname",
        "password",
        "is_superuser",
        "role",
        "comment",
        )
    update_field = (
        "id",
        "nickname",
        "password",
        "is_superuser",
        "role",
        "is_used",
        "is_active",
        "comment",
        )
    create_required_field = (
        "username",
        "password",
        )
    
    @property
    def queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    def login(self):
        try:
            logger.info(f"{self.resources}登录 user:{request.headers.get('host')} params:{self.request_data}")
            
            username = self.request_data.get("username")
            password = self.request_data.get("password")
            if not all([username, password]):
                raise PlusException(f"缺少必填参数")
            
            instance = self.queryset.filter_by(username=username).first()
            if not instance:
                raise PlusException(f"用户{username}不存在", code=RET.USERERR)
            if not instance.check_password(password):
                raise PlusException(f"用户名密码错误", code=RET.PWDERR)
            instance.last_login = datetime.now()
            user = instance.update()
            
            data = {
                "token": jwt_encode_handler(instance),
                "user": user
                }
            return json_resp(RET.OK, f"{self.resources}登录成功", data=data)
        except Exception as e:
            logger.error(f"{self.resources}登录错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}登录错误 error:{e}", data=None)
    
    @cache.cached(make_cache_key=make_cache_key)
    def post_query(self):
        try:
            logger.info(f"{self.resources}查询 user:{request.headers.get('host')} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.query_field if self.request_data.get(x, "") != ""}
            
            queryset = self.queryset.filter_by(**params)
            queryset = queryset.order_by(self.model.update_time.desc())
            offset = self.request_data.get("offset")
            limit = self.request_data.get("limit")
            if offset and limit:
                instance = queryset.offset(offset).limit(limit).all()
                total = queryset.count()
            else:
                instance = queryset.all()
                total = len(instance)
            
            data = self.model.to_list(instance)
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    def create(self):
        try:
            logger.info(f"{self.resources}创建 user:{request.headers.get('host')} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.create_field if self.request_data.get(x) is not None}
            
            if not all([x in params for x in self.create_required_field]):
                raise PlusException(f"缺少必填参数")
            
            params["user"] = request.headers.get('host')
            obj = self.model(**params)
            obj.password = params["password"]
            data = obj.create()
            
            return json_resp(RET.OK, f"{self.resources}创建成功", data=data)
        except Exception as e:
            logger.error(f"{self.resources}创建错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}创建错误 error:{e}", data=None)

    @property
    def update_queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    @user_required
    def update(self):
        try:
            logger.info(f"{self.resources}更新 user:{request.headers.get('host')} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.update_field if self.request_data.get(x) is not None}
            
            if not all([x in params for x in self.update_required_field]):
                raise PlusException("缺少必填参数")
            pk = params.pop("id")
            
            params["user"] = request.headers.get('host')
            instance = self.update_queryset.filter_by(id=pk).first()
            if not instance:
                raise PlusException(f"对象不存在", code=RET.NODATA)
            for k, v in params.items():
                setattr(instance, k, v)
            
            result = instance.update()
            
            return json_resp(RET.OK, f"{self.resources}更新成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}更新错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}更新错误 error:{e}", data=None)

    @property
    def delete_queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    def delete(self):
        try:
            logger.info(f"{self.resources}删除 user:{request.headers.get('host')} params:{self.request_data}")
            
            pk = self.request_data.get("id")
            is_deleted = self.request_data.get("is_deleted", True)
            if pk is None:
                raise PlusException("缺少id参数")
            
            result = self.delete_queryset.filter_by(id=pk).update(dict(
                user=request.headers.get('host'),
                is_deleted=self.model.id if is_deleted else 0
                ))
            self.db_commit()
            
            return json_resp(RET.OK, f"{self.resources}删除成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}删除错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}删除错误 error:{e}", data=None)


class UriView(BaseViewSet):
    resources = "uri"
    model = UriModel
    query_field = (
        "id",
        "request_method",
        "uri",
        )
    create_field = (
        "request_method",
        "uri",
        )
    create_required_field = (
        "request_method",
        "uri",
        )
    update_field = (
        "id",
        "request_method",
        "uri",
        )
    
    @property
    def queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    def query_uri(self):
        try:
            logger.info(f"{self.resources}查询 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.query_field if self.request_data.get(x, "") != ""}
            
            queryset = self.queryset.filter_by(**params)
            queryset = queryset.order_by(self.model.update_time.desc())
            offset = self.request_data.get("offset")
            limit = self.request_data.get("limit")
            if offset and limit:
                instance = queryset.offset(offset).limit(limit).all()
                total = queryset.count()
            else:
                instance = queryset.all()
                total = len(instance)
            
            data = self.model.to_list(instance)
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    @SignAdminPermission()
    def create(self):
        try:
            logger.info(f"{self.resources}创建 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.create_field if self.request_data.get(x) is not None}
            
            if not all([x in params for x in self.create_required_field]):
                raise PlusException(f"缺少必填参数")
            
            params["author"] = self.current_user.username
            obj = self.model(**params)
            data = obj.create()
            
            return json_resp(RET.OK, f"{self.resources}创建成功", data=data)
        except Exception as e:
            logger.error(f"{self.resources}创建错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}创建错误 error:{e}", data=None)
    
    @property
    def update_queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    @SignAdminPermission()
    def update(self):
        try:
            logger.info(f"{self.resources}更新 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.update_field if self.request_data.get(x) is not None}
            
            if not all([x in params for x in self.update_required_field]):
                raise PlusException("缺少必填参数")
            pk = params.pop("id")
            
            params["author"] = self.current_user.username
            result = self.update_queryset.filter_by(id=pk).update(params)
            self.db_commit()
            
            return json_resp(RET.OK, f"{self.resources}更新成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}更新错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}更新错误 error:{e}", data=None)
    
    @property
    def delete_queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    @SignAdminPermission()
    def delete(self):
        try:
            logger.info(f"{self.resources}删除 user:{self.current_user.username} params:{self.request_data}")
            
            pk = self.request_data.get("id")
            result = self.delete_queryset.filter_by(id=pk).delete()
            self.db_commit()
            
            return json_resp(RET.OK, f"{self.resources}删除成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}删除错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}删除错误 error:{e}", data=None)


class UserUriView(BaseViewSet):
    resources = "用户uri"
    model = UserUriModel
    query_field = (
        "id",
        "username",
        "request_method",
        "uri",
        )
    create_field = (
        "username",
        "request_method",
        "uri",
        "comment",
        )
    create_required_field = (
        "username",
        "request_method",
        "uri",
        )
    
    @property
    def queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    @SignAdminPermission()
    def post_query(self):
        try:
            logger.info(f"{self.resources}查询 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.query_field if self.request_data.get(x, "") != ""}
            
            queryset = self.queryset.filter_by(**params)
            queryset = queryset.order_by(self.model.update_time.desc())
            offset = self.request_data.get("offset")
            limit = self.request_data.get("limit")
            if offset and limit:
                instance = queryset.offset(offset).limit(limit).all()
                total = queryset.count()
            else:
                instance = queryset.all()
                total = len(instance)
            
            data = self.model.to_list(instance)
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    @SignAdminPermission()
    def create(self):
        try:
            logger.info(f"{self.resources}创建 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.create_field if self.request_data.get(x) is not None}
            
            if not all([x in params for x in self.create_required_field]):
                raise PlusException(f"缺少必填参数")
            
            params["author"] = self.current_user.username
            obj = self.model(**params)
            data = obj.create()
            
            return json_resp(RET.OK, f"{self.resources}创建成功", data=data)
        except Exception as e:
            logger.error(f"{self.resources}创建错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}创建错误 error:{e}", data=None)
    
    @property
    def delete_queryset(self):
        return self.model.query.filter_by(is_deleted=0)
    
    @SignAdminPermission()
    def delete(self):
        try:
            logger.info(f"{self.resources}删除 user:{self.current_user.username} params:{self.request_data}")
            
            pk = self.request_data.get("id")
            result = self.delete_queryset.filter_by(id=pk).delete()
            self.db_commit()
            
            return json_resp(RET.OK, f"{self.resources}删除成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}删除错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}删除错误 error:{e}", data=None)
