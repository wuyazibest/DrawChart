#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : meta.py
# @Time    : 2020/8/30 15:32
# @Author  : wuyazibest
# @Email   : wuyazibest@163.com
# @Desc    : 基础类：基础模型，自定义模型字段，基础视图
import datetime
import logging
import uuid
import sqlalchemy

from functools import update_wrapper
from flask import g, request, json, current_app
from flask.views import View
from sqlalchemy import types, TypeDecorator, Boolean
from sqlalchemy.orm import validates

from main import config
from main.setting import db

from .auth import IsLoginPermission
from .fmt_resp import json_resp
from .error import exception_assert, MethodNotAllowed, RET
from .mixin import ModelMixin

logger = logging.getLogger(__name__)

DataDict = config.DataDict


class LiberalBoolean(TypeDecorator):
    """
    sqlalchemy新版本的bool类型只支持 True/False 标准格式，不兼容0/1等
    """
    impl = Boolean
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = bool(int(value))
        return value


class StrChoiceType(types.TypeDecorator):
    """
    usage:
        ChoiceType({"s":"short","m":"medium","t":"tall"})
        migrate 创建数据库是需要临时将类型改为impl指定的类型
    """
    impl = types.String
    
    def __init__(self, choices, length=191, **kw):
        self.choices = dict(choices)
        super(StrChoiceType, self).__init__(length=length, **kw)
    
    def process_bind_param(self, value, dialect):
        # 返回值写入到数据库
        values = [k for k, v in self.choices.items() if v == value]
        if not values:
            raise Exception(f"choice value not in options!")
        return values[0]
    
    def process_result_value(self, value, dialect):
        # 从数据库查询结果处理后返回
        return self.choices[value]


class IntChoiceType(types.TypeDecorator):
    """
    usage:
        ChoiceType({"s":"short","m":"medium","t":"tall"})
        migrate 创建数据库是需要临时将类型改为impl指定的类型
    """
    impl = types.Integer
    
    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(IntChoiceType, self).__init__(**kw)
    
    def process_bind_param(self, value, dialect):
        # 返回值写入到数据库
        values = [k for k, v in self.choices.items() if v == value]
        if not values:
            raise Exception(f"choice value not in options!")
        return values[0]
    
    def process_result_value(self, value, dialect):
        # 从数据库查询结果处理后返回
        return self.choices[value]


class JSONEncodedDict(types.TypeDecorator):
    """Represents an immutable structure as a json-encode string.
    Usage:
        JSONEncodedDict(255)
    
    """
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        """Receive a bound parameter value to be converted.
        """
        if value is not None:
            value = json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        """Receive a result-row column value to be converted.
        """
        if value is not None:
            value = json.loads(value)
        return value


class MetaModel(db.Model):
    __abstract__ = True
    
    def validate_finally(self):
        pass
    
    def create(self, params=None, **kwargs):
        try:
            params = params or {}
            params.update(kwargs)
            for k, v in params.items():
                if hasattr(self, k):
                    setattr(self, k, v)
            
            self.validate_finally()
            db.session.add(self)
            db.session.commit()
            return self.to_dict()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def update(self, params=None, **kwargs):
        try:
            params = params or {}
            params.update(kwargs)
            for k, v in params.items():
                if hasattr(self, k):
                    setattr(self, k, v)
            
            self.validate_finally()
            db.session.commit()
            return self.to_dict()
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def get_columns_dict(cls, default_value=None):
        return {x.name: default_value for x in cls.__table__.columns}
    
    def to_dict(self):
        return DataDict({x.name: getattr(self, x.name, None) for x in self.__table__.columns})
    
    @staticmethod
    def to_list(obj_list):
        ret = []
        for i in obj_list:
            if isinstance(i, sqlalchemy.Row):
                row = DataDict(i._mapping)  # 使用了with_entities之后，返回的不再是模型
            else:
                row = i.to_dict()
            ret.append(row)
        
        return ret


class ValidateModel(MetaModel):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, comment="id")
    create_user = db.Column(db.Text, nullable=False, comment="创建人")
    update_user = db.Column(db.Text, nullable=False, comment="更新人")
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")
    is_deleted = db.Column(db.Integer, nullable=False, default=0, comment="删除标记")
    remark = db.Column(db.Text, nullable=True, default="", comment="备注")
    
    validates_choice = set()
    
    @validates(*validates_choice)
    def validate_choice(self, key, value):
        exception_assert(value in getattr(self, f"{key}_choice".upper()), f"不支持的{key}!", RET.EnumERR)
        return value
    
    def to_dict(self):
        ignore = ("create_time", "update_time")
        ret = DataDict({x.name: getattr(self, x.name, None) for x in self.__table__.columns if x.name not in ignore})
        ret["create_time"] = self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        ret["update_time"] = self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        
        for i in self.validates_choice:
            ret[f"{i}_label"] = getattr(self, f"{i}_choice".upper()).get(getattr(self, i))
        return ret


