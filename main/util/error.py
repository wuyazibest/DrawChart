#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : error.py
# @Time   : 2020/11/25 14:36
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :

import sqlalchemy.exc
from flask import Response

from .common import json_resp
from .response_code import RET


class PlusError(Exception):
    code = None
    status = None
    
    def __init__(self, *args, code=None, status=None, **kwargs):
        super(PlusError, self).__init__(*args)
        self.code = code or self.code
        self.status = status or self.status
        for k, v in kwargs.items():
            setattr(self, k, v)


class PlusException(PlusError):
    code = RET.PARAMERR


class ParamError(PlusError):
    code = RET.PARAMERR


class AuthenticationFailed(PlusError):
    code = RET.AUTHERR


class PermissionDenied(PlusError):
    code = RET.ROLEERR


class RequestAborted(PlusError):
    """The request was closed before it was completed, or timed out."""
    pass


class ViewDoesNotExist(PlusError):
    """The requested view does not exist"""
    pass


class MiddlewareNotUsed(PlusError):
    """This middleware is not used in this server configuration"""
    pass


class ImproperlyConfigured(PlusError):
    """Django is somehow improperly configured"""
    pass


class FieldError(PlusError):
    """Some kind of problem with a model field."""
    pass


class ValidationError(PlusError):
    """校验错误"""
    code = RET.PARAMERR


class HttpResponseError:
    
    @staticmethod
    def server_error(message):
        return json_resp(RET.SERVERERR, message)
    
    @staticmethod
    def method_error(message):
        return json_resp(RET.METHODERR, message)


def plus_assert(expression, msg="", code=RET.PARAMERR, status=None):
    """
    自定义断言，可以指定错误类型
    """
    if not expression:
        raise PlusException(msg, code=code, status=status)


def exception_handler(exc, prefix='', **kwargs):
    """
    统一错误处理
    :param exc:
    :param prefix:
    :param kwargs:
    :return:
    """
    if isinstance(exc, ValidationError):
        return json_resp(RET.PARAMERR, f"数据校验错误：{exc}", **kwargs)
    
    if isinstance(exc, sqlalchemy.exc.IntegrityError):
        if "UniqueViolation" in str(exc):
            return json_resp(RET.DATAERR, f"该资源已存在，重复创建")
        
        return json_resp(RET.DATAERR, f"数据写入错误  error：{exc}", **kwargs)
    
    if isinstance(exc, sqlalchemy.exc.SQLAlchemyError):
        return json_resp(RET.DATAERR, f"数据库操作错误 error：{exc}", **kwargs)
    
    return json_resp(getattr(exc, "code", RET.SERVERERR), f"{prefix} error: {exc}", **kwargs)
