#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : config.py
# @Time   : 2021/8/17 14:25
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import os
from datetime import timedelta

from celery.schedules import crontab
from kombu import Queue, Exchange

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 消息中间件
# redis://:password@hostname:port/db_number
broker_url = 'redis://:remote_redis@localhost:6379/1'
# 结果接收地址
result_backend = 'redis://:remote_redis@localhost:6379/2'

# 任务序列化方式
task_serializer = 'json'
# 结果序列化方式
result_serializer = 'json'
# 接受的序列化方式
accept_content = ['json']
# 时区
# timezone = 'Europe/Oslo'
# enable_utc = True

imports = [
    "celery_task.clean_file.task",
    "celery_task.refresh_tiobe.task",
    ]

# redis作消息中间件 只支持type='direct'，对于direct模式 routing_key可以不需要
task_queues = (
    Queue('default', exchange=Exchange('default', type='direct'), routing_key='default'),
    Queue('q1', exchange=Exchange('e1', type='direct'), routing_key='k1'),
    Queue('q2', exchange=Exchange('e2', type='direct'), routing_key='k2'),
    )

# 路由 将消费队列和任务连接对应
# 注   task_routes  ],)   这里必须是个元组
task_routes = ([
                   ('refresh_tiobe.task.refresh', {'queue': 'q1'}),
                   ('clean_file.task.clean', {'queue': 'q2'}),
                   ],)

# 启动多个work，任务并不会重复执行，谁先拿到，谁执行
# 在启动worker的时候可以指定work接受那个队列
# 第一种： -Q  指定Queue  只接受指定队列任务
# 第二种 ： 不指定（全部执行）  接受全部


# 定时任务
beat_schedule = {
    "delta_task": {
        "task": "refresh_tiobe.task.refresh",  # 注册的任务名
        # "schedule": crontab(minute="0", hour="2"),  # 每天的2点执行
        "schedule": crontab(minute="1"),  # test
        "args": ()  # 任务函数参数
        },
    "crontab_task": {
        "task": "clean_file.task.clean",  # 注册的任务名
        # "schedule": timedelta(hours=24),  # 每间隔24小时执行一次
        "schedule": timedelta(minutes=1),  # test
        "args": (os.path.join(BASE_DIR, "dist"),)  # 任务函数参数
        },
        
    }
