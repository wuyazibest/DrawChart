#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : setting.py
# @Time    : 2020/8/30 15:31
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import datetime
import logging
import os
import time

from flask import Flask, request, has_request_context, json
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import config
from main.util.single_logging import setup_log

db = SQLAlchemy(engine_options=config.SQLALCHEMY_ENGINE_OPTIONS_DEFAULT)
cache = Cache()
# Session = config.DataDict()
# Session["management"] = sessionmaker(bind=create_engine(config.SQLALCHEMY_BINDS["management"], pool_pre_ping=True))


def create_app():
    # 配置日志
    setup_log(config.LOG_LEVEL)
    # 创建Flask对象,__name__为当前目录
    app = Flask(__name__, instance_relative_config=True)
    # 加载配置
    app.config.from_object(config)
    # 初始化mysql数据库
    # db=SQLAlchemy(app)
    db.init_app(app)
    
    # csrf注册，
    # CsrfProtect(app)
    
    # 初始化缓存工具
    cache.init_app(app)
    # 每次启动清除接口缓存
    cache.clear()
    
    # 初始化请求中间件
    from main.core.middleware import init_hook
    init_hook(app)
    
    # 注册蓝图
    from main.url import register_url
    register_url(app)
    
    from main.core.middleware import init_database
    init_database(app, db)
    
    from main.core.middleware import register_error_handler
    register_error_handler(app)
    
    # 统一错误处理
    from main.core.error import exception_handler
    app.extensions["exception_handler"] = exception_handler
    
    # 指定json编码的工具
    class UpdatedJSONProvider(json.provider.DefaultJSONProvider):
        ensure_ascii = False
        sort_keys = False
        compact = False
        
        def default(self, o):
            if isinstance(o, datetime.datetime):
                return o.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(o, datetime.date):
                return o.strftime("%Y-%m-%d")
            
            return super().default(o)
    
    app.json = UpdatedJSONProvider(app)
    
    return app
