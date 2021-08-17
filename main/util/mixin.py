#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : mixin.py
# @Time   : 2020/11/27 11:51
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import collections
import logging
import pandas as pd
import numpy as np

from flask import request

from main.setting import db
from .common import json_resp
from .error import PlusException
from .response_code import RET

logger = logging.getLogger(__name__)


class RawQueryHandle:
    @staticmethod
    def raw_params_to_filter(params):
        return " and ".join([f"{k}='{v}'" for k, v in params.items()]) or "1=1"
    
    @staticmethod
    def raw_get_sql_count(sql):
        query = db.session.execute(sql)
        return query.rowcount
    
    @staticmethod
    def raw_get_sql_keys(sql):
        query = db.session.execute(sql)
        return query.keys()
    
    @staticmethod
    def raw_queryset_to_dict(queryset, default=None):
        if not queryset:
            return {}
        row = queryset.items()
        return {x[0]: x[1] if x[1] is not None else default for x in row}
    
    @classmethod
    def raw_queryset_list_to_dict_list(cls, queryset, default=None):
        return [cls.raw_queryset_to_dict(x, default) for x in queryset]
    
    @staticmethod
    def raw_get_sql_fetchone(sql, must=True, default=None):
        query = db.session.execute(sql)
        queryset = query.fetchone()
        if not queryset:
            if must:
                return {x: default for x in query.keys()}
            return {}
        row = queryset.items()
        return {x[0]: x[1] if x[1] is not None else default for x in row}


class TableQueryHandle:
    @staticmethod
    def table_params_to_filter(table, params):
        return [getattr(table.columns, k) == v for k, v in params.items() if hasattr(table.columns, k)]
    
    @staticmethod
    def table_field_to_query(table, field):
        return [getattr(table.columns, x) for x in field]
    
    @staticmethod
    def table_get_title(table, title_field):
        title_value_queryset = db.session.query(*[getattr(table.columns, x) for x in title_field]).first()
        if title_value_queryset:
            return list(title_value_queryset)
        return []
    
    @staticmethod
    def table_get_title_dict(table, title_field):
        queryset = db.session.query(*[getattr(table.columns, x) for x in title_field]).first()
        if not queryset:
            return []
        return [{"key": key, "value": getattr(queryset, key)} for key in title_field]
    
    @staticmethod
    def table_get_key(table):
        return [x.key for x in table.columns]
    
    @staticmethod
    def table_get_value_list(table, field):
        queryset = db.session.query(*[getattr(table.columns, x) for x in field]).all()
        return [list(x) for x in queryset]
    
    def table_get_value_dict(self, table, field):
        queryset = db.session.query(*[getattr(table.columns, x) for x in field]).all()
        return [self.table_queryset_to_dict(x, field) for x in queryset]
    
    def table_get_all_value_dict(self, table):
        field = self.table_get_key(table)
        queryset = db.session.query(*[getattr(table.columns, x) for x in field]).all()
        return [self.table_queryset_to_dict(x, field) for x in queryset] or [{}]
    
    @staticmethod
    def table_queryset_to_dict(queryset, keys):
        return {key: getattr(queryset, key) for key in keys if hasattr(queryset, key)}
    
    @staticmethod
    def table_queryset_to_dict_default(queryset, keys, default=0):
        return {key: default if getattr(queryset, key) is None else getattr(queryset, key) for key in keys if hasattr(queryset, key)}
    
    def table_queryset_list_to_dict(self, queryset_list, keys):
        return [self.table_queryset_to_dict(x, keys) for x in queryset_list]
    
    @staticmethod
    def table_queryset_to_list(queryset, keys):
        return [getattr(queryset, key) for key in keys if hasattr(queryset, key)]


class DataToolkit:
    @staticmethod
    def data_table_columns_sum(t1, t2):
        df1 = pd.DataFrame(t1)
        df2 = pd.DataFrame(t2)
        df_all = pd.concat([df1, df2])
        if not df_all.empty:
            df_all = df_all.groupby(0).apply(lambda x: x.iloc[:, 1:].sum())
        return df_all.reset_index().values


