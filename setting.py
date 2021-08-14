#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : setting.py
# @Time   : 2021/7/27 21:36
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import logging

from pyecharts.globals import CurrentConfig

from config import *

CurrentConfig.ONLINE_HOST = PYECHARTS_ASSETS_HOST or CurrentConfig.ONLINE_HOST.OnlineHostType.DEFAULT_HOST


def init_log():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        filename="log.log"
        )


init_log()
