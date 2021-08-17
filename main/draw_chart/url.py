#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : url.py
# @Time    : 2020/8/30 17:30
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import logging

from flask import Blueprint, request, Response, abort

from .view import *
from main.util import uri_required, json_resp

blu_chart = Blueprint("chart", __name__)
logger = logging.getLogger(__name__)


@blu_chart.route("/", methods={"GET", "POST"})
def home():
    return "this is draw chart home page!"


blu_chart.add_url_rule("tiobe/option/", view_func=TiobeView.as_view({"GET": "query_option", "POST": "query_option"}))
blu_chart.add_url_rule("tiobe/query/", view_func=TiobeView.as_view({"GET": "get_query", }))

blu_chart.add_url_rule("stock/option/", view_func=StockView.as_view({"GET": "query_option", "POST": "query_option"}))
blu_chart.add_url_rule("stock/query/", view_func=StockView.as_view({"GET": "get_query", }))
