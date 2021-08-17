#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : error.py
# @Time   : 2020/11/25 14:36
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from flask import Response

from .common import json_resp
from .response_code import RET


class PlusException(Exception):
    def __init__(self, *args, code=RET.PARAMERR, status=None, **kwargs):
        super(PlusException, self).__init__(*args)
        self.code = code
        self.status = status
        for k, v in kwargs.items():
            setattr(self, k, v)


class AuthenticationFailed(PlusException):
    def __init__(self, *args, code=RET.AUTHERR, status=None, **kwargs):
        super(AuthenticationFailed, self).__init__(*args, code=code, status=status, **kwargs)


class PermissionDenied(PlusException):
    def __init__(self, *args, code=RET.ROLEERR, status=None, **kwargs):
        super(PermissionDenied, self).__init__(*args, code=code, status=status, **kwargs)


class RequestAborted(Exception):
    """The request was closed before it was completed, or timed out."""
    pass


class ViewDoesNotExist(Exception):
    """The requested view does not exist"""
    pass


class MiddlewareNotUsed(Exception):
    """This middleware is not used in this server configuration"""
    pass


class ImproperlyConfigured(Exception):
    """Django is somehow improperly configured"""
    pass


class FieldError(Exception):
    """Some kind of problem with a model field."""
    pass


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
