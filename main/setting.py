#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : setting.py
# @Time    : 2020/8/30 15:31
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, request, has_request_context
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from main import config

db = SQLAlchemy()
cache = Cache()


def create_app():
    # 配置日志
    setup_log(config.LOG_LEVEL)
    # 创建Flask对象,__name__为当前目录
    app = Flask(
        __name__,
        static_url_path="/static",  # 页面访问静态文件的前缀
        static_folder=os.path.join(config.BASE_DIR, "dist"),  # 实际静态文件的存放目录  最好使用绝对路径
        template_folder=os.path.join(config.BASE_DIR, "dist"),
        instance_relative_config=True
        )
    # 加载配置
    app.config.from_object(config)
    
    # 指定json编码的工具
    from main.util.common import JSONEncoder
    app.json_encoder = JSONEncoder
    
    # 初始化数据库
    # db=SQLAlchemy(app)
    db.init_app(app)
    
    # 初始化缓存工具
    cache.init_app(app)
    # 每次启动清楚接口缓存
    cache.clear()
    
    # csrf注册，
    # CsrfProtect(app)
    
    # error handle注册
    from main.util.middleware import register_error_handler
    register_error_handler(app)
    
    # 初始化请求中间件
    from main.util.middleware import init_hook
    init_hook(app)
    
    # 注册蓝图
    from main.url import register_url
    register_url(app)
    
    return app


def setup_log(level_name):
    formatter_simple = logging.Formatter("%(levelname)-8s %(asctime)s %(filename)s:%(lineno)d %(message)s")
    formatter_long = UnwrapFormatter(
        "%(levelname)-8s %(asctime)s %(name)s %(filename)s:%(lineno)d:%(funcName)s "
        "%(request_method)s %(request_path)s %(request_addr)s %(message)s")
    
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formatter_simple)
    handler_console.setLevel(logging.DEBUG)
    
    handler_file = RotatingFileHandler("log/log.log", maxBytes=1024 * 1024 * 100, backupCount=10, encoding="utf-8")
    handler_file.setFormatter(formatter_long)
    handler_file.setLevel(logging.DEBUG)
    
    handler_err = RotatingFileHandler("log/err.log", maxBytes=1024 * 1024 * 100, backupCount=10, encoding="utf-8")
    handler_err.setFormatter(formatter_long)
    handler_err.setLevel(logging.ERROR)
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level_name.upper()))
    logger.addHandler(handler_console)
    logger.addHandler(handler_file)
    logger.addHandler(handler_err)
    
    # 关闭模块日志
    # logging.getLogger("werkzeug").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").propagate = False


class UnwrapFormatter(logging.Formatter):
    """强制日志不换行
    """
    
    def format(self, record):
        if has_request_context():
            record.request_method = request.method.upper()
            record.request_path = request.path
            record.request_addr = request.remote_addr
        else:
            record.request_method = ""
            record.request_path = ""
            record.request_addr = ""
        
        s = super(UnwrapFormatter, self).format(record)
        s = s.strip().replace("\r", " ").replace("\n", " ")
        return s
