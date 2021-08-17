#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : manage.py.py
# @Time    : 2020/8/30 15:28
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
from flask_migrate import Migrate
from flask_script import Manager

from main.setting import create_app, db

app = create_app()
manager = Manager(app)
Migrate(app, db)

if __name__ == '__main__':
    manager.run()

# 1.python manage.py db init
# 2.python manage.py db migrate -m"版本名(注释)"
# 3.python manage.py db upgrade 然后观察表结构
# 4.根据需求修改模型
# 5.python manage.py db migrate -m"新版本名(注释)"
# 6.python manage.py db upgrade 然后观察表结构
# 7.若返回版本,则利用 python manage.py db history查看版本号
# 8.python manage.py db downgrade(upgrade) 版本号
