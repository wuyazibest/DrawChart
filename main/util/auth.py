#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : auth.py
# @Time    : 2020/8/30 15:32
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc    : 认证和权限校验
import functools
import logging
from datetime import datetime

from flask import current_app, g, request
from werkzeug.local import LocalProxy

from .encrypt import verify_sign
from .error import AuthenticationFailed
from .jwt_util import jwt_decode_handler
from .common import json_resp, RET

logger = logging.getLogger(__name__)
UserModel = LocalProxy(lambda: current_app.extensions["UserModel"])


# Authentication
# ============================================

class JWTAuthentication(object):
    """
    获取token
    校验token
    添加user信息到g
    """
    www_authenticate_realm = "jwt"
    
    @classmethod
    def authenticate(cls):
        token = cls.get_authorization_header()
        if token:
            try:
                user = cls.authenticate_credentials(token)
            except Exception as e:
                return json_resp(getattr(e, "code", RET.AUTHERR), f"Invalid token error:{e}", data=None)
    
    @classmethod
    def get_authorization_header(cls):
        # Authorization
        auth = request.headers.get("Authorization", "")
        auth = auth.split()
        if not auth or auth[0].lower() != cls.www_authenticate_realm:
            return None
        
        if len(auth) < 2:
            msg = "Invalid basic header. No credentials provided."
            raise Exception(msg)
        elif len(auth) > 2:
            msg = "Invalid basic header. Credentials string should not contain spaces."
            raise Exception(msg)
        return auth[1]
    
    @classmethod
    def authenticate_credentials(cls, token):
        try:
            user_id = jwt_decode_handler(token)
            user = cls.get_user_info(user_id)
            logger.info(f"{cls.www_authenticate_realm}认证成功,username：{user['username']}")
        except Exception as e:
            logger.info(f"{cls.www_authenticate_realm}认证失败，error: {e}")
            raise AuthenticationFailed(str(e))
        
        cls.set_user(user)
        return user
    
    @classmethod
    def get_user_info(cls, user_id):
        try:
            # from main.user.models import UserModel
            user = UserModel.query.filter_by(id=user_id).first()
        except Exception as e:
            raise Exception(f"查询用户信息错误 {e}")
        if not user:
            raise Exception(f"用户不存在")
        
        if not user.is_active:
            raise Exception("User inactive or deleted.")
        
        return user.to_dict()
    
    @staticmethod
    def set_user(user):
        g.user = user


class ApiAuthentication(object):
    """服务端api校验
    """
    www_authenticate_realm = "api"
    
    @classmethod
    def authenticate(cls):
        # Authorization
        auth = request.headers.get("Authorization", "")
        auth = auth.split()
        if not auth or auth[0].lower() != cls.www_authenticate_realm:
            return None
        
        if len(auth) < 3:
            msg = "Invalid basic header. No credentials provided."
            raise Exception(msg)
        elif len(auth) > 3:
            msg = "Invalid basic header. Credentials string should not contain spaces."
            raise Exception(msg)
        
        try:
            user = cls.authenticate_credentials(auth[1], auth[2])
        except Exception as e:
            return json_resp(getattr(e, "code", RET.AUTHERR), f"Invalid token error:{e}", data=None)
    
    @classmethod
    def authenticate_credentials(cls, username, password):
        try:
            user = cls.get_user_info(username, password)
            logger.info(f"{cls.www_authenticate_realm}认证成功,username：{user['username']}")
        except Exception as e:
            logger.info(f"{cls.www_authenticate_realm}认证失败，error: {e}")
            raise AuthenticationFailed(str(e))
        
        cls.set_user(user)
        return user
    
    @classmethod
    def get_user_info(cls, username, password):
        try:
            # from main.user.model import UserModel
            user = UserModel.query.filter_by(username=username).first()
        except Exception as e:
            raise Exception(f"查询用户信息错误 {e}")
        if not user:
            raise Exception(f"用户不存在")
        
        if not user.check_password(password):
            raise Exception("用户名密码错误")
        
        if not user.is_active:
            raise Exception("User inactive or deleted.")
        
        return user.to_dict()
    
    @staticmethod
    def set_user(user):
        g.user = user


