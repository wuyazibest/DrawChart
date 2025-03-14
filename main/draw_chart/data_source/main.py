#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : main.py
# @Time   : 2021/8/14 10:31
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from main.draw_chart.data_source import tiobe, tencent_stock
from main.util.draw import draw_bar, draw_line, draw_timeline


def draw_tiobe():
    title = {
        # "path": "bar.html",
        "title"     : "开发语言热度",
        "xaxis_name": "语言种类",
        "yaxis_name": "热度",
        }
    
    df = tiobe.get_format_data()
    df = df.replace({np.nan: None})
    draw_bar(df.index.values.tolist(), df.to_dict("list"), path="test/bar.html", **title)
    draw_line(df.index.values.tolist(), df.to_dict("list"), path="test/line.html", **title)
    draw_timeline(df.to_dict("index"), path="test/timeline.html", **title)


def draw_tencent_stock():
    title = {
        # "path": "bar.html",
        "title"     : "股票趋势",
        "xaxis_name": "股票",
        "yaxis_name": "数值",
        }
    
    df = tencent_stock.batch_request_stock(stock_code=["sh601318", "sh601238", "sh688981"],
                                           begin_date="2021-04-01",
                                           end_date="2021-04-15",
                                           target="price_range")
    df = df.replace({np.nan: None})
    draw_bar(df.index.values.tolist(), df.to_dict("list"), path="test/bar.html", **title)
    draw_line(df.index.values.tolist(), df.to_dict("list"), path="test/line.html", **title)
    draw_timeline(df.to_dict("index"), path="test/timeline.html", **title)


if __name__ == '__main__':
    draw_tiobe()
    # draw_tencent_stock()
