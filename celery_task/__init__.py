#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : __init__.py.py
# @Time   : 2021/8/17 14:25
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
'''

启动定时任务生产者
celery -A celery_task.main beat -l info

启动消费者
celery -A celery_task.main worker -l info
指定消费的队列
celery -A celery_task.main worker -Q q1,q2 -l info
windows下启动
celery -A celery_task.main worker -l info -P gevent


同时启动生产者和消费者
# celery -A celery_task.main worker -B -l info


# 守护进程
celery multi start w1 -A celery_task.main -l info --logfile=./logs/celery.log
停止和重启 分别将 start 改为 stop / restart
celery multi restart w1 -A celery_task.main -B -l info --logfile=./logs/celery.log
celery status -A celery_task.main
查看该项目运行的进程数


'''
