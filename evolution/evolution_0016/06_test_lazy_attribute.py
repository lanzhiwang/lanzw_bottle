# -*- coding: utf-8 -*-

"""
参考
https://anyisalin.github.io/2017/03/08/python-descriptor/
"""

import re
import functools


class lazy_attribute(object):  # Does not need configuration -> lower-case name
    ''' A property that caches itself to the class object. '''

    def __init__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter = func

    def __get__(self, obj, cls):
        value = self.getter(cls)
        setattr(cls, self.__name__, value)
        return value


class Router(object):

    @lazy_attribute
    def syntax(cls):
        return re.compile(r'(?<!\\):([a-zA-Z_][a-zA-Z_0-9]*)?(?:#(.*?)#)?')

    """
    等价于
    syntax = lazy_attribute(syntax)

    当使用下面的方法获取值，修改值，删除值时，调用对应的魔术方法
    self.syntax
    self.syntax = 
    del self.syntax
    
    实例化 Router() 对象后获取值，修改值，删除值时，也调用对应的魔术方法
    
    第一次无论何时，用什么方法获取值，__get__ 方法中的 value 会是正则对象，并且该正则对象
    赋值给了同名的 syntax 属性，类似于
    syntax = re.compile(r'(?<!\\):([a-zA-Z_][a-zA-Z_0-9]*)?(?:#(.*?)#)?')
    
    后面第二次，第三次获取值都直接返回正则对象
    
    正则对象是在第一次获取属性之后生成的，并不是直接写死或者__init__()初始化时生成，
    是调用之后生成的，所以是懒加载或者延时加载

    """