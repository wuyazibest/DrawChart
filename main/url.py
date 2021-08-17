#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : url.py
# @Time   : 2020/11/22 21:44
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from flask import send_file


def register_url(app):
    """
    蓝图注册中心
    :param app:
    :return:
    """
    
    @app.route("/favicon.ico", methods={"GET", "POST"})
    def home():
        return app.send_static_file("favicon.png")
    
    from main.user.url import blu_user, UserModel
    # app.register_blueprint(blu_user, url_prefix="/user")
    
    from main.draw_chart.url import blu_chart
    app.register_blueprint(blu_chart, url_prefix="/chart")
    
    if not hasattr(app, "extensions"):  # pragma: no cover
        app.extensions = {}
    app.extensions["UserModel"] = UserModel
    
    print("===" * 10)
    print(app.url_map)
    print("===" * 10)
