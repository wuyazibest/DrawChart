#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : task.py
# @Time   : 2021/8/17 14:26
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import logging
import os

from celery_task.main import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="clean_file.task.clean")
def clean(path=""):
    try:
        if not os.path.isdir(path):
            logger.error(f"删除文件失败,目录不存在 {path}")
        
        cou = 0
        for i in os.listdir(path):
            if i.endswith(".html"):
                os.remove(os.path.join(path, i))
                cou += 1
        
        logger.info(f"删除文件成功，共删除文件{cou}个")
        return cou
    except Exception as e:
        logger.error(f"删除文件失败 {e}")


if __name__ == '__main__':
    clean()
