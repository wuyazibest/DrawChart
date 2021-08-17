#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : config.py
# @Time    : 2020/8/30 15:31
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import base64
import configparser
import os

from main.constant import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_ENV = os.getenv('SERVER_ENV')
_CONFIG = configparser.ConfigParser()
_CONFIG.read(os.path.join(BASE_DIR, "conf/config.ini"), encoding='utf-8')


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
        conf_name = "conf/conf_online.ini"
        conf_online = cls.get_conf()
        if conf_online:
            with open(conf_name, "w+", encoding="utf-8") as f:
                f.write(conf_online)
            
            _CONFIG.read(os.path.join(BASE_DIR, conf_name), encoding="utf-8")


# 使用配置中心的配置覆盖本地配置
if _CONFIG.getboolean("nacos", "start"):
    Nacos.update_conf()
DEBUG = _CONFIG.getboolean("default", "debug")
# 当多服务端做冗余的时候此值需要设置为固定值
SECRET_KEY = bytes.decode(base64.b64encode(os.urandom(48)))


class MySQLConf:
    host = _CONFIG.get("mysql", "host")
    port = _CONFIG.getint("mysql", "port")
    user = _CONFIG.get("mysql", "user")
    password = _CONFIG.get("mysql", "password")
    db = _CONFIG.get("mysql", "db")
    charset = _CONFIG.get("mysql", "charset")
    maxconnections = _CONFIG.getint("mysql", "maxconnections")


class PgSQLConf:
    host = _CONFIG.get("pgsql", "host")
    port = _CONFIG.getint("pgsql", "port")
    user = _CONFIG.get("pgsql", "user")
    password = _CONFIG.get("pgsql", "password")
    db = _CONFIG.get("pgsql", "db")
    charset = _CONFIG.get("pgsql", "charset")
    maxconnections = _CONFIG.getint("pgsql", "maxconnections")
    pool_recycle = _CONFIG.getint("pgsql", "pool_recycle")
    pool_size = _CONFIG.getint("pgsql", "pool_size")


class RedisConf:
    host = _CONFIG.get("redis", "host")
    port = _CONFIG.getint("redis", "port")
    db1 = _CONFIG.getint("redis", "db1")
    db2 = _CONFIG.getint("redis", "db2")
    password = _CONFIG.get("redis", "password")
    expires = _CONFIG.getint("redis", "expires")


SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MySQLConf.user}:{MySQLConf.password}@{MySQLConf.host}:{MySQLConf.port}/{MySQLConf.db}"
SQLALCHEMY_BINDS = {
    # "management": f"mysql+pymysql://{MySQLConf.user}:{MySQLConf.password}@{MySQLConf.host}:{MySQLConf.port}/management",
    # "sqlite_db": f"sqlite:{BASE_DIR}/lib/sqlite_db.db",
    # "pgsql_db": f":postgresql//{PgSQLConf.user}:{PgSQLConf.password}@{PgSQLConf.host}:{PgSQLConf.port}/{PgSQLConf.db}",
    }
SQLALCHEMY_TRACK_MODIFICATIONS = _CONFIG.getboolean("sqlalchemy", "track_modifications")
SQLALCHEMY_COMMIT_ON_TEARDOWN = _CONFIG.getboolean("sqlalchemy", "commit_on_teardown")
SQLALCHEMY_ECHO = _CONFIG.getboolean("sqlalchemy", "echo")

LOG_LEVEL = _CONFIG.get("log", "level")
# flask输出json是否排序
JSON_SORT_KEYS = False
# 中文编码
JSON_AS_ASCII = False
# json格式化格式 flask的debug模式默认启用，需要修改源码
JSONIFY_PRETTYPRINT_REGULAR = False

# cache缓存
CACHE_DEFAULT_TIMEOUT = 60 * 60 * 3
CACHE_THRESHOLD = 1000
CACHE_TYPE = "redis"
CACHE_REDIS_URL = f"redis://:{RedisConf.password}@{RedisConf.host}:{RedisConf.port}/{RedisConf.db2}"


class EChart:
    file_path = os.path.join(BASE_DIR, "dist")
    width = "90%"
    height = "90%"
    page_title = "DrawChart"
    theme = "white"
    js_host = "/static/pyecharts-assets-master/assets/"
