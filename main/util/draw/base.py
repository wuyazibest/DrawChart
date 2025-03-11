#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : base.py
# @Time   : 2021/8/10 15:11
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import os

from pyecharts.charts import Bar, Timeline, Line
from pyecharts import options

from main.config import BASE_DIR

color_function = """
        function (params) {
            if (params.value < 1)
                return 'green';
            else if (params.value > 1 && params.value < 2)
                return '#0000ff';
            else return 'red';
        }
        """

base_colors = [
    "#00CD00",
    "#000000",
    "#00BFFF",
    "#8B864E",
    "#FF1493",
    "#0000CD",
    "#FFD700",
    "#008000",
    "#FF4500",
    "#00FA9A",
    "#6495ED",
    "#191970",
    "#9932CC",
    ]

initopts = options.InitOpts(
    # width="1600px",
    # height="800px",
    width="90%",
    height="90%",
    chart_id=None,
    page_title="DrawChart",
    theme="white",
    bg_color=None,
    # js_host=os.path.join(BASE_DIR, "dist/pyecharts-assets-master/assets/"),
    )


def chart_lib(chart_type):
    if chart_type == "bar":
        return Bar(initopts)
    elif chart_type == "line":
        return Line(initopts)
    elif chart_type == "timeline":
        return Timeline(initopts)


def fmt_file_path(path):
    if os.path.splitext(path)[1] != ".html":
        path += ".html"
    
    if not path.startswith(BASE_DIR):
        path = os.path.join(BASE_DIR, "dist", path.lstrip("/"))
    
    if os.path.exists(path):
        os.remove(path)
    else:
        dirpath = os.path.dirname(path)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
    
    return path
