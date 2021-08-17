#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : wsgi.py
# @Time    : 2020/10/1 21:08
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
from main.setting import create_app, db

application = create_app()

if __name__ == '__main__':
    application.run()

