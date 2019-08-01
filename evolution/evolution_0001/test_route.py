#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random

from evolution_0001 import HTTPError
from evolution_0001 import Request

OPTIMIZER = True
ROUTES_SIMPLE = {}
ROUTES_REGEXP = {}

# Routing
def compile_route(route):
    """ Compiles a route string and returns a precompiled RegexObject.

    Routes may contain regular expressions with named groups to support url parameters.
    Example:
      '/user/(?P<id>[0-9]+)' will match '/user/5' with {'id':'5'}

    A more human readable syntax is supported too.
    Example:
      '/user/:id/:action' will match '/user/5/kiss' with {'id':'5', 'action':'kiss'}
      Placeholders match everything up to the next slash.
      '/user/:id#[0-9]+#' will match '/user/5' but not '/user/tim'
      Instead of "#" you can use any single special char other than "/"
    """
    route = route.strip().lstrip('$^/ ').rstrip('$^ ')
    route = re.sub(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)', r'(?P<\1>\g<re>)', route)
    route = re.sub(r':([a-zA-Z_]+)', r'(?P<\1>[^/]+)', route)
    return re.compile('^/%s$' % route)


def match_url(url, method='GET'):
    """Returns the first matching handler and a parameter dict or raises HTTPError(404).

    This reorders the ROUTING_REGEXP list every 1000 requests. To turn this off, use OPTIMIZER=False"""

    print '\n\n开始解析路由'
    print 'url: {} method: {}'.format(url, method)
    url = '/' + url.strip().lstrip("/")
    print 'url: {} method: {}'.format(url, method)
    # Search for static routes first
    route = ROUTES_SIMPLE.get(method, {}).get(url, None)
    if route:
        print '解析成简单路由'
        return (route, {})

    print '解析成复杂路由'
    # Now search regexp routes
    routes = ROUTES_REGEXP.get(method, [])
    print routes
    """
    [
        [<_sre.SRE_Pattern object at 0x7fd106c123d0>, <function say at 0x1121320>], 
        [<_sre.SRE_Pattern object at 0x10a12b8>, <function say at 0x11212a8>]
    ]
    """

    print '开始循环'
    for i in xrange(len(routes)):
        print 'i = {}'.format(i)
        print routes
        match = routes[i][0].match(url)
        if match:
            handler = routes[i][1]
            # if i > 0 and OPTIMIZER and random.random() <= 0.001:
            if i > 0 and OPTIMIZER:
                # Every 1000 requests, we swap the matching route with its predecessor.
                # Frequently used routes will slowly wander up the list.
                # 每1000个请求，我们将匹配的路由与其前任交换。
                # 经常使用的路线会慢慢在列表中徘徊。
                routes[i - 1], routes[i] = routes[i], routes[i - 1]
                print routes
            return handler, match.groupdict()
    raise HTTPError(404, "Not found")

# add_route('/', handler)
# add_route('/hello/:name', handler)
# add_route('/hello', handler, method='POST')
def add_route(route, handler, method='GET', simple=False):
    """ Adds a new route to the route mappings.

        Example:
        def hello():
          return "Hello world!"
        add_route(r'/hello', hello)"""
    method = method.strip().upper()
    print '增加路由 path：{} method: {}'.format(route, method)
    print re.match(r'^/(\w+/)*\w*$', route)
    if re.match(r'^/(\w+/)*\w*$', route) or simple:
        ROUTES_SIMPLE.setdefault(method, {})[route] = handler
        print ROUTES_SIMPLE
    else:
        route = compile_route(route)
        ROUTES_REGEXP.setdefault(method, []).append([route, handler])
        print ROUTES_REGEXP

    print '全局路由变量 ROUTES_SIMPLE: {} ROUTES_REGEXP: {}'.format(ROUTES_SIMPLE, ROUTES_REGEXP)

"""
@route('/')
@route('/hello/:name')
@route('/hello', method='POST')
"""
def route(url, **kargs):
    """ Decorator for request handler. Same as add_route(url, handler)."""

    def wrapper(handler):
        # add_route('/', handler)
        # add_route('/hello/:name', handler)
        # add_route('/hello', handler, method='POST')
        add_route(url, handler, **kargs)
        return handler

    return wrapper

request = Request()

