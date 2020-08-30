import inspect

def yieldroutes(func):
    """ Return a generator for routes that match the signature (name, args)
    of the func parameter. This may yield more than one route if the function
    takes optional keyword arguments. The output is best described by example:
      a()         -> '/a'
      b(x, y)     -> '/b/:x/:y'
      c(x, y=5)   -> '/c/:x' and '/c/:x/:y'
      d(x=5, y=6) -> '/d' and '/d/:x' and '/d/:x/:y'
    """
    print('func.__name__: %r' % func.__name__)
    path = func.__name__.replace('__','/').lstrip('/')
    print('path: %r' % path)
    spec = inspect.getargspec(func)
    print(spec)
    print(spec[0])
    print(spec[1])
    print(spec[2])
    print(spec[3])
    argc = len(spec[0]) - len(spec[3] or [])
    print('argc: %s' % argc)
    print(spec[0][:argc])
    print(spec[0][argc:])
    print('/:%s' * argc)
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

for fun in [a, b, c, d]:
    print(list(yieldroutes(fun)))
    print('++++++++++++++++++++++++++')

"""
func.__name__: 'a'
path: 'a'
ArgSpec(args=[], varargs=None, keywords=None, defaults=None)
[]
None
None
None
argc: 0
[]
[]

['a']
++++++++++++++++++++++++++
func.__name__: 'b'
path: 'b'
ArgSpec(args=['x', 'y'], varargs=None, keywords=None, defaults=None)
['x', 'y']
None
None
None
argc: 2
['x', 'y']
[]
/:%s/:%s
['b/:x/:y']
++++++++++++++++++++++++++
func.__name__: 'c'
path: 'c'
ArgSpec(args=['x', 'y'], varargs=None, keywords=None, defaults=(5,))
['x', 'y']
None
None
(5,)
argc: 1
['x']
['y']
/:%s
['c/:x', 'c/:x/:y']
++++++++++++++++++++++++++
func.__name__: 'd'
path: 'd'
ArgSpec(args=['x', 'y'], varargs=None, keywords=None, defaults=(5, 6))
['x', 'y']
None
None
(5, 6)
argc: 0
[]
['x', 'y']

['d', 'd/:x', 'd/:x/:y']
++++++++++++++++++++++++++
"""
