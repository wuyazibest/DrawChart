#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : middleware.py
# @Time   : 2020/11/25 14:33
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import logging
import time

from flask import request, json, jsonify, g
from flask_wtf.csrf import generate_csrf

from .auth import authentication
from .fmt_resp import json_resp, norm_data
from .response_code import RET
from main.util.encrypt import verify_sign, attach_sign
from main.config import RequestFrom

logger = logging.getLogger(__name__)


def init_database(app, db):
    # 初始化所有数据库表
    with app.app_context():
        # db.drop_all()
        db.create_all()


def set_csrf(response):
    """csrf 默认校验'POST', 'PUT', 'PATCH', 'DELETE'
    需要先通过get请求获取cookie中的csrf token
    然后 post 等请求时 在header中携带X-CSRFToken
    """
    # 生成随机csrf_token值
    csrf_token = generate_csrf()
    # 往cookie中写随机值
    response.set_cookie("csrf_token", csrf_token)
    return response


def add_sign(response):
    try:
        if not response.json:
            return response
        data = attach_sign(response.json or {}, prefix="api nonce ")
        response.set_data(json.dumps(data))
    except Exception as e:
        msg = f"加签出错！{e}"
        logger.error(msg)
        response = jsonify(attach_sign(norm_data(RET.SYSERR, msg)))
    
    return response


def request_from():
    # 请求来源
    request_from = request.headers.get("RequestFrom")
    request_from = request_from if request_from in RequestFrom else RequestFrom.web.key
    
    g.request_from = request_from


def init_hook(app):
    """Flask 请求钩子(hook)
    """
    
    @app.before_first_request
    def handle_before_first_request():
        """在第一次请求处理之前被执行 (服务器启动后,只会执行一次)
        """
        pass
    
    @app.before_request
    def handle_before_request():
        """在每次请求之前都被执行
        """
        request_from()
        return authentication()
    
    @app.after_request
    def handle_after_request(response):
        """
        # 必须传入response参数(视图函数返回的response)
        在每次请求(视图函数处理)之后都被执行, 前提是视图函数没有出现异常
        """
        # response = set_csrf(response)  # 使用JWT校验，不存在csrf攻击问题，不再需要防范
        # response = add_sign(response)
        return response
    
    @app.teardown_request
    def handle_teardown_request(response):
        """
         # 必须传入response参数(视图函数返回的response)
        在每次请求(视图函数处理)之后都被执行，无论视图函数是否出现异常都被执行(只有在生产环境下才会执行)
        """
        return response


def register_error_handler(app):
    @app.errorhandler(404)
    def handle_404_error(err):
        """
        以json格式返回url错误
        """
        return json_resp(RET.REQERR, f"路由未发现 {err}")
    
    @app.errorhandler(405)
    def handle_405_error(err):
        """
        以json格式返回url错误
        """
        return json_resp(RET.REQERR, f"请求方式错误 {err}")
    
    @app.errorhandler(Exception)
    def catch_all_except(err):
        return json_resp(RET.UNKOWNERR, f"{err}")
