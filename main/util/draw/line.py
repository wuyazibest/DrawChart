#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : line.py
# @Time   : 2021/8/10 15:14
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :

from pyecharts.charts import Line
from pyecharts import options as opts

from .base import base_colors, chart_lib, fmt_file_path


def draw_line(
        xaxis,
        row_dict,
        colors=None,
        path="line.html",
        title=None,
        xaxis_name=None,
        yaxis_name=None,
        stack=None,
        ) -> Line:
    """
    :param xaxis:
    ['2001-06-30', '2001-07-30', '2001-08-30', '2001-09-28', '2001-10-26', '2001-11-28', '2001-12-31', '2002-01-30', '2002-02-27', '2002-03-29']
    :param row_dict:
    {
    'Assembly language': [None, None, None, None, None, None, None, None, None, None],
    'C': [20.24, 20.77, 20.75, 20.77, 19.75, 19.21, 20.14, 18.83, 19.89, 19.85],
    'C#': [0.38, 0.43, 0.38, 0.39, 0.42, 0.76, 0.59, 0.62, 0.74, 0.74],
    'C++': [14.2, 16.11, 16.12, 15.85, 16.1, 15.67, 14.96, 15.18, 15.54, 15.91],
    'Java': [26.49, 25.03, 24.66, 24.82, 25.68, 24.37, 24.2, 24.06, 24.01, 24.41],
    'JavaScript': [1.55, 1.72, 1.66, 1.63, 1.51, 1.47, 1.46, 2.73, 1.48, 1.47],
    'PHP': [1.9, 1.38, 1.55, 1.55, 1.78, 4.87, 7.27, 8.27, 7.44, 7.03],
    'Python': [1.25, 1.13, 1.2, 1.17, 1.28, 1.23, 1.04, 1.02, 0.99, 0.99],
    'SQL': [2.96, 2.77, 2.38, 2.36, 2.24, 1.84, 1.87, 1.94, 2.09, 2.06],
    'Visual Basic': [None, None, None, None, None, None, None, None, None, None]
    }
    :param colors:
    :param path:
    :param title:
    :param xaxis_name:
    :param yaxis_name:
    :param stack:
    :return:
    """
    colors_raw = colors or base_colors
    color = colors_raw.copy()
    color.reverse()
    graph = chart_lib("line")
    graph.add_xaxis(xaxis)
    
    for k, row in row_dict.items():
        graph.add_yaxis(
            k, row,
            color=color.pop() if color else None,
            is_symbol_show=False,  # 线上的小圆点
            is_connect_nones=False,  # 连接空数据
            is_smooth=True,  # 是否平滑
            is_step=False,
            is_hover_animation=True,
            stack=stack
            )
    
    graph.set_series_opts(
        label_opts=opts.LabelOpts(is_show=False),  # 线上的数字标签
        linestyle_opts=opts.LineStyleOpts(width=4, opacity=0.8, curve=0),  # 可以放在add_yaxis中单独设置每条线
        markline_opts=opts.MarkLineOpts(  # 标记线数据
            data=[opts.MarkLineItem(x=x) for x in xaxis if "00:00:00" in x],
            label_opts=opts.LabelOpts(),
            linestyle_opts=opts.LineStyleOpts(type_="dashed", color="#d3d3d3", )
            ),
        )
    graph.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        legend_opts=opts.LegendOpts(orient="vertical", pos_left="right", pos_top="middle"),
        tooltip_opts=opts.TooltipOpts(is_show=True, trigger="axis", axis_pointer_type="cross"),
        xaxis_opts=opts.AxisOpts(name=xaxis_name,
                                 # axislabel_opts={"interval": "2"},
                                 max_="dataMax"),
        yaxis_opts=opts.AxisOpts(name=yaxis_name),
        )
    graph.render(fmt_file_path(path))
    return graph
