#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : bar.py
# @Time   : 2021/8/10 15:15
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
from pyecharts.charts import Bar
from pyecharts import options as opts

from .base import base_colors, color_function, chart_lib


def draw_bar(xaxis,
             row_dict,
             colors=None,
             path="dist/bar.html",
             title=None,
             xaxis_name=None,
             yaxis_name=None,
             stack=None,
             ) -> Bar:
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
    colors = colors or base_colors
    graph = chart_lib("bar")
    graph.add_xaxis(xaxis)
    
    for index, (k, row) in enumerate(row_dict.items()):
        graph.add_yaxis(
            k, row,
            color=colors[index] if len(colors) > index else None,
            stack=stack,
            # itemstyle_opts=opts.ItemStyleOpts(color=JsCode(color_function)),  # 使用js来控制颜色
            )
    
    graph.set_global_opts(title_opts=opts.TitleOpts(title=title),
                          tooltip_opts=opts.TooltipOpts(is_show=True, trigger="axis", axis_pointer_type="shadow"),
                          xaxis_opts=opts.AxisOpts(name=xaxis_name, axislabel_opts={"interval": "0"}),
                          yaxis_opts=opts.AxisOpts(name=yaxis_name))
    graph.render(path)
    return graph


def draw_single_bar(
        data_dict,
        colors=None,
        path="dist/bar_single.html",
        title=None,
        xaxis_name=None,
        yaxis_name=None,
        reversal_axis=False,
        max_columns=None,
        ) -> Bar:
    """
    
    :param data_dict:
    {
    'Assembly language': None,
    'C': 20.14,
    'C#': 0.59,
    'C++': 14.96,
    'Java': 24.2,
    'JavaScript': 1.46,
    'PHP': 7.27,
    'Python': 1.04,
    'SQL': 1.87,
    'Visual Basic': None
    }
    :param colors:
    :param path:
    :param title:
    :param xaxis_name:
    :param yaxis_name:
    :param reversal_axis:
    :param max_columns: 最大显示柱子数
    :return:
    """
    colors = colors or base_colors
    # 数据重新排序后颜色如果不使用字典，一种颜色对应的数据列会改变
    data_colors = {k: colors[index] if len(colors) > index else None for index, k in enumerate(data_dict)}
    graph = chart_lib("bar")
    max_columns = max_columns or len(data_dict)
    data_dict = dict(sorted(data_dict.items(), key=lambda x: x[1] or 0)[-max_columns:])
    
    graph.add_xaxis(list(data_dict.keys()))
    
    y_axis = []
    for k, v in data_dict.items():
        y_axis.append(opts.BarItem(
            name=k,
            value=v,
            itemstyle_opts=opts.ItemStyleOpts(color=data_colors[k])
            ))
    graph.add_yaxis("", y_axis=y_axis)
    if reversal_axis:
        graph.set_series_opts(
            label_opts=opts.LabelOpts(position="right"),  # 线上的标签
            )
        xaxis_name, yaxis_name = yaxis_name, xaxis_name
        graph.reversal_axis()  # 翻转xy
    
    graph.set_global_opts(title_opts=opts.TitleOpts(title=title, pos_left="center"),
                          tooltip_opts=opts.TooltipOpts(is_show=True, trigger="axis", axis_pointer_type="shadow"),
                          xaxis_opts=opts.AxisOpts(name=xaxis_name, axislabel_opts={"interval": "0"}),
                          yaxis_opts=opts.AxisOpts(name=yaxis_name))
    # graph.render(path)
    return graph
