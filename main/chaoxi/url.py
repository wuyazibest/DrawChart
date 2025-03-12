#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : url.py
# @Time   : 2025/3/11 16:36
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from flask import Blueprint

from .view import *

blu_chaoxi = Blueprint("chaoxi", __name__)


@blu_chaoxi.route("/home", methods={"GET", "POST"})
def home():
    return "this is draw chaoxi home page!"


blu_chaoxi.add_url_rule("/chart/query", view_func=ChaoXiView.as_view({"GET": "get_query", }))
