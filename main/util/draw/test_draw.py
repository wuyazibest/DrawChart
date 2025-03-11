#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : test_draw.py
# @Time   : 2025/2/26 15:58
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import os

import pytest
import numpy as np
import pandas as pd

from main.config import BASE_DIR
from main.util.draw import draw_bar, draw_line, draw_timeline


def setup_module(module):
    """
    这是一个module级别的setup，它会在本module(test_website.py)里
    所有test执行之前，被调用一次。
    注意，它是直接定义为一个module里的函数"""
    print()
    print("-------------- setup before module --------------")


def teardown_module(module):
    """
    这是一个module级别的teardown，它会在本module(test_website.py)里
    所有test执行完成之后，被调用一次。
    注意，它是直接定义为一个module里的函数"""
    print("-------------- teardown after module --------------")


class TestDraw(object):
    title = {
        "title"     : "开发语言热度",
        "xaxis_name": "语言种类",
        "yaxis_name": "热度",
        }
    df = None
    
    @classmethod
    def setup_class(cls):
        """ 这是一个class级别的setup函数，它会在这个测试类TestSohu里
        所有test执行之前，被调用一次.
        注意它是一个@classmethod
        """
        print("------ setup before class TestSohu ------")
        cls.get_format_data()
    
    @classmethod
    def teardown_class(cls):
        """ 这是一个class级别的teardown函数，它会在这个测试
        类TestSohu里所有test执行完之后，被调用一次.
       注意它是一个@classmethod
       """
    
    print("------ teardown after class TestSohu ------")
    
    def setup_method(self, method):
        """ 这是一个method级别的setup函数，它会在这个测试
         类TestSohu里，每一个test执行之前，被调用一次.
        """
        print("--- setup before each method ---")
    
    def teardown_method(self, method):
        """ 这是一个method级别的teardown函数，它会在这个测试
         类TestSohu里，每一个test执行之后，被调用一次.
        """
        print("--- teardown after each method ---")
    
    @classmethod
    def get_format_data(cls):
        df_dict = {
            '2001-06-30': {'Assembly language': None, 'C': 20.24, 'C#': 0.38, 'C++': 14.2, 'Java': 26.49, 'JavaScript': 1.55, 'PHP': 1.9,
                           'Python'           : 1.25, 'SQL': 2.96, 'Visual Basic': None
                           },
            '2001-07-30': {'Assembly language': None, 'C': 20.77, 'C#': 0.43, 'C++': 16.11, 'Java': 25.03, 'JavaScript': 1.72, 'PHP': 1.38,
                           'Python'           : 1.13, 'SQL': 2.77, 'Visual Basic': None
                           },
            '2001-08-30': {'Assembly language': None, 'C': 20.75, 'C#': 0.38, 'C++': 16.12, 'Java': 24.66, 'JavaScript': 1.66, 'PHP': 1.55,
                           'Python'           : 1.2, 'SQL': 2.38, 'Visual Basic': None
                           },
            '2001-09-28': {'Assembly language': None, 'C': 20.77, 'C#': 0.39, 'C++': 15.85, 'Java': 24.82, 'JavaScript': 1.63, 'PHP': 1.55,
                           'Python'           : 1.17, 'SQL': 2.36, 'Visual Basic': None
                           },
            '2001-10-26': {'Assembly language': None, 'C': 19.75, 'C#': 0.42, 'C++': 16.1, 'Java': 25.68, 'JavaScript': 1.51, 'PHP': 1.78,
                           'Python'           : 1.28, 'SQL': 2.24, 'Visual Basic': None
                           },
            '2001-11-28': {'Assembly language': None, 'C': 19.21, 'C#': 0.76, 'C++': 15.67, 'Java': 24.37, 'JavaScript': 1.47, 'PHP': 4.87,
                           'Python'           : 1.23, 'SQL': 1.84, 'Visual Basic': None
                           },
            '2001-12-31': {'Assembly language': None, 'C': 20.14, 'C#': 0.59, 'C++': 14.96, 'Java': 24.2, 'JavaScript': 1.46, 'PHP': 7.27,
                           'Python'           : 1.04, 'SQL': 1.87, 'Visual Basic': None
                           },
            '2002-01-30': {'Assembly language': None, 'C': 18.83, 'C#': 0.62, 'C++': 15.18, 'Java': 24.06, 'JavaScript': 2.73, 'PHP': 8.27,
                           'Python'           : 1.02, 'SQL': 1.94, 'Visual Basic': None
                           },
            '2002-02-27': {'Assembly language': None, 'C': 19.89, 'C#': 0.74, 'C++': 15.54, 'Java': 24.01, 'JavaScript': 1.48, 'PHP': 7.44,
                           'Python'           : 0.99, 'SQL': 2.09, 'Visual Basic': None
                           },
            '2002-03-29': {'Assembly language': None, 'C': 19.85, 'C#': 0.74, 'C++': 15.91, 'Java': 24.41, 'JavaScript': 1.47, 'PHP': 7.03,
                           'Python'           : 0.99, 'SQL': 2.06, 'Visual Basic': None
                           }
            }
        
        pd.set_option('display.float_format', lambda x: str(x))
        df = pd.DataFrame.from_dict(df_dict, orient="index")
        df = df.astype("float")
        df = df.round(2)
        # df = df.replace({np.nan: None})
        cls.df = df
    
    # @pytest.mark.skip()
    def test_draw_bar(self):
        draw_bar(self.df.index.values.tolist(), self.df.to_dict("list"), **self.title)
        path = os.path.join(BASE_DIR, "dist", "bar.html")
        assert os.path.exists(path) is True
    
    # @pytest.mark.skip()
    def test_draw_line(self):
        draw_line(self.df.index.values.tolist(), self.df.to_dict("list"), **self.title)
        path = os.path.join(BASE_DIR, "dist", "line.html")
        assert os.path.exists(path) is True
    
    # @pytest.mark.skip()
    def test_draw_timeline(self):
        draw_timeline(self.df.to_dict("index"), **self.title)
        path = os.path.join(BASE_DIR, "dist", "timeline.html")
        assert os.path.exists(path) is True


if __name__ == '__main__':
    pytest.main()