class MetaView(object):
    http_method_funcs = frozenset(
        ["GET", "POST", "HEAD", "OPTIONS", "DELETE", "PUT", "TRACE", "PATCH"]
        )
    methods = set()
    provide_automatic_options = None
    decorators = ()
    model = None
    
    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @classmethod
    def as_view(cls, actions, **class_kwargs):
        """ this refer flask MethodView and django rest framework ViewSetMixin
        For example:
        actions = {
            "GET":"get_func",
            "POST":"post_func",
        }
        """
        
        if not actions or not isinstance(actions, dict):
            raise TypeError("The `actions` argument must be provided when "
                            "calling `.as_view()` on a ViewSet. For example "
                            "`.as_view({'get': 'list'})`")
        
        for key in class_kwargs:
            if key in cls.http_method_funcs:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r" % (
                    cls.__name__, key))
        
        cls.methods = set([x.upper() for x in actions])
        
        def view(*args, **kwargs):
            self = cls(**class_kwargs)
            
            for method, action in actions.items():
                handler = getattr(self, action)
                setattr(self, method.upper(), handler)
            
            if hasattr(self, "GET") and not hasattr(self, "HEAD"):
                self.HEAD = self.GET
            
            self.args = args
            self.kwargs = kwargs
            return self.dispatch_request(*args, **kwargs)
        
        # We attach the view class to the view function for two reasons:
        # first of all it allows us to easily figure out what class-based
        # view this thing came from, secondly it's also used for instantiating
        # the view class so you can actually replace it with something else
        # for testing purposes and debugging.
        update_wrapper(view, cls, updated=())
        view.cls = cls
        view.__name__ += str(actions).replace(".", "")
        view.methods = cls.methods
        view.provide_automatic_options = cls.provide_automatic_options
        
        return view
    
    def check_permissions(self, view):
        """
        权限检查
        """
        decorators = [*self.decorators, *getattr(view, "decorators", [])]
        for permission in decorators:
            view = permission(view)
        return view
    
    def initial(self, view):
        """
        进行一些请求前的初始化
        """
        return self.check_permissions(view)
    
    def http_method_not_allowed(self, *args, **kwargs):
        raise MethodNotAllowed(f"Method {request.method.upper()} not allowed")
    
    def handle_exception(self, exc):
        msg = f"{self.resources}错误 query:{self.request_args} params:{self.request_data} error:{exc}"
        logger.error(msg)
        
        if current_app.extensions.get("exception_handler"):
            response = current_app.extensions["exception_handler"](self, exc)
        else:
            response = json_resp(getattr(exc, "code", RET.SYSERR), msg)
        
        return response
    
    def dispatch_request(self, *args, **kwargs):
        try:
            if request.method in self.http_method_funcs:
                handler = getattr(self, request.method, self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            
            handler = self.initial(handler)
            response = handler(*args, **kwargs)
            # db.session.commit()  # 自动提交
        except Exception as exc:
            db.session.rollback()
            response = self.handle_exception(exc)
        
        return response
    
    @property
    def request_args(self):
        data = DataDict()
        for k, v in request.args.lists():
            data[k] = v if len(v) > 1 else v[0]
        return data
    
    @property
    def request_data(self) -> dict:
        data = DataDict()
        data.update(request.form)
        try:
            data.update(request.json or {})
        except Exception:
            pass
        
        return data
    
    @property
    def request_from(self):
        return g.request_from
    
    @property
    def current_user(self):
        if hasattr(g, "user"):
            return g.user
        
        return DataDict({
            "id"      : None,
            "username": request.headers.get("host"),
            "role"    : None,
            })
    
    @staticmethod
    def db_commit():
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class MetaViewSet(MetaView):
    decorators = (IsLoginPermission,)
    resources = ""
    query_field = ()
    create_field = ()
    update_field = ()
    create_required_field = ()
    update_required_field = ("id",)


class ModelViewSet(MetaViewSet, ModelMixin): pass
