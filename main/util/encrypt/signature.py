#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : signature.py
# @Time   : 2020/12/24 14:47
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   : 签名

import json
import time
import uuid
from Crypto.Hash import HMAC, SHA256


def generate_sign(data, secret_key, digestmod=None, code_type="utf-8"):
    service = HMAC.new(secret_key.encode(code_type), digestmod=digestmod or SHA256)
    # 部分语言，json的冒号 ：后面不带空格，python默认带空格，会造成签名认证失败
    service.update(json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(code_type))
    return service.hexdigest()


def attach_sign(data, secret_key=None, sign_key="authorization", prefix="", digestmod=None):
    if sign_key in data:
        raise Exception("参数错误：数据中不能含有键sign_key")
    
    nonce = uuid.uuid4().hex
    if "timestamp" not in data:
        data["timestamp"] = int(time.time())
    data["nonce"] = nonce
    secret_key = secret_key or nonce
    data[sign_key] = prefix + generate_sign(data, secret_key, digestmod=digestmod)
    return data


def verify_sign(data, signature, secret_key=None, digestmod=None, code_type="utf-8"):
    if any([x not in data for x in {"nonce"}]):
        raise Exception("参数缺失")
    
    secret_key = secret_key or data["nonce"]
    service = HMAC.new(secret_key.encode(code_type), digestmod=digestmod or SHA256)
    service.update(json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(code_type))
    try:
        service.hexverify(signature)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    secret_id = "secret_id"
    secret_key = "secret_key"
    data = {
        "code": "0",
        "msg": "成功",
        "desc": "查询用户成功",
        "data": {"user": "aa"}
        }
    data = attach_sign(data, secret_key=secret_key, prefix=f"api {secret_id} ")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    auth = data.pop("authorization")
    auth = auth.split()
    print(verify_sign(data, auth[2], secret_key))
