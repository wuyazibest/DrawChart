#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : timeline.py
# @Time   : 2021/8/10 15:14
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :

from pyecharts import options as opts

from .bar import draw_single_bar
from .base import base_colors, chart_lib


def draw_timeline(
        df_dict,
        path="dist/timeline.html",
        title=None,
        xaxis_name=None,
        yaxis_name=None,
        ):
    """
    
    :param df_dict:
    {
    '2001-06-30': {'Assembly language': None, 'C': 20.24, 'C#': 0.38, 'C++': 14.2, 'Java': 26.49, 'JavaScript': 1.55, 'PHP': 1.9, 'Python': 1.25, 'SQL': 2.96, 'Visual Basic': None},
    '2001-07-30': {'Assembly language': None, 'C': 20.77, 'C#': 0.43, 'C++': 16.11, 'Java': 25.03, 'JavaScript': 1.72, 'PHP': 1.38, 'Python': 1.13, 'SQL': 2.77, 'Visual Basic': None},
    '2001-08-30': {'Assembly language': None, 'C': 20.75, 'C#': 0.38, 'C++': 16.12, 'Java': 24.66, 'JavaScript': 1.66, 'PHP': 1.55, 'Python': 1.2, 'SQL': 2.38, 'Visual Basic': None},
    '2001-09-28': {'Assembly language': None, 'C': 20.77, 'C#': 0.39, 'C++': 15.85, 'Java': 24.82, 'JavaScript': 1.63, 'PHP': 1.55, 'Python': 1.17, 'SQL': 2.36, 'Visual Basic': None},
    '2001-10-26': {'Assembly language': None, 'C': 19.75, 'C#': 0.42, 'C++': 16.1, 'Java': 25.68, 'JavaScript': 1.51, 'PHP': 1.78, 'Python': 1.28, 'SQL': 2.24, 'Visual Basic': None},
    '2001-11-28': {'Assembly language': None, 'C': 19.21, 'C#': 0.76, 'C++': 15.67, 'Java': 24.37, 'JavaScript': 1.47, 'PHP': 4.87, 'Python': 1.23, 'SQL': 1.84, 'Visual Basic': None},
    '2001-12-31': {'Assembly language': None, 'C': 20.14, 'C#': 0.59, 'C++': 14.96, 'Java': 24.2, 'JavaScript': 1.46, 'PHP': 7.27, 'Python': 1.04, 'SQL': 1.87, 'Visual Basic': None},
    '2002-01-30': {'Assembly language': None, 'C': 18.83, 'C#': 0.62, 'C++': 15.18, 'Java': 24.06, 'JavaScript': 2.73, 'PHP': 8.27, 'Python': 1.02, 'SQL': 1.94, 'Visual Basic': None},
    '2002-02-27': {'Assembly language': None, 'C': 19.89, 'C#': 0.74, 'C++': 15.54, 'Java': 24.01, 'JavaScript': 1.48, 'PHP': 7.44, 'Python': 0.99, 'SQL': 2.09, 'Visual Basic': None},
    '2002-03-29': {'Assembly language': None, 'C': 19.85, 'C#': 0.74, 'C++': 15.91, 'Java': 24.41, 'JavaScript': 1.47, 'PHP': 7.03, 'Python': 0.99, 'SQL': 2.06, 'Visual Basic': None}
    }
    :param path:
    :param title:
    :param xaxis_name:
    :param yaxis_name:
    :return:
    """
    timeline = chart_lib("timeline")
    
    for date in df_dict:
        timeline.add(draw_single_bar(df_dict[date], reversal_axis=True, title=title, xaxis_name=xaxis_name, yaxis_name=yaxis_name),
                     time_point=str(date))
    
    timeline.add_schema(
        # axis_type="time",  # time,value
        symbol="none",
        is_auto_play=True,
        play_interval=240,  # 表示播放的速度（跳动的间隔），单位毫秒（ms）
        is_loop_play=False,
        linestyle_opts=opts.LineStyleOpts(width=3),
        # label_opts=opts.LabelOpts(interval=5),
        )
    timeline.render(path)
