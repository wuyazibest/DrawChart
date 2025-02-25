#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : error.py
# @Time   : 2020/11/25 14:36
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :

import sqlalchemy.exc
from flask import Response

from .fmt_resp import json_resp
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
    """参数错误
    """
    code = RET.PARAMERR


class AuthenticationFailed(PlusError):
    """认证错误
    """
    code = RET.AUTHERR


class PermissionDenied(PlusError):
    """权限错误
    """
    code = RET.PermERR


class DataError(PlusError):
    """数据错误
    """
    code = RET.DATAERR


class SysError(PlusError):
    """系统错误
    """
    code = RET.SYSERR


class ThirdError(PlusError):
    """三方系统错误
    """
    code = RET.THIRDERR


class RequestAborted(PlusError):
    """The request was closed before it was completed, or timed out."""
    pass


class ViewDoesNotExist(PlusError):
    """The requested view does not exist"""
    pass


class MethodNotAllowed(PlusError):
    """不允许的请求方式"""
    code = RET.METHODERR


def exception_assert(expression, msg="", code=RET.VALIDERR):
    if not expression:
        raise ParamError(msg, code=code)


def exception_handler(self, exc, **kwargs):
    """
    统一错误处理
    :param self:
    :param exc:
    :param kwargs:
    :return:
    """
    
    if isinstance(exc, sqlalchemy.exc.IntegrityError):
        if "UniqueViolation" in str(exc):
            return json_resp(RET.EXISTDATA, f"唯一性错误，该资源已存在，重复创建")
        if "Duplicate entry" in str(exc):
            return json_resp(RET.EXISTDATA, f"联合唯一索引错误，该资源已存在，重复创建")
        
        return json_resp(RET.DATAERR, f"数据写入错误  error：{exc}")
    
    if isinstance(exc, sqlalchemy.exc.SQLAlchemyError):
        return json_resp(RET.DBERR, f"数据库操作错误 error：{exc}")
    
    msg = f"{self.resources}错误 error:{exc}"
    return json_resp(getattr(exc, "code", RET.SYSERR), msg, **kwargs)
