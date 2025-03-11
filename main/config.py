#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : config.py
# @Time    : 2020/8/30 15:31
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import base64
import configparser
import json
import os
from email.policy import default
from urllib.parse import quote_plus

from main.constant import *


class DataDict(dict):
    def __getattr__(self, item):
        if item in self:
            return self.get(item)
        return super().__getattribute__(item)
    
    def __setattr__(self, *args, **kwargs):
        self.__setitem__(*args, **kwargs)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_ENV = os.getenv("SERVER_ENV")
_CONFIG = configparser.ConfigParser()
_CONFIG.read(os.path.join(BASE_DIR, "conf/config.ini"), encoding="utf-8")


class Nacos:
    server_addresses = _CONFIG.get("nacos", "server_addresses")
    namespace = _CONFIG.get("nacos", "namespace")
    service_name = _CONFIG.get("nacos", "service_name")
    data_id = SERVER_ENV or _CONFIG.get("nacos", "data_id") or "development"
    group = _CONFIG.get("nacos", "group")
    
    @classmethod
    def connection(cls):
        import nacos
        return nacos.NacosClient(cls.server_addresses, namespace=cls.namespace)
    
    @classmethod
    def get_instance(cls):
        client = cls.connection()
        instance = client.list_naming_instance(cls.service_name, healthy_only=True)
        if not instance:
            raise Exception("nacos 读取服务器配置失败!")
        host_fir = instance["hosts"][0]
        return f"http://{host_fir.get('ip')}:{host_fir.get('port')}"
    
    @classmethod
    def get_conf(cls):
        client = cls.connection()
        return client.get_config(cls.data_id, cls.group)
    
    @classmethod
    def update_conf(cls):
        conf_path = os.path.join(BASE_DIR, "conf/conf_online.ini")
        conf_online = cls.get_conf()
        if conf_online:
            with open(conf_path, "w+", encoding="utf-8") as f:
                f.write(conf_online)
            
            _CONFIG.read(conf_path, encoding="utf-8")


# 使用配置中心的配置覆盖本地配置
if _CONFIG.getboolean("nacos", "enable", fallback=False):
    Nacos.update_conf()

# 当多服务端做冗余的时候此值需要设置为固定值
SECRET_KEY = bytes.decode(base64.b64encode(os.urandom(48)))
DEBUG = _CONFIG.getboolean("default", "debug")
LOG_LEVEL = _CONFIG.get("log", "level")

MySQLConf = DataDict(
    host=_CONFIG.get("mysql", "host"),
    port=_CONFIG.getint("mysql", "port"),
    user=_CONFIG.get("mysql", "user"),
    password=quote_plus(_CONFIG.get("mysql", "password")),
    db=_CONFIG.get("mysql", "db"),
    charset=_CONFIG.get("mysql", "charset"),
    pool_size=_CONFIG.getint("mysql", "pool_size"),
    max_overflow=_CONFIG.getint("mysql", "max_overflow"),
    pool_recycle=_CONFIG.getint("mysql", "pool_recycle"),
    pool_timeout=_CONFIG.getint("mysql", "pool_timeout"),
    pool_pre_ping=_CONFIG.getboolean("mysql", "pool_pre_ping"),
    echo=_CONFIG.getboolean("mysql", "echo"),
    )

PgSQLConf = DataDict(
    host=_CONFIG.get("pgsql", "host"),
    port=_CONFIG.getint("pgsql", "port"),
    user=_CONFIG.get("pgsql", "user"),
    password=quote_plus(_CONFIG.get("pgsql", "password")),
    db=_CONFIG.get("pgsql", "db"),
    charset=_CONFIG.get("pgsql", "charset"),
    pool_size=_CONFIG.getint("pgsql", "pool_size"),
    max_overflow=_CONFIG.getint("pgsql", "max_overflow"),
    pool_recycle=_CONFIG.getint("pgsql", "pool_recycle"),
    pool_timeout=_CONFIG.getint("pgsql", "pool_timeout"),
    pool_pre_ping=_CONFIG.getboolean("pgsql", "pool_pre_ping"),
    echo=_CONFIG.getboolean("pgsql", "echo"),
    )

RedisConf = DataDict(
    host=_CONFIG.get("redis", "host"),
    port=_CONFIG.getint("redis", "port"),
    db1=_CONFIG.getint("redis", "db1"),
    db2=_CONFIG.getint("redis", "db2"),
    password=_CONFIG.get("redis", "password"),
    expires=_CONFIG.getint("redis", "expires"),
    )

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MySQLConf.user}:{MySQLConf.password}@{MySQLConf.host}:{MySQLConf.port}/{MySQLConf.db}"
SQLALCHEMY_ENGINE_OPTIONS = {  # 给主数据库链接专用的
    "connect_args" : {"charset": MySQLConf.charset},
    "pool_size"    : MySQLConf.pool_size,
    "max_overflow" : MySQLConf.max_overflow,
    "pool_recycle" : MySQLConf.pool_recycle,
    "pool_timeout" : MySQLConf.pool_timeout,
    "pool_pre_ping": MySQLConf.pool_pre_ping,
    "echo"         : MySQLConf.echo,
    }

SQLALCHEMY_ENGINE_OPTIONS_DEFAULT = {  # 数据库连接的默认值，优先级最低
    "json_serializer": lambda obj: json.dumps(obj, ensure_ascii=False),
    "pool_size"      : _CONFIG.get("sqlalchemy", "pool_size"),  # 常驻连接数
    "max_overflow"   : _CONFIG.get("sqlalchemy", "max_overflow"),  # 最大连接数
    "pool_recycle"   : _CONFIG.get("sqlalchemy", "pool_recycle"),  # 每个连接的生存时间
    "pool_timeout"   : _CONFIG.get("sqlalchemy", "pool_timeout"),  # 生成连接的最大等待时间
    "pool_pre_ping"  : _CONFIG.getboolean("sqlalchemy", "pool_pre_ping"),
    "echo"           : _CONFIG.getboolean("sqlalchemy", "echo"),
    }
SQLALCHEMY_TRACK_MODIFICATIONS = _CONFIG.getboolean("sqlalchemy", "track_modifications")
# SQLALCHEMY_COMMIT_ON_TEARDOWN = _CONFIG.getboolean("sqlalchemy", "commit_on_teardown")  # This session is in 'prepared' state
SQLALCHEMY_ECHO = _CONFIG.getboolean("sqlalchemy", "echo")  # sqlalchemy连接的默认值,比默认值高

# flask输出json是否排序
JSON_SORT_KEYS = False
# json格式化格式 flask的debug模式默认启用，需要修改源码
JSONIFY_PRETTYPRINT_REGULAR = False

# cache缓存
CACHE_DEFAULT_TIMEOUT = 60 * 60 * 3
CACHE_THRESHOLD = 1000
CACHE_TYPE = "redis"
CACHE_REDIS_URL = f"redis://:{RedisConf.password}@{RedisConf.host}:{RedisConf.port}/{RedisConf.db2}"

# jwt生存时间
JWT_EXPIRATION_DELTA = 60 * 60 * 12

# 请求来源
RequestFrom = DataDict(
    web=DataDict(key="web", label="web页面"),
    mobile=DataDict(key="mobile", label="小程序"),
    weixin=DataDict(key="weixin", label="weixin小程序"),
    api=DataDict(key="api", label="api接口"),
    )
