#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : task.py
# @Time   : 2021/8/17 21:42
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import logging

from celery_task.main import celery_app
from main.draw_chart.data_source import tiobe

logger = logging.getLogger(__name__)


@celery_app.task(name="refresh_tiobe.task.refresh")
def refresh():
    try:
        tiobe.save(tiobe.request_tiobe())
        
        logger.info(f"刷新tiobe数据成功")
    except Exception as e:
        logger.error(f"刷新tiobe数据失败 {e}")


if __name__ == '__main__':
    refresh()
