# -*- coding: utf-8 -*-
"""

"""

def yieldroutes(func):
    """ Return a generator for routes that match the signature (name, args)
    of the func parameter. This may yield more than one route if the function
    takes optional keyword arguments. The output is best described by example::

        a()         -> '/a'
        b(x, y)     -> '/b/:x/:y'
        c(x, y=5)   -> '/c/:x' and '/c/:x/:y'
        d(x=5, y=6) -> '/d' and '/d/:x' and '/d/:x/:y'
    """
    import inspect  # Expensive module. Only import if necessary.
    path = '/' + func.__name__.replace('__', '/').lstrip('/')
    spec = inspect.getargspec(func)
    print spec
    """
    def a():
    ArgSpec(args=[], varargs=None, keywords=None, defaults=None)
    rule: /a
    
    def b(x, y):
    ArgSpec(args=['x', 'y'], varargs=None, keywords=None, defaults=None)
    rule: /b/:x/:y
    
    def c(x, y=5):
    ArgSpec(args=['x', 'y'], varargs=None, keywords=None, defaults=(5,))
    rule: /c/:x
    rule: /c/:x/:y
    
    def d(x=5, y=6):
    ArgSpec(args=['x', 'y'], varargs=None, keywords=None, defaults=(5, 6))
    rule: /d
    rule: /d/:x
    rule: /d/:x/:y
    
    """
    argc = len(spec[0]) - len(spec[3] or [])
    path += ('/:%s' * argc) % tuple(spec[0][:argc])
    yield path
    for arg in spec[0][argc:]:
        path += '/:%s' % arg
        yield path


def a():
    pass


def b(x, y):
    pass


def c(x, y=5):
    pass


def d(x=5, y=6):
    pass


for rule in yieldroutes(a):
    print 'rule: {}'.format(rule)

for rule in yieldroutes(b):
    print 'rule: {}'.format(rule)

for rule in yieldroutes(c):
    print 'rule: {}'.format(rule)

for rule in yieldroutes(d):
    print 'rule: {}'.format(rule)

