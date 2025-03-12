#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : nmdis.py
# @Time   : 2024/12/19 14:48
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   : 国家海洋科学数据中心
import datetime
import json
import logging
import os
import time
import requests
import numpy as np
import pandas as pd

from main.util.common import parse_url

logger = logging.getLogger(__name__)


class NmdisStock:
    def __init__(self, headers=None):
        self.headers = headers or {
            "Content-Type": "application/json",
            "user-agent"  : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
            }
        self.sitecode_map = {
            "T140": "蛇口（赤湾）"
            }
        self.data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chaoxi_data.xlsx")
    
    def get_daily_data(self, date, sitecode):
        ret = {}
        url = "https://mds.nmdis.org.cn/service/rdata/front/knowledge/chaoxidata/list"
        payload = {
            "serchdate": date,  # "2024-12-20",
            "sitecode" : sitecode  # "T140"
            }
        resp = parse_url(url, method="POST", json=payload, headers=self.headers)
        data = resp.get("data")
        if data:
            ret = self.format_data(data[0])
        
        return ret
    
    def format_data(self, raw_data):
        data = {}
        sitecode = raw_data.get("sitecode")
        title = raw_data.get("title")
        serchdate = raw_data.get("serchdate")
        filedata = raw_data.get("filedata", {})
        for k, v in filedata.items():
            if k.startswith("a"):
                data[f"{serchdate} {int(k.lstrip('a')):02}:00:00"] = v
        
        return dict(sorted(data.items(), key=lambda x: x[0]))
    
    def get_monthly_data(self, sitecode="T140"):
        ret = {}
        today = datetime.datetime.now()
        for i in range(30):
            next_day = today + datetime.timedelta(i)
            next_day_str = next_day.strftime("%Y-%m-%d")
            ret.update(self.get_daily_data(next_day_str, sitecode))
        
        return {self.sitecode_map[sitecode]: ret}
    
    def save_data(self):
        pass


def get_fmt_data():
    ns = NmdisStock()
    pd.set_option('display.float_format', lambda x: str(x))
    
    if os.path.exists(ns.data_path):
        df = pd.read_excel(ns.data_path, index_col=0, header=0, engine="openpyxl")
    else:
        df_dict = ns.get_monthly_data()
        df = pd.DataFrame.from_dict(df_dict)
        df.to_excel(ns.data_path, encoding="utf8")
    
    return df


if __name__ == '__main__':
    res = get_fmt_data()
    print(res)
