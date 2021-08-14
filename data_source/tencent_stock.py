#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : tencent_stock.py
# @Time   : 2021/8/12 10:47
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :

import json
import logging
import time
import numpy as np
import pandas as pd

from util.common import parse_url, talib_format

logger = logging.getLogger(__name__)


class TencentStock:
    columns = ["date", "open", "close", "high", "low", "volume"]
    
    def __init__(self, headers=None, columns=None):
        self.headers = headers or {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
            }
        self.columns = columns or self.columns
    
    def get_daily_data(self,
                       stock_code,
                       cycle="day",
                       begin_date="",
                       end_date="",
                       date_num=100,
                       fq_type="qfd",
                       **kwargs):
        """
        :param stock_code:
        :param cycle:
        :param begin_date:
        :param end_date:
        :param date_num:
        :param fq_type:
        :param kwargs:
        :return:
         [
            "2021-03-10",// 0-交易日
            "1977.000",// 1-开盘价
            "1970.010",// 2-收盘价
            "1999.870",// 3-最高价
            "1967.000",// 4-最低价
            "51172.000"// 5-总手
        ]
        """
        
        # url = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get"
        url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        stock_code = stock_code  # usAAPL.OQ 股票代码，这里是us是美股，AAPL是苹果，“.OQ”是美股拼接后缀，其他不需要拼接
        cycle = cycle
        begin_date = begin_date  # 从结束时间倒退，如果没有超过开始时间，则返回限制的天数，如果超过，则返回日期限制
        end_date = end_date
        date_num = date_num
        fq_type = fq_type
        params = f"param={stock_code},{cycle},{begin_date},{end_date},{date_num},{fq_type}"
        resp = parse_url(url, params=params, headers=self.headers, **kwargs)
        
        if resp.get("code") is not 0:
            logger.error(resp.get("msg", ""))
        
        return resp.get("data", {}).get(stock_code, {}).get(cycle, [])
    
    def format_data(self, data):
        df = pd.DataFrame(data, columns=self.columns)
        df = df.set_index("date")
        df = df.astype(float)
        # 星期数
        df["week"] = pd.to_datetime(df.index).weekday + 1
        
        return df


def request_stock(stock_code, begin_date, end_date, target=None, **kwargs):
    pd.set_option('display.float_format', lambda x: str(x))
    ts = TencentStock()
    data = ts.get_daily_data(stock_code=stock_code, begin_date=begin_date, end_date=end_date, **kwargs)
    if not data:
        return pd.DataFrame([])
    
    df = ts.format_data(data)
    
    columns_name = [
        *ts.columns,
        "week",
        "ys_close",
        "true_range",
        "price_range",
        ]
    # 昨日收盘价
    df["ys_close"] = df["close"].shift(1)
    # 真实波幅
    df["true_range"] = talib_format("TRANGE", df["high"], df["low"], df["close"]) / df[["close", "low"]].min(axis=1) * 100
    # 涨跌幅
    df["price_range"] = (df["close"] - df["ys_close"]) / df["ys_close"] * 100
    # 保留小数位
    df = df.round(2)
    # 填充nan
    # df = df.fillna(0)
    # df = df.replace({np.nan: None})
    
    if target and target in columns_name:
        df = df[[target]]
        df = df.rename(columns={target: stock_code})
    
    return df


def batch_request_stock(stock_code, begin_date, end_date, target, **kwargs):
    df = pd.DataFrame([])
    for i in stock_code:
        df = pd.concat([df, request_stock(i, begin_date, end_date, target, **kwargs)], join='outer', axis=1)
    
    return df


if __name__ == '__main__':
    # ret = request_stock(stock_code="sh000001", begin_date="2021-04-01", end_date="2021-04-15", date_num=100)
    # print(ret)
    
    ret = batch_request_stock(stock_code=["sh601318", "sh601238", "sh688981"], begin_date="2021-04-01", end_date="2021-04-15",
                              target="price_range")
    print(ret)
