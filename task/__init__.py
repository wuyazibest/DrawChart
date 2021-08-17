#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : __init__.py.py
# @Time   : 2020/12/3 13:57
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   : 独立运行的定时任务、异步时延任务
import os

path = ""
for i in os.listdir(path):
    if i.endswith(".html"):
        os.remove(os.path.join(path, i))
