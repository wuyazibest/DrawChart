#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File   : lazy_load.py
# @Time   : 2021/8/10 21:13
# @Author : wuyazibest
# @Email  : wuyazibest@163.com
# @Desc   :


"""
懒加载（延迟实例化）
在类的实例化是并没有真正的实例化，只有在使用实例，调用实例的属性或方法时才开始实例化
减少资源占用
"""


class LazyProxy:
    def __init__(self, cls, *args, **kwargs):
        print("INIT PROXY")
        self.__dict__['_cls'] = cls
        self.__dict__['_args'] = args
        self.__dict__['_kwargs'] = kwargs
        self.__dict__['_obj'] = None
    
    def __getattr__(self, item):
        if self.__dict__['_obj'] is None:
            self._init_obj()
        return getattr(self.__dict__['_obj'], item)
    
    def __setattr__(self, key, value):
        if self.__dict__['_obj'] is None:
            self._init_obj()
        
        setattr(self.__dict__['_obj'], key, value)
    
    def _init_obj(self):
        # 生成类的实例
        self.__dict__['_obj'] = object.__new__(self.__dict__['_cls'])
        # 实例初始化
        self.__dict__['_obj'].__init__(*self.__dict__['_args'], **self.__dict__['_kwargs'])


class LazyMixin:
    def __new__(cls, *args, **kwargs):
        return LazyProxy(cls, *args, **kwargs)


if __name__ == '__main__':
    class A(LazyMixin):
        def __init__(self, ss):
            print("Init A")
            self.ss = ss
        
        def pp(self, ss):
            return "asdasd" + str(ss)
    
    
    class B:
        def __init__(self, ss):
            print("Init B")
            self.ss = ss
        
        def pp(self, ss):
            return "asdasd" + str(ss)
    
    
    # 懒加载（延迟实例化）
    a = A(1)
    print("----------------")
    print(a.ss)
    print(a.pp("xxxx"))
    
    # 一开始就生成
    b = B(1)
    print("----------------")
    print(b.ss)
    print(b.pp("xxxx"))
    
    # 懒加载（延迟实例化）
    c = LazyProxy(B, 1)
    print("----------------")
    print(c.ss)
    print(c.pp("xxxx"))
