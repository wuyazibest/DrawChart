#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : data_stock.py
# @Time   : 2025/3/9 15:45
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :

def talib_format(fn, *args, **kwargs):
    import talib
    return getattr(talib, fn)(*args, **kwargs)


def format_stock_code(stock_code):
    stock_code = str(stock_code)
    return stock_code if not stock_code[:1].isdecimal() else \
        "sh%s" % stock_code if stock_code[:1] in ["5", "6", "9"] or stock_code[:2] in ["11", "13"] else "sz%s" % stock_code
