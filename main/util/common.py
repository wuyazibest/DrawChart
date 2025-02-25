#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : common.py
# @Time    : 2020/8/30 15:32
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import hashlib
import logging
import datetime
import re
import redis
import time
import requests

from flask import jsonify, request, json
from jsonschema import validate
from openpyxl import Workbook
from retrying import retry

from main import config

logger = logging.getLogger(__name__)


class Pager(object):
    def __init__(self, object_list, limit):
        self.object_list = object_list
        self.limit = int(limit)
        self.total = len(self.object_list)
    
    def page(self, offset):
        try:
            if not (isinstance(offset, int) or offset.isdecimail()):
                offset = 1
            else:
                offset = int(offset)
            
            bottom = (offset - 1) * self.limit
            top = bottom + self.limit
            if not self.total:
                return []
            if bottom < 0:
                ret = self.object_list[0:self.limit]
            else:
                ret = self.object_list[bottom:top]
        except Exception as e:
            logger.error(f"分页查询出错 error: {e} {self.object_list[0]}")
            ret = self.object_list[0:self.limit]
        
        return ret


@retry(stop_max_attempt_number=2)
def _parse_url(method, url, **kwargs):
    if method.upper() in ["GET"]:
        kwargs.setdefault('allow_redirects', True)
    tt = time.time()
    resp = requests.request(method, url, **kwargs)
    logger.debug(f">>>> time:{(time.time() - tt):.3f} url: {method} {resp.url}")
    if resp.status_code != 200:
        raise Exception(resp.text)
    return resp


def __parse_url(method, url, **kwargs):
    if method.upper() in ["GET"]:
        kwargs.setdefault('allow_redirects', True)
    tt = time.time()
    resp = requests.request(method, url, **kwargs)
    logger.debug(f">>>> time:{(time.time() - tt):.3f} url: {method} {resp.url}")
    if resp.status_code != 200:
        raise Exception(resp.text)
    return resp


def parse_url(url, method="GET", ret_json=True, raise_exception=False, timeout=10, max_retry=2, **kwargs):
    """
    kwargs:
    headers  请求头
    params   请求参数
    data     请求体参数
    json     请求体参数，转换为json格式
    cookies  cookie
    """
    try:
        # resp = _parse_url(method, url, timeout=timeout, **kwargs)
        resp = retry(stop_max_attempt_number=max_retry)(__parse_url)(method, url, timeout=timeout, **kwargs)
        return resp.json() if ret_json else resp.text
    except Exception as e:
        msg = f"请求失败 {method} {url} kwargs:{json.dumps(kwargs, ensure_ascii=False)} error:{e}"
        logger.error(msg)
        if raise_exception:
            raise Exception(msg)
        else:
            return {} if ret_json else ""


def get_request_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        request_ip = x_forwarded_for.split(",")[0]
    else:
        request_ip = request.META.get("REMOTE_ADDR")
    return request_ip


def check_json(instance, schema):
    try:
        validate(instance, schema, types=dict(array=(list, tuple)))
        return True
    except Exception as e:
        logger.error(f"json数据校验失败  {instance}   error: %s" % e)
        return False


def check_datetime_fmt(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        return datetime.datetime.strptime(date_str, fmt)
    except:
        return False


def generate_md5(s, encoding="utf-8"):
    return str(hashlib.md5(s.encode(encoding)).hexdigest())


def get_now_time(fmt="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(fmt)


def get_datetime_obj(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        return datetime.datetime.strptime(date_str, fmt)
    except:
        return False


def get_datetime_str(date_obj, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        return datetime.datetime.strftime(date_obj, fmt)
    except:
        return ""


def get_timestamp(date_str, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        return time.mktime(time.strptime(date_str, fmt))
    except:
        return ""


def make_cache_key(*args, **kwargs):
    """
    自定义缓存key生成规则：
    根据请求路径和所有请求参数的不同而分别缓存
    """
    args_as_sorted_tuple = tuple(sorted((pair for pair in request.args.items(multi=True))))
    args_as_bytes = str(args_as_sorted_tuple).encode()
    
    cache_hash = hashlib.md5()
    cache_hash.update(args_as_bytes)
    cache_hash.update(request.data)
    cache_hash = str(cache_hash.hexdigest())
    cache_key = request.path + cache_hash
    return cache_key


def _param_escape(s, re_escape=re.compile(r"([\\'])")):
    """ 清洗sql参数,解决sql注入问题
    """
    if s is None:
        return "null"
    
    s = re_escape.sub(r'\\\1', str(s))
    return f"'{s}'"


def generate_virtual_excel(data_list, file_name, table_head=(), table_head_ch=()):
    exl = Workbook()
    sheet = exl.active
    
    if table_head_ch: sheet.append(table_head_ch)
    if table_head: sheet.append(table_head)
    for data in data_list:
        if isinstance(data, dict):
            row = [str(data.get(x)) for x in table_head]
        else:
            row = data
        sheet.append(row)
    
    if os.path.splitext(file_name)[1] != ".xlsx":
        file_name += ".xlsx"
    # vir_exl = save_virtual_workbook(exl)  # 新版本不支持
    with io.BytesIO() as buffer:
        exl.save(buffer)
        vir_exl = buffer.getvalue()
    return file_name, vir_exl


def type_convergence(primary, param):
    """ 试图将目标参数类型转换到一致
    """
    primary_type = type(primary)
    try:
        param = primary_type(param)
    except:
        pass
    return primary, param
