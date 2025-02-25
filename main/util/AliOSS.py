#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : AliOSS.py
# @Time   : 2022/6/13 13:54
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import base64
import datetime
import hashlib
import hmac
import json
import logging
import concurrent.futures
import os
import shutil
import time

import oss2

from main.config import ALiOSSConf

logger = logging.getLogger(__name__)


class ALiOSS:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        cls._instance = cls._instance or super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.AccessKeyID = ALiOSSConf.AccessKeyID
        self.AccessKeySecret = ALiOSSConf.AccessKeySecret
        self.Bucket = ALiOSSConf.Bucket
        self.Endpoint = "https://oss-cn-shenzhen.aliyuncs.com"
    
    @property
    def oss_auth(self):
        return oss2.Auth(self.AccessKeyID, self.AccessKeySecret)
    
    @property
    def oss_bucket(self):
        self._oss_bucket = self._oss_bucket if hasattr(self, "_oss_bucket") else oss2.Bucket(self.oss_auth, self.Endpoint, self.Bucket)
        return self._oss_bucket
    
    @property
    def oss_service(self):
        self._oss_service = self._oss_service if hasattr(self, "_oss_service") else oss2.Service(self.oss_auth, self.Endpoint)
        return self._oss_service
    
    def put_str(self, oss_path, s):
        self.oss_bucket.put_object(oss_path, s)
    
    def batch_put_str(self, path_dict):
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            for oss_path, s in path_dict.items():
                future = executor.submit(self.put_str, oss_path, s)
    
    def get_str(self, oss_path):
        object_stream = self.oss_bucket.get_object(oss_path)
        ret = object_stream.read().decode("utf-8")
        if object_stream.client_crc != object_stream.server_crc:
            raise Exception("The CRC checksum between client and server is inconsistent!")
        return ret
    
    def list_directory(self, oss_dir):
        ret = []
        for obj in oss2.ObjectIteratorV2(self.oss_bucket, prefix=oss_dir):
            ret.append(obj.key)
        return ret
    
    def get_dir_str(self, oss_dir):
        ret = []
        list_directory = self.list_directory(oss_dir) if isinstance(oss_dir, str) else set(oss_dir)
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            ft = {}
            for oss_path in list_directory:
                future = executor.submit(self.get_str, oss_path)
                ft[future] = oss_path
            
            for i in concurrent.futures.as_completed(ft):
                ret.append({ft[i]: i.result()})
        
        return ret
    
    def delete_dir(self, oss_dir):
        for oss_path in self.list_directory(oss_dir):
            self.oss_bucket.delete_object(oss_path)
    
    def download_file(self, file_name, oss_path):
        try:
            file_name = file_name + "_" + os.path.split(oss_path)[1]
            dir_path = "F:/PyDev/exercise/car_img"
            file_path = os.path.join(dir_path, file_name)
            
            if os.path.exists(file_path):
                return
            
            object_stream = self.oss_bucket.get_object(oss_path)
            with open(file_path, 'wb') as local_fileobj:
                shutil.copyfileobj(object_stream, local_fileobj)
            
            print(file_name)
            return file_name
        except Exception as e:
            print(file_name, e)
    
    def generate_temporary_url(self, path, ex=60 * 60):
        """
        临时授权访问
        """
        return self.oss_bucket.sign_url("GET", path, ex, slash_safe=True)


def object_exists(oss_path):
    try:
        oss_path = oss_path.replace(ALiOSSConf.Domain + "/", "", 1)
        oss = ALiOSS()
        return oss.oss_bucket.object_exists(oss_path)
    except Exception as e:
        logger.error(f"查询oss文件失败： {e}")


def delete_file(oss_path):
    try:
        oss_path = oss_path.replace(ALiOSSConf.Domain + "/", "", 1)
        oss = ALiOSS()
        oss.delete_dir(oss_path)
        return True
    except Exception as e:
        logger.error(f"删除oss文件失败： {e}")


def put_file(oss_path, s):
    try:
        oss_path = oss_path.replace(ALiOSSConf.Domain + "/", "", 1)
        oss = ALiOSS()
        oss.put_str(oss_path, s)
        return True
    except Exception as e:
        logger.error(f"上传文件到oss失败： {e}")


def batch_put_str(path_dict):
    try:
        oss = ALiOSS()
        oss.batch_put_str(path_dict)
        return True
    except Exception as e:
        logger.error(f"批量上传到oss失败： {e}")


def get_dir_str(oss_dir):
    try:
        oss = ALiOSS()
        return oss.get_dir_str(oss_dir)
    except Exception as e:
        logger.error(f"批量下载文件失败： {e}")
        return []


def get_weixin_upload_sign(file_path):
    access_key_id = ALiOSSConf.AccessKeyID
    access_key_secret = ALiOSSConf.AccessKeySecret
    host = ALiOSSConf.Domain
    upload_dir = file_path
    expire_time = 60 * 60
    
    def get_iso_8601(expire):
        gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
        gmt += 'Z'
        return gmt
    
    expire = get_iso_8601(int(time.time()) + expire_time)
    
    policy_dict = dict()
    policy_dict['expiration'] = expire
    policy_dict['conditions'] = [['starts-with', '$key', upload_dir]]
    
    policy = base64.b64encode(json.dumps(policy_dict).strip().encode())
    sign = hmac.new(access_key_secret.encode(), policy, hashlib.sha1).digest()
    sign_str = base64.encodebytes(sign).strip().decode()
    
    token_dict = dict()
    token_dict['host'] = host
    token_dict['access_id'] = access_key_id
    token_dict['policy'] = policy.decode()
    token_dict['signature'] = sign_str
    token_dict['oss_path'] = upload_dir
    
    return token_dict


if __name__ == '__main__':
    # oss = ALiOSS()
    # print(oss_obj.list_directory(""))
    # oss_obj.put_str(
    #     f"credentials/1111.txt",
    #     json.dumps([{"test": "1111111111111"}, {"test": 11111111111111}])
    #     )
    
    # print(oss.get_str(f"aliNLS/{datetime.datetime.now().strftime('%Y%m%d')}/1111111111"))
    
    # url = oss.generate_temporary_url("credentials/20240821175803000000007/20240822_120408.jpg", )
    # print(url)
    ret = get_weixin_upload_sign("")
    print(ret)
