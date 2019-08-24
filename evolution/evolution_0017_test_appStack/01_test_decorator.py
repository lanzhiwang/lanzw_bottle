# -*- coding: utf-8 -*-
"""
测试多个装饰器的顺序
"""

def one(func):
    print('----1----')
    def two():
        print('----2----')
        func()
    return two

def a(func):
    print('----a----')
    def b():
        print('----b----')
        func()
    return b

"""
@one
@a
def demo():
    print('----3----')
"""

def demo():
    print('----3----')

b = a(demo)
two = one(b)
two()

"""
----a----
----1----
----2----
----b----
----3----
"""