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
import simplejson
from flask import jsonify, request, json
from jsonschema import validate
from retrying import retry

from main import config

from .response_code import RET, error_map

logger = logging.getLogger(__name__)


class JSONEncoder(simplejson.JSONEncoder):
    """
    不能同时继承simplejson.JSONEncoder和json.JSONEncoder  在itsdangerous<2.0 是出现继承错误
    """
    
    def default(self, o):
        # 强制调用json.JSONEncoder的方法
        return json.JSONEncoder().default(o)


def norm_data(code, desc=None, data=None, **kwargs):
    kwargs["code"] = code if code in error_map else RET.UNKOWNERR
    kwargs["msg"] = error_map.get(code, "未知消息")
    kwargs["desc"] = desc or error_map.get(code, "未知消息")
    kwargs["data"] = data
    return kwargs


def json_resp(code, desc=None, data=None, **kwargs):
    return jsonify(norm_data(code, desc=desc, data=data, **kwargs))


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
def parse_url(url, method="GET", raise_exception=False, timeout=10, **kwargs):
    try:
        if method.upper() in ["GET"]:
            kwargs.setdefault('allow_redirects', True)
        tt = time.time()
        resp = requests.request(method, url, timeout=timeout, **kwargs)
        logger.debug(f">>>> time:{(time.time() - tt):.3f} url: {method} {resp.url}")
        if resp.status_code != 200:
            raise Exception(resp.content.decode())
        return resp.json()
    except Exception as e:
        msg = f"地址请求失败 {method} {url} kwargs:{json.dumps(kwargs, ensure_ascii=False)} error:{e}"
        logger.error(msg)
        if raise_exception:
            raise Exception(msg)
        else:
            return {}


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


def talib_format(fn, *args, **kwargs):
    import talib
    return getattr(talib, fn)(*args, **kwargs)


def check_is_mobile(request):
    """
    # 判断网站来自mobile还是pc
    :param request:
    :return:
    """
    userAgent = request.headers['User-Agent']  # flask
    # userAgent = request.META.get("HTTP_USER_AGENT")  # django
    # userAgent = env.get('HTTP_USER_AGENT')
    
    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|' \
                    r'midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|' \
                    r'treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
    
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|' \
                     r'an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|' \
                     r'bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|' \
                     r'da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|' \
                     r'ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|' \
                     r'hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|' \
                     r'i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|' \
                     r'kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|' \
                     r'm1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|' \
                     r'do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|' \
                     r'ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|' \
                     r'pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|' \
                     r'qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|' \
                     r'sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|' \
                     r'sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|' \
                     r'tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|' \
                     r'vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|' \
                     r'wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    
    _short_matches = re.compile(_short_matches, re.IGNORECASE)
    
    if _long_matches.search(userAgent) is not None:
        return True
    user_agent = userAgent[0:4]
    if _short_matches.search(user_agent) is not None:
        return True
    return False
