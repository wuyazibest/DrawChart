#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : test_model.py
# @Time   : 2021/3/25 21:21
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import inspect


class DataDict(dict):
    def __getattr__(self, item):
        return self.get(item, None)


class Choice:
    """
    label 为展示值
    value 为存储值
    admin = DataDict({"label": "管理员", "value": "admin"})
    存在问题： 取出存储在数据库中的值 无法转换成显示值  例：数据库中存储的为admin 却无法转换成管理员
    """
    
    @classmethod
    def choice_name(cls):
        return [x[0] for x in inspect.getmembers(cls, lambda x: isinstance(x, DataDict)) if not x[0].startswith("__")]
    
    @classmethod
    def choice_value(cls):
        return [getattr(cls, x).value for x in cls.choice_name()]
    
    @classmethod
    def choice_label(cls):
        return [getattr(cls, x).label for x in cls.choice_name()]


class RoleChoice(Choice):
    admin = DataDict({"label": "管理员", "value": "admin"})
    user = DataDict({"label": "普通用户", "value": "user"})


# denmo
class UserModel:
    __bind_key__ = "management"
    __tablename__ = "open_api_user"
    __table_args__ = {"comment": "接口开放平台用户"}
    
    class RoleChoice(Choice):
        admin = DataDict({"label": "admin", "value": "admin"})
        user = DataDict({"label": "admin", "value": "admin"})


print(UserModel.RoleChoice.admin.label)
