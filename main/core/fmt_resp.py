#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : fmt_resp.py
# @Time   : 2024/12/25 19:11
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from flask import jsonify, request

from .response_code import error_map, RET


def norm_data(code, desc=None, data=None, **kwargs):
    kwargs["code"] = code if code in error_map else RET.UNKOWNERR
    kwargs["msg"] = error_map.get(code, "未知消息")
    kwargs["desc"] = desc or error_map.get(code, "未知消息")
    kwargs["data"] = data
    return kwargs


def json_resp(code, desc=None, data=None, **kwargs):
    return jsonify(norm_data(code, desc=desc, data=data, **kwargs))
