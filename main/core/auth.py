#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : auth.py
# @Time    : 2020/8/30 15:32
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc    : 认证和权限校验
import base64
import functools
import json
import jwt
import logging
import time
import urllib.parse

from flask import current_app, g, request
from werkzeug.local import LocalProxy

from .error import AuthenticationFailed, PlusException, DataError, PermissionDenied
from .jwt_util import jwt_decode_handler
from .fmt_resp import json_resp, RET
from main.util.db import redis_store
from main.config import REQUEST_EXPIRE, REQUEST_NONCE_PREFIX, REQUEST_NONCE_EXPIRE

logger = logging.getLogger(__name__)


# Authentication
# ============================================
def authentication():
    try:
        return JWTAuthentication() or ApiAuthentication()
    except Exception as e:
        msg = f"认证失败：{e}"
        logger.error(msg)
        return json_resp(getattr(e, "code", RET.AUTHERR), msg)


class BaseAuthentication(object):
    """签名认证
    """
    
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        return instance.authenticate()
    
    www_authenticate_realm = "token"
    
    def authenticate(self):
        # Authorization : jwt signature
        auth = request.headers.get("Authorization", "")  # request.headers的key不区分大小写，默认会将首字母大写
        auth = auth.split()
        if not auth or auth[0].lower() != self.www_authenticate_realm:
            return None
        
        if len(auth) != 2:
            msg = "Invalid basic header. Credentials string wrong length."
            raise AuthenticationFailed(msg, code=RET.JWTFormatError)
        
        user = self.authenticate_credentials(auth[1])
        self.set_user(user)
        
        logger.info(f"{self.www_authenticate_realm}认证成功,username：{user.username}")
    
    def authenticate_credentials(self, *args, **kwargs):
        raise NotImplementedError
    
    @staticmethod
    def set_user(user):
        g.user = user


class JWTAuthentication(BaseAuthentication):
    """JWT 认证
    """
    www_authenticate_realm = "jwt"
    
    def authenticate_credentials(self, token):
        try:
            user_id = jwt_decode_handler(token)
        except jwt.DecodeError as e:
            raise AuthenticationFailed(f"token解析失败 {e}", code=RET.JWTDecodeError)
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationFailed(f"token超时 {e}", code=RET.JWTExpiredError)
        except Exception as e:
            raise AuthenticationFailed(f"token解析错误 {e}", code=RET.JWTDecodeError)
        
        user = self.get_user_info(user_id)
        
        return user
    
    @staticmethod
    def get_user_info(user_id):
        try:
            from main.user.model import UserModel
            user = UserModel.query.filter_by(id=user_id).first()
        except Exception as e:
            raise DataError(f"查询用户信息错误 {e}", code=RET.DBERR)
        
        if not user:
            raise AuthenticationFailed(f"用户不存在", code=RET.UserNotExite)
        
        if not user.is_active:
            raise AuthenticationFailed("用户未启用", code=RET.NotActive)
        
        return user.to_dict()


class ApiAuthentication(BaseAuthentication):
    """服务端api认证
    """
    www_authenticate_realm = "api"
    
    def authenticate_credentials(self, signature):
        try:
            sign = self.decode_sign(signature)
        except Exception as e:
            raise AuthenticationFailed(f"签名解析失败 {e}", code=RET.JWTDecodeError)
        
        if any([x not in sign for x in {"username", "password", "timestamp", "nonce"}]):
            raise AuthenticationFailed("非法请求,认证参数缺失!", code=RET.AUTHERR)
        
        if int(time.time()) - int(sign["timestamp"]) > REQUEST_EXPIRE:
            raise AuthenticationFailed("非法请求,认证已过期!", code=RET.JWTExpiredError)
        
        if redis_store.get(REQUEST_NONCE_PREFIX + sign["nonce"]):
            raise AuthenticationFailed("非法请求,重放请求!", code=RET.AUTHERR)
        
        v = f"{request.remote_addr}:{request.method.upper()}:{request.path}"
        redis_store.set(REQUEST_NONCE_PREFIX + sign["nonce"], v, ex=REQUEST_NONCE_EXPIRE)
        
        try:
            from main.user.model import UserModel
            user = UserModel.query.filter_by(username=sign["username"], is_deleted=0).first()
        except Exception as e:
            raise DataError(f"查询用户信息错误 {e}", code=RET.DBERR)
        
        if not user:
            raise AuthenticationFailed(f"用户不存在", code=RET.UserNotExite)
        
        if not user.check_password(sign["password"]):
            raise AuthenticationFailed("用户名密码错误", code=RET.PWDERR)
        
        if not user.is_active:
            raise AuthenticationFailed("用户未启用", code=RET.NotActive)
        
        return user.to_dict()
    
    @staticmethod
    def decode_sign(signature):
        """
        
        """
        code_flg = "utf-8"
        sign = base64.b64decode(signature.encode(code_flg)).decode(code_flg)
        sign = json.loads(sign)
        return sign


# Permission
# ============================================
def login_required(f):
    """Checks whether user is logged in or raises error 401."""
    
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        if not hasattr(g, "user"):
            raise PermissionDenied(f"用户未登录", code=RET.NotLogging)
        return f(*args, **kwargs)
    
    return decorator


def permission_classes(permission_list):
    def decorator(func):
        func.decorators = permission_list
        return func
    
    return decorator


class IsLoginPermission:
    """类装饰器不能用于类中的方法，对于单个方法配合permission_classes使用
    """
    
    def __init__(self, func):
        self.__func = func
    
    def __call__(self, *args, **kwargs):
        if not hasattr(g, "user"):
            raise PermissionDenied(f"用户未登录", code=RET.NotLogging)
        
        return self.__func(*args, **kwargs)


class IsAdminPermission:
    def __init__(self, func):
        self.__func = func
    
    def check_permission(self):
        from main.user.model import UserModel
        
        if not UserModel.is_admin(g.user.role):
            raise PermissionDenied(f"当前用户无权限", code=RET.NoPerm)
    
    def __call__(self, *args, **kwargs):
        self.check_permission()
        return self.__func(*args, **kwargs)


class DataApiPermission:
    def __init__(self, func):
        self.__func = func
    
    def check_permission(self):
        from main.user.model import UserModel
        from main.perm.model import PermModel
        
        if UserModel.is_admin(g.user.role):
            return
        
        user = g.user
        request_method = request.method.upper()
        uri = request.path
        
        perm = PermModel.get_perm(user.id)
        for i in perm:
            if i.get("perm_typ") == "data_api" and i.get("perm_value") == f"{request_method}:{uri}":
                return
        
        raise PermissionDenied(f"当前用户无权限", code=RET.NoPerm)
    
    def __call__(self, *args, **kwargs):
        self.check_permission()
        return self.__func(*args, **kwargs)


class RequestFromPermission:
    def __init__(self, request_from):
        self.request_from = request_from
    
    def check_permission(self):
        if isinstance(self.request_from, (tuple, list)):
            if g.request_from in self.request_from:
                return
        else:
            if g.request_from == self.request_from:
                return
        
        raise PermissionDenied(f"当前用户无权限", code=RET.NoPerm)
    
    def __call__(self, f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            self.check_permission()
            return f(*args, **kwargs)
        
        return wrapped