class SignNonceAuthentication(object):
    """服务端nonce校验
    """
    www_authenticate_realm = "nonce"
    
    @classmethod
    def authenticate(cls, data):
        # authorization = nonce nonce signature
        auth = data.get("authorization", "")
        auth = auth.split()
        if not auth or auth[0].lower() != cls.www_authenticate_realm:
            return None
        
        data.pop("authorization")
        
        if len(auth) != 3:
            msg = "Invalid basic header. Credentials string wrong length."
            return json_resp(RET.AUTHERR, msg, data=None)
        
        return cls.authenticate_credentials(auth[1], auth[2], data)
    
    @classmethod
    def authenticate_credentials(cls, username, signature, data):
        try:
            if not verify_sign(data, signature):
                raise Exception("签名验证失败")
        
        except Exception as e:
            msg = f"{cls.www_authenticate_realm}认证失败，error: {e}"
            logger.info(msg)
            return json_resp(RET.AUTHERR, msg, data=None)


class SignApiAuthentication(object):
    """服务端api校验
    """
    www_authenticate_realm = "api"
    
    @classmethod
    def authenticate(cls, data):
        # authorization = api user signature
        auth = data.get("authorization", "")
        auth = auth.split()
        if not auth or auth[0].lower() != cls.www_authenticate_realm:
            return None
        
        data.pop("authorization")
        
        if len(auth) != 3:
            msg = "Invalid basic header. Credentials string wrong length."
            return json_resp(RET.AUTHERR, msg, data=None)
        
        return cls.authenticate_credentials(auth[1], auth[2], data)
    
    @classmethod
    def authenticate_credentials(cls, username, signature, data):
        try:
            user = cls.get_user_info(username)
            if not verify_sign(data, signature, user.password_hash):
                raise Exception("签名验证失败")
            
            logger.info(f"{cls.www_authenticate_realm}认证成功,username：{user.username}")
            cls.set_user(user)
        except Exception as e:
            msg = f"{cls.www_authenticate_realm}认证失败，error: {e}"
            logger.info(msg)
            return json_resp(RET.AUTHERR, msg, data=None)
    
    @classmethod
    def get_user_info(cls, username):
        try:
            from main.user.model import UserModel
            user = UserModel.query.filter_by(username=username, is_deleted=0).first()
        except Exception as e:
            raise Exception(f"查询用户信息错误 {e}")
        
        if not user:
            raise Exception(f"用户不存在")
        
        if not user.is_active:
            raise Exception("User inactive or deleted.")
        
        return user.to_dict()
    
    @staticmethod
    def set_user(user):
        g.user = user


# Permission
# ============================================

def user_required(f):
    """Checks whether user is logged in or raises error 401."""
    
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        if not getattr(g, "user"):
            return json_resp(RET.USERERR, f"用户还未登录", data=None)
        return f(*args, **kwargs)
    
    return decorator


def uri_required(f):
    """校验apitoken 校验成功返回视图 校验失败直接返回
    """
    
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        if not getattr(g, "user"):
            return json_resp(RET.USERERR, f"用户还未登录", data=None)
        # TODO： 校验用户的uri权限
        return f(*args, **kwargs)
    
    return decorator


class SignApiUserPermission:
    def __init__(self):
        self.headers = {}
    
    def check_permission(self):
        try:
            from main.user.model import UserModel, UserUriModel
            
            if not hasattr(g, "user"):
                raise Exception(f"用户未登录")
            
            if g.user.role == UserModel.RoleChoice.admin.name:
                return
            
            user = g.user
            request_method = request.method.upper()
            uri = request.path
            
            user_permission = UserUriModel.query.filter_by(
                username=user.username, request_method=request_method, uri=uri
                ).first()
            
            if not user_permission:
                raise Exception(f"无权限")
        
        except Exception as e:
            msg = f"check user permission error {e}"
            logger.error(msg)
            return json_resp(RET.AUTHERR, msg)

    def __call__(self, f):
        def wrapped(*args, **kwargs):
            permission = self.check_permission()
            if permission:
                return permission
            return f(*args, **kwargs)

        return wrapped


class SignAdminPermission:
    def __init__(self):
        self.headers = {}
    
    def check_permission(self):
        try:
            from main.user.model import UserModel, UserUriModel
            
            if not hasattr(g, "user"):
                raise Exception(f"用户未登录")
            
            if g.user.role != UserModel.RoleChoice.admin.name:
                raise Exception(f"无权限")
        
        except Exception as e:
            msg = f"check user permission error {e}"
            logger.error(msg)
            return json_resp(RET.AUTHERR, msg)
    
    def __call__(self, f):
        def wrapped(*args, **kwargs):
            permission = self.check_permission()
            if permission:
                return permission
            return f(*args, **kwargs)
        
        return wrapped
