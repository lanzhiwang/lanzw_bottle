# -*- coding: utf-8 -*-

import functools


class DictProperty(object):

    # DictProperty('__dict__')
    def __init__(self, attr, key=None, read_only=False):
        self.attr = attr  # '__dict__'
        self.key = key  # None
        self.read_only = read_only  # False

    def __call__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter = func
        self.key = self.key or func.__name__  # co
        return self

    def __get__(self, obj, cls):
        if not obj:  # 类名直接调用返回 DictProperty 对象
            return self
        key = self.key  # co
        storage = getattr(obj, self.attr)  # SimpleTemplate 的 __dict__ 属性
        if key not in storage:
            storage[key] = self.getter(obj)  # SimpleTemplate['co'] =
        return storage[key]

    def __set__(self, obj, value):
        if self.read_only:
            raise ApplicationError("Read-Only property.")
        getattr(obj, self.attr)[self.key] = value

    def __delete__(self, obj):
        if self.read_only:
            raise ApplicationError("Read-Only property.")
        del getattr(obj, self.attr)[self.key]


def cached_property(func):
    ''' A property that, if accessed, replaces itself with the computed
        value. Subsequent accesses won't call the getter again. '''
    d = DictProperty('__dict__')
    r = d(func)
    return r


class SimpleTemplate(object):
    blocks = ('if', 'elif', 'else', 'try', 'except', 'finally', 'for', 'while', 'with', 'def', 'class')
    dedent_blocks = ('elif', 'else', 'except', 'finally')

    @cached_property
    def co(self):
        return compile(self.code, self.filename or '<string>', 'exec')

    """
    co = cached_property(co)
    
    self.co
    self.co = 
    del self.co
    """
