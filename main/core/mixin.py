#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : mixin.py
# @Time   : 2020/11/27 11:51
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :
import collections
import logging
import re
import pandas as pd
import numpy as np

from sqlalchemy import text, cast

from main.setting import db
from .fmt_resp import json_resp
from .error import ParamError, DataError
from .response_code import RET

logger = logging.getLogger(__name__)


class RawQueryHandle:
    """原生sql查询
    """
    
    @staticmethod
    def raw_params_to_filter(params):
        re_escape = re.compile(r"([\\'])")
        return " and ".join([f"{k}='%s'" % (re_escape.sub(r'\\\1', str(v))) for k, v in params.items()]) or "1=1"
    
    def raw_page(self, sql, offset=1, limit=1, serializer=None):
        offset = self.request_data.get("offset") or offset
        limit = self.request_data.get("limit") or limit
        offset, limit = (int(offset) - 1), int(limit)
        # query = db.session.execute(text(sql)) # 对于大表查询会很慢
        # total = query.rowcount
        cnt_sql = f"""select count(1) as cnt from ({sql.strip().strip(";")}) a """
        total = db.session.execute(text(cnt_sql)).scalar()
        # ADB不支持子查询排序 例：select *  from (select * from tb order by id) a limit 1 offset 10 此时排序无效会导致分页数据出现重复
        # mysql分页必须先limit 例：select * from a limit 1 offset 1  如果先offset则出错
        # page_sql = f"""select * from ({sql.strip().strip(";")}) a offset {offset * limit} limit {limit}"""
        page_sql = f"""{sql.strip().strip(";")} limit {limit} offset {offset * limit}"""
        instance = db.session.execute(text(page_sql)).all()  # sqlalchemy < 1.4 用fetchall
        if callable(serializer):
            instance = serializer(instance)
        return total, instance
    
    @staticmethod
    def raw_instance_to_dict(instance, default=None):
        if not instance:
            return {}
        row = instance._mapping.items()
        return {x[0]: x[1] if x[1] is not None else default for x in row}
    
    @classmethod
    def raw_instance_to_list(cls, instance, default=None):
        return [cls.raw_instance_to_dict(x, default) for x in instance]
    
    @staticmethod
    def raw_sql_fetchone(sql, must=False, default=None):
        queryset = db.session.execute(text(sql))
        instance = queryset.fetchone()
        if not instance:
            if must:
                return {x: default for x in queryset.keys()}
            return {}
        row = instance._mapping.items()
        return {x[0]: x[1] if x[1] is not None else default for x in row}
    
    @staticmethod
    def raw_sql_fetchall(sql, default=None):
        instance = db.session.execute(text(sql)).fetchall()
        ret = []
        for row in instance:
            # content = row.items() #  sqlalchemy 1.4版本后返回的是Row对象
            content = row._mapping.items()
            ret.append({x[0]: x[1] if x[1] is not None else default for x in content})
        return ret


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
    like_field = []
    
    def orm_page(self, queryset, offset=1, limit=1, serializer=None):
        offset = self.request_data.get("offset") or offset
        limit = self.request_data.get("limit") or limit
        total = queryset.count()
        instance = queryset.offset((offset - 1) * limit).limit(limit).all()
        if callable(serializer):
            instance = serializer(instance)
        return total, instance
    
    @property
    def queryset(self):
        return self.model.query.filter_by(is_deleted=0).order_by(self.model.id)
    
    def perform_query(self, queryset, params):
        # return queryset.filter_by(**params)
        like_field = self.like_field
        return queryset.filter_by(**{x: params[x] for x in params if x not in like_field}).filter(
            *[cast(getattr(self.model, x), db.String).like(f"%{params[x]}%") for x in params
              if hasattr(self.model, x) and x in like_field])
    
    def serializer(self, instance):
        return self.model.to_list(instance)
    
    def get_query(self):
        self.resources += "查询"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_args}")
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
        
        data = self.serializer(instance)
        return json_resp(RET.OK, f"{self.resources}成功", data=data, total=total)
    
    def post_query(self):
        self.resources += "查询"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_data}")
        params = {x: self.request_data.get(x) for x in self.query_field if self.request_data.get(x, "") != ""}
        
        queryset = self.perform_query(self.queryset, params)
        queryset = queryset.order_by(self.model.id.desc())
        total, data = self.orm_page(queryset, serializer=self.serializer)
        
        return json_resp(RET.OK, f"{self.resources}成功", data=data, total=total)
    
    def create(self):
        self.resources += "创建"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_data}")
        params = {x: self.request_data.get(x) for x in self.create_field if self.request_data.get(x) is not None}
        
        if not all([x in params for x in self.create_required_field]):
            raise ParamError(f"缺少必填参数", code=RET.RequiredERR)
        
        params["create_user"] = self.current_user.username
        params["update_user"] = self.current_user.username
        # obj = self.model(**params)  # 如果存在额外字段则失败
        # data = obj.create()
        
        obj = self.model()
        data = obj.create(**params)
        
        return json_resp(RET.OK, f"{self.resources}成功", data=data)
    
    @property
    def update_queryset(self):
        return self.queryset
    
    def update(self):
        self.resources += "更新"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_data}")
        params = {x: self.request_data.get(x) for x in self.update_field if self.request_data.get(x) is not None}
        
        if not all([x in params for x in self.update_required_field]):
            raise ParamError(f"缺少必填参数", code=RET.RequiredERR)
        pk = params.pop("id")
        
        params["update_user"] = self.current_user.username
        instance = self.update_queryset.filter_by(id=pk).first()
        if not instance:
            raise DataError(f"对象不存在", code=RET.NODATA)
        
        result = instance.update(params)
        # result = self.update_queryset().filter_by(id=pk).update(params)  # 不会触发校验
        
        return json_resp(RET.OK, f"{self.resources}成功", data=result)
    
    @property
    def delete_queryset(self):
        return self.model.query
    
    def delete(self):
        self.resources += "逻辑删除"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_data}")
        
        pk = self.request_data.get("id")
        is_deleted = self.request_data.get("is_deleted", True)
        if pk is None:
            raise ParamError(f"缺少id参数", code=RET.RequiredERR)
        
        result = self.delete_queryset.filter_by(id=pk).update(dict(
            update_user=self.current_user.username,
            is_deleted=self.model.id if is_deleted else 0
            ))
        self.db_commit()
        
        return json_resp(RET.OK, f"{self.resources}成功", data=result)
    
    def abs_delete(self):
        self.resources += "物理删除"
        logger.info(f"{self.resources} user:{self.current_user.username} params:{self.request_data}")
        
        pk = self.request_data.get("id")
        if pk is None:
            raise ParamError(f"缺少id参数", code=RET.RequiredERR)
        
        result = self.delete_queryset.filter_by(id=pk).delete()
        self.db_commit()
        
        return json_resp(RET.OK, f"{self.resources}成功", data=result)
