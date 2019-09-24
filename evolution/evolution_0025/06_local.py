# -*- coding: utf-8 -*-

import threading


class BaseRequest(object):
    __slots__ = ('environ')

    MEMFILE_MAX = 102400

    def __init__(self, environ=None):
        print 'step 3'
        if environ is None:
            print 'step 4'
            self.environ = {}
        else:
            self.environ = environ
        print 'step 6'
        self.environ['bottle.request'] = self  # self.environ 返回字典，然后给字典赋值
        print 'step 9'
        print self.environ


def local_property(name=None):
    ls = threading.local()

    def fget(self):
        print 'step 7'
        print 'fget'
        try:
            print 'step 8'
            return ls.var
        except AttributeError:
            raise RuntimeError("Request context not initialized.")

    def fset(self, value):
        print 'step 5'
        print 'fset value: {}'.format(value)
        ls.var = value
        print ls.var

    def fdel(self):
        print 'fdel'
        del ls.var

    return property(fget, fset, fdel, 'Thread-local property')


class LocalRequest(BaseRequest):
    print 'step 1'
    # LocalRequest 没有定义 __init__ 方法，不过会默认调用父类的 __init__ 方法
    bind = BaseRequest.__init__
    environ = local_property()
    print 'step 2'


request = LocalRequest()
"""
step 1
step 2
step 3
step 4
step 5
fset value: {}
{}

step 6
step 7
fget
step 8
step 9

step 7
fget
step 8
{'bottle.request': <__main__.LocalRequest object at 0x7fe5f06eb320>}
"""
