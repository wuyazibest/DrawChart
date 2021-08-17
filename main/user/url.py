#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : url.py
# @Time    : 2020/9/12 21:44
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
from flask import Blueprint

from .view import *
from main.util import user_required

blu_user = Blueprint("user", __name__)


@blu_user.route("/", methods={"GET", "POST"})
def home():
    return "this is user home"


# user_info
blu_user.add_url_rule("/user_info/login/", view_func=UserView.as_view({"GET": "login", "POST": "login"}))
blu_user.add_url_rule("/user_info/query", view_func=UserView.as_view({"POST": "post_query"}))
blu_user.add_url_rule("/user_info/create", view_func=UserView.as_view({"POST": "create"}))
blu_user.add_url_rule("/user_info/update", view_func=UserView.as_view({"PUT": "update"}))
blu_user.add_url_rule("/user_info/delete", view_func=UserView.as_view({"DELETE": "delete"}))

# uri
blu_user.add_url_rule("/uri/query", view_func=UriView.as_view({"POST": "query_uri"}))
blu_user.add_url_rule("/uri/create", view_func=UriView.as_view({"POST": "create"}))
blu_user.add_url_rule("/uri/update", view_func=UriView.as_view({"PUT": "update"}))
blu_user.add_url_rule("/uri/delete", view_func=UriView.as_view({"DELETE": "delete"}))

# user_uri
blu_user.add_url_rule("/user_uri/query", view_func=UserUriView.as_view({"POST": "post_query"}))
blu_user.add_url_rule("/user_uri/create", view_func=UserUriView.as_view({"POST": "create"}))
blu_user.add_url_rule("/user_uri/delete", view_func=UserUriView.as_view({"DELETE": "delete"}))
