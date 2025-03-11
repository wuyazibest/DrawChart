#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : view.py
# @Time    : 2020/8/30 17:30
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc   :
import logging
import os
import uuid

from flask import request, send_file, send_from_directory, render_template
import numpy as np
import pandas as pd

from main.config import BASE_DIR
from main.core import (
    ModelViewSet,
    permission_classes,
    IsLoginPermission,
    IsAdminPermission,
    RequestFromPermission,
    RET,
    ParamError,
    DataError,
    AuthenticationFailed,
    jwt_encode_handler,
    json_resp,
    )
from main.draw_chart.data_source import tiobe, tencent_stock, ifeng_stock
from main.util.common import generate_md5
from main.util.draw import draw_bar, draw_line, draw_timeline

logger = logging.getLogger(__name__)


class TiobeView(ModelViewSet):
    decorators = ()
    resources = "tiobe"
    
    def query_option(self):
        self.resources += "查询"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_args}")
        
        data = [
            {
                "field"  : "chart_type",
                "mean"   : "图形类别",
                "value"  : ["bar", "line", "timeline"],
                "is_must": False,
                "type"   : "str",
                }
            ]
        
        return json_resp(RET.OK, f"{self.resources}成功", data=data)
    
    def get_query(self):
        self.resources += "查询"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_args}")
        params = {x: self.request_args.get(x) for x in self.query_field if self.request_args.get(x, "") != ""}
        
        chart_type = self.request_args.get("chart_type") or "line"
        file_name = chart_type + "_tiobe_chart.html"
        file_path = os.path.join(BASE_DIR, "dist", file_name)
        if os.path.exists(file_path):
            return render_template(file_name)
        
        title = {
            "path"      : file_path,
            "title"     : "开发语言热度",
            "xaxis_name": "语言种类",
            "yaxis_name": "热度",
            }
        
        df = tiobe.get_format_data()
        df = df.replace({np.nan: None})
        
        if chart_type == "bar":
            draw_bar(df.index.values.tolist(), df.to_dict("list"), **title)
        elif chart_type == "line":
            draw_line(df.index.values.tolist(), df.to_dict("list"), **title)
        elif chart_type == "timeline":
            draw_timeline(df.to_dict("index"), **title)
        else:
            raise ParamError("图形类别错误")
        
        return render_template(file_name)


class StockView(ModelViewSet):
    decorators = ()
    resources = "stock"
    query_field = (
        "stock_code",
        "begin_date",
        "end_date",
        "target"
        )
    query_required_field = (
        "stock_code",
        "begin_date",
        "end_date",
        "target"
        )
    data_source_map = {
        "tencent": tencent_stock,
        "ifeng"  : ifeng_stock,
        }
    chart_type_map = {
        "bar"     : draw_bar,
        "line"    : draw_line,
        "timeline": draw_timeline,
        }
    target_map = (
        "open",
        "close",
        "high",
        "low",
        "volume"
        "ys_close",
        "true_range",
        "price_range",
        )
    
    @staticmethod
    def validate_stock_code(stock_code):
        pass
    
    def query_option(self):
        try:
            logger.info(f"{self.resources}查询 user:{self.current_user.username} params:{self.request_args}")
            
            data = [
                {
                    "field"  : "chart_type",
                    "mean"   : "图形类别",
                    "value"  : list(self.chart_type_map),
                    "is_must": False,
                    "type"   : "str",
                    },
                {
                    "field"  : "data_source",
                    "mean"   : "数据源",
                    "value"  : list(self.data_source_map),
                    "is_must": False,
                    "type"   : "str",
                    },
                
                {
                    "field"  : "stock_code",
                    "mean"   : "股票代码-字符串列表-上海sh 深圳sz 香港hk",
                    "value"  : ["600001", "399001"],
                    "is_must": True,
                    "type"   : "list",
                    },
                {
                    "field"  : "begin_date",
                    "mean"   : "查询开始时间",
                    "value"  : "%Y-%m-%d",
                    "is_must": True,
                    "type"   : "str",
                    },
                {
                    "field"  : "end_date",
                    "mean"   : "查询结束时间",
                    "value"  : "%Y-%m-%d",
                    "is_must": True,
                    "type"   : "str",
                    },
                {
                    "field"  : "target",
                    "mean"   : "指标",
                    "value"  : self.target_map,
                    "is_must": True,
                    "type"   : "str",
                    },
                ]
            
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{self.request_args} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    def get_query(self):
        logger.info(f"{self.resources}查询 user:{self.current_user.username} params:{self.request_args}")
        params = {x: self.request_args.get(x) for x in self.query_field if self.request_args.get(x, "") != ""}
        
        if not all([x in params for x in self.query_required_field]):
            raise ParamError("参数缺失")
        
        chart_type = self.request_args.get("chart_type") or "line"
        data_source = self.request_args.get("data_source") or "tencent"
        target = params.get("target")
        
        if chart_type not in self.chart_type_map:
            raise ParamError("参数错误")
        if data_source not in self.data_source_map:
            raise ParamError("参数错误")
        if target not in self.target_map:
            raise ParamError("参数错误")
        
        file_name = generate_md5(f"{chart_type}{data_source}{str(params)}") + "_stock_chart.html"
        file_path = os.path.join(BASE_DIR, "dist", file_name)
        if os.path.exists(file_path):
            return render_template(file_name)
        
        title = {
            "path"      : file_path,
            "title"     : "股票趋势",
            "xaxis_name": "股票",
            "yaxis_name": "数值",
            }
        
        df = self.data_source_map[data_source].batch_request_stock(**params)
        df = df.replace({np.nan: None})
        
        if chart_type == "bar":
            draw_bar(df.index.values.tolist(), df.to_dict("list"), **title)
        elif chart_type == "line":
            draw_line(df.index.values.tolist(), df.to_dict("list"), **title)
        elif chart_type == "timeline":
            draw_timeline(df.to_dict("index"), **title)
        else:
            raise ParamError("图形类别错误")
        
        return render_template(file_name)
