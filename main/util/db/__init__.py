#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : __init__.py.py
# @Time   : 2020/12/25 11:44
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :

__all__ = [
    'redis_store', 'redis_conn'
    ]

from main.util.db.redis_db import redis_store, redis_conn
