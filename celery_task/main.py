#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : mian.py
# @Time   : 2021/8/17 14:25
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from celery import Celery, Task

celery_app = Celery()
celery_app.config_from_object("celery_task.config")