if __name__ == "__main__":

    @route('/')
    def index():
        return 'Hello World!'

    @route('/py')
    def py():
        return 'Hello Py'

    @route('/hello', method='POST')
    def say():
        name = request.POST['name']
        return 'Hello %s!' % name

    @route('/hello/:name')
    def say(name):
        return 'Hello %s!' % name


    @route('/say/:name')
    def say(name):
        return 'say %s!' % name

    """
    增加路由 path：/ method: GET
    <_sre.SRE_Match object at 0x1e4e210>
    {
    'GET': {'/': <function index at 0x1e4e1b8>}
    }
    全局路由变量 
    ROUTES_SIMPLE: 
    {
    'GET': {'/': <function index at 0x1e4e1b8>}
    } 
    ROUTES_REGEXP: {}
    
    增加路由 path：/py method: GET
    <_sre.SRE_Match object at 0x1e4e288>
    {
    'GET': {'/py': <function py at 0x1e4e230>, '/': <function index at 0x1e4e1b8>}
    }
    全局路由变量 
    ROUTES_SIMPLE: 
    {
    'GET': {'/py': <function py at 0x1e4e230>, '/': <function index at 0x1e4e1b8>}
    } 
    ROUTES_REGEXP: {}

    增加路由 path：/hello method: POST
    <_sre.SRE_Match object at 0x1e4e300>
    {
    'POST': {'/hello': <function say at 0x1e4e2a8>}, 
    'GET': {'/py': <function py at 0x1e4e230>, '/': <function index at 0x1e4e1b8>}
    }
    全局路由变量 
    ROUTES_SIMPLE: 
    {
    'POST': {'/hello': <function say at 0x1e4e2a8>}, 
    'GET': {'/py': <function py at 0x1e4e230>, '/': <function index at 0x1e4e1b8>}
    } 
    ROUTES_REGEXP: {}

    增加路由 path：/hello/:name method: GET
    None
    {
    'GET': [[<_sre.SRE_Pattern object at 0x7f213d0953d0>, <function say at 0x1e4e398>]]
    }
    全局路由变量 
    ROUTES_SIMPLE: 
    {
    'POST': {'/hello': <function say at 0x1e4e2a8>}, 
    'GET': {'/py': <function py at 0x1e4e230>, '/': <function index at 0x1e4e1b8>}
    } 
    ROUTES_REGEXP: 
    {
    'GET': [[<_sre.SRE_Pattern object at 0x7f213d0953d0>, <function say at 0x1e4e398>]]
    }
    
    增加路由 path：/say/:name method: GET
    None
    {
    'GET': [
            [<_sre.SRE_Pattern object at 0x7fd106c123d0>, <function say at 0x1121320>], 
            [<_sre.SRE_Pattern object at 0x10a12b8>, <function say at 0x11212a8>]
           ]
    }
    全局路由变量 
    ROUTES_SIMPLE: 
    {
    'POST': {'/hello': <function say at 0x1121230>}, 
    'GET': {'/py': <function py at 0x11211b8>, '/': <function index at 0x1121140>}
    } 
    ROUTES_REGEXP: 
    {
    'GET': [
            [<_sre.SRE_Pattern object at 0x7fd106c123d0>, <function say at 0x1121320>], 
            [<_sre.SRE_Pattern object at 0x10a12b8>, <function say at 0x11212a8>]
           ]
    }
    """

    path_method = [('/', 'GET'), ('/py', 'GET'), ('/hello', 'POST'), ('/hello/lanzhiwang', 'GET'), ('/say/lanzhiwang', 'GET'), ('/error', 'POST')]
    for path, method in path_method:
        handler, args = match_url(path, method)
        print 'handler: {} args: {}'.format(handler, args)

    """
    开始解析路由
    url: / method: GET
    url: / method: GET
    解析成简单路由
    handler: <function index at 0x1edf140> args: {}
    
    
    开始解析路由
    url: /py method: GET
    url: /py method: GET
    解析成简单路由
    handler: <function py at 0x1edf1b8> args: {}
    
    
    开始解析路由
    url: /hello method: POST
    url: /hello method: POST
    解析成简单路由
    handler: <function say at 0x1edf230> args: {}
    
    
    开始解析路由
    url: /hello/lanzhiwang method: GET
    url: /hello/lanzhiwang method: GET
    解析成复杂路由
    [[<_sre.SRE_Pattern object at 0x7fd2a00ff3d0>, <function say at 0x1edf320>], [<_sre.SRE_Pattern object at 0x1e5f2b8>, <function say at 0x1edf2a8>]]
    开始循环
    i = 0
    [[<_sre.SRE_Pattern object at 0x7fd2a00ff3d0>, <function say at 0x1edf320>], [<_sre.SRE_Pattern object at 0x1e5f2b8>, <function say at 0x1edf2a8>]]
    handler: <function say at 0x1edf320> args: {'name': 'lanzhiwang'}
    
    
    开始解析路由
    url: /say/lanzhiwang method: GET
    url: /say/lanzhiwang method: GET
    解析成复杂路由
    [[<_sre.SRE_Pattern object at 0x7fd2a00ff3d0>, <function say at 0x1edf320>], [<_sre.SRE_Pattern object at 0x1e5f2b8>, <function say at 0x1edf2a8>]]
    开始循环
    i = 0
    [[<_sre.SRE_Pattern object at 0x7fd2a00ff3d0>, <function say at 0x1edf320>], [<_sre.SRE_Pattern object at 0x1e5f2b8>, <function say at 0x1edf2a8>]]
    i = 1
    [[<_sre.SRE_Pattern object at 0x7fd2a00ff3d0>, <function say at 0x1edf320>], [<_sre.SRE_Pattern object at 0x1e5f2b8>, <function say at 0x1edf2a8>]]
    [[<_sre.SRE_Pattern object at 0x1e5f2b8>, <function say at 0x1edf2a8>], [<_sre.SRE_Pattern object at 0x7fd2a00ff3d0>, <function say at 0x1edf320>]]
    handler: <function say at 0x1edf2a8> args: {'name': 'lanzhiwang'}
    
    
    开始解析路由
    url: /error method: POST
    url: /error method: POST
    解析成复杂路由
    []
    开始循环
    Traceback (most recent call last):
      File "test_route.py", line 225, in <module>
        handler, args = match_url(path, method)
      File "test_route.py", line 77, in match_url
        raise HTTPError(404, "Not found")
    evolution_0001.HTTPError: Not found

    """

