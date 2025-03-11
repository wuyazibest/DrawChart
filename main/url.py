#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : url.py
# @Time   : 2020/11/22 21:44
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :


def register_url(app):
    """
    蓝图注册中心
    :param app:
    :return:
    """
    from main.user.url import blu_user
    app.register_blueprint(blu_user, url_prefix="/user")
    
    from main.draw_chart.url import blu_chart
    app.register_blueprint(blu_chart, url_prefix="/chart")
    
    print("===" * 10)
    print(app.url_map)
    print("===" * 10)
