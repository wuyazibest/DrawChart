#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : base.py
# @Time   : 2021/8/10 15:11
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from importlib import import_module

from pyecharts.charts import Bar, Timeline, Line
from pyecharts import options as opts

from main.config import EChart

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

initopts = opts.InitOpts(
    # width="1600px",
    # height="800px",
    width=EChart.width,
    height=EChart.height,
    chart_id=None,
    page_title=EChart.page_title,
    theme="white",
    bg_color=None,
    js_host=EChart.js_host,
    )


def chart_lib(chart_type):
    if chart_type == "bar":
        return Bar(initopts)
    elif chart_type == "line":
        return Line(initopts)
    elif chart_type == "timeline":
        return Timeline(initopts)
