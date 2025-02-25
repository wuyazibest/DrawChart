#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : url.py
# @Time   : 2020/11/25 14:15
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from flask import Blueprint

from .view import *

blu_user = Blueprint("user", __name__)


@blu_user.route("/home", methods={"GET", "POST"})
def home():
    return "this is user home"


# login
blu_user.add_url_rule("/login", view_func=LoginView.as_view({"POST": "login"}))

# user
blu_user.add_url_rule("/sys_user/query", view_func=UserView.as_view({"POST": "post_query"}))
blu_user.add_url_rule("/sys_user/create", view_func=UserView.as_view({"POST": "create"}))
blu_user.add_url_rule("/sys_user/update", view_func=UserView.as_view({"PUT": "update"}))
blu_user.add_url_rule("/sys_user/delete", view_func=UserView.as_view({"DELETE": "delete"}))
blu_user.add_url_rule("/sys_user/certification", view_func=UserView.as_view({"POST": "certification"}))

blu_user.add_url_rule("/sys_customer/query", view_func=CustomerView.as_view({"POST": "post_query"}))
blu_user.add_url_rule("/sys_customer/update", view_func=CustomerView.as_view({"PUT": "update"}))
blu_user.add_url_rule("/sys_customer/delete", view_func=CustomerView.as_view({"DELETE": "delete"}))