class ModelMixin:
    @property
    def queryset(self):
        return self.model.query.filter_by(is_deleted=True)
    
    def perform_query(self, queryset, params):
        return queryset.filter_by(**params)
    
    def get_query(self):
        try:
            logger.info(f"{self.resources}查询 user:{self.current_user.username} params:{self.request_args}")
            params = {x: self.request_args.get(x) for x in self.query_field if self.request_args.get(x, "") != ""}
            
            queryset = self.perform_query(self.queryset, params)
            queryset = queryset.order_by(self.model.update_time.desc())
            offset = self.request_args.get("offset")
            limit = self.request_args.get("limit")
            if offset and limit:
                instance = queryset.offset((int(offset) - 1) * int(limit)).limit(int(limit)).all()
                total = queryset.count()
            else:
                instance = queryset.all()
                total = len(instance)
            
            data = self.model.to_list(instance)
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{self.request_args} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    def post_query(self):
        try:
            logger.info(f"{self.resources}查询 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.query_field if self.request_data.get(x, "") != ""}
            
            queryset = self.perform_query(self.queryset, params)
            queryset = queryset.order_by(self.model.update_time.desc())
            offset = self.request_data.get("offset")
            limit = self.request_data.get("limit")
            if offset and limit:
                instance = queryset.offset((int(offset) - 1) * int(limit)).limit(int(limit)).all()
                total = queryset.count()
            else:
                instance = queryset.all()
                total = len(instance)
            
            data = self.model.to_list(instance)
            return json_resp(RET.OK, f"{self.resources}查询成功", data=data, total=total)
        except Exception as e:
            logger.error(f"{self.resources}查询错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}查询错误 error:{e}", data=None)
    
    def create(self):
        try:
            logger.info(f"{self.resources}创建 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.create_field if self.request_data.get(x) is not None}
            
            if not all([x in params for x in self.create_required_field]):
                raise PlusException(f"缺少必填参数")
            
            params["author"] = self.current_user.username
            # obj = self.model(**params)
            # data = obj.create()

            obj = self.model()
            data = obj.create(params)
            
            return json_resp(RET.OK, f"{self.resources}创建成功", data=data)
        except Exception as e:
            logger.error(f"{self.resources}创建错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}创建错误 error:{e}", data=None)
    
    @property
    def update_queryset(self):
        return self.queryset
    
    def update(self):
        try:
            logger.info(f"{self.resources}更新 user:{self.current_user.username} params:{self.request_data}")
            params = {x: self.request_data.get(x) for x in self.update_field if self.request_data.get(x) is not None}
            
            if not all([x in params for x in self.update_required_field]):
                raise PlusException("缺少必填参数")
            pk = params.pop("id")
            
            params["author"] = self.current_user.username
            instance = self.update_queryset.filter_by(id=pk).first()
            if not instance:
                raise PlusException(f"对象不存在", code=RET.NODATA)
            
            result = instance.update(params)
            # result = self.update_queryset().filter_by(id=pk).update(params)  # 不会触发校验
            
            return json_resp(RET.OK, f"{self.resources}更新成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}更新错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}更新错误 error:{e}", data=None)
    
    @property
    def delete_queryset(self):
        return self.queryset
    
    def delete(self):
        try:
            logger.info(f"{self.resources}删除 user:{self.current_user.username} params:{self.request_data}")
            
            pk = self.request_data.get("id")
            is_deleted = self.request_data.get("is_deleted", True)
            if pk is None:
                raise PlusException("缺少id参数")
            
            result = self.delete_queryset.filter_by(id=pk).update(dict(
                user=self.current_user.username,
                is_deleted=self.model.id if is_deleted else 0
                ))
            self.db_commit()
            
            return json_resp(RET.OK, f"{self.resources}删除成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}删除错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}删除错误 error:{e}", data=None)
    
    def abs_delete(self):
        try:
            logger.info(f"{self.resources}删除 user:{self.current_user.username} params:{self.request_data}")
            
            pk = self.request_data.get("id")
            if pk is None:
                raise PlusException("缺少id参数")
            
            result = self.delete_queryset.filter_by(id=pk).delete()
            self.db_commit()
            
            return json_resp(RET.OK, f"{self.resources}删除成功", data=result)
        except Exception as e:
            logger.error(f"{self.resources}删除错误 params:{self.request_data} error:{e}")
            return json_resp(getattr(e, "code", RET.SERVERERR), f"{self.resources}删除错误 error:{e}", data=None)
