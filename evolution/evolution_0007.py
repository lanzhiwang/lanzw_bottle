# -*- coding: utf-8 -*-

"""
第一版
实现基本框架基本结构

具体实现：
http status code
Request
Response
route
wsgi server
"""

__author__ = 'lanzhiwang'
__version__ = ('0', '0', '0')
__license__ = 'MIT'

import cgi
import mimetypes
import os
import sys
import re
import random
import Cookie
import threading
import time
import traceback

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

DEBUG = False
# OPTIMIZER = True
OPTIMIZER = False
ROUTES_SIMPLE = {}
ROUTES_REGEXP = {}
ERROR_HANDLER = {}  # ERROR_HANDLER[code] = handler
HTTP_CODES = {
    100: 'CONTINUE',
    101: 'SWITCHING PROTOCOLS',
    200: 'OK',
    201: 'CREATED',
    202: 'ACCEPTED',
    203: 'NON-AUTHORITATIVE INFORMATION',
    204: 'NO CONTENT',
    205: 'RESET CONTENT',
    206: 'PARTIAL CONTENT',
    300: 'MULTIPLE CHOICES',
    301: 'MOVED PERMANENTLY',
    302: 'FOUND',
    303: 'SEE OTHER',
    304: 'NOT MODIFIED',
    305: 'USE PROXY',
    306: 'RESERVED',
    307: 'TEMPORARY REDIRECT',
    400: 'BAD REQUEST',
    401: 'UNAUTHORIZED',
    402: 'PAYMENT REQUIRED',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    405: 'METHOD NOT ALLOWED',
    406: 'NOT ACCEPTABLE',
    407: 'PROXY AUTHENTICATION REQUIRED',
    408: 'REQUEST TIMEOUT',
    409: 'CONFLICT',
    410: 'GONE',
    411: 'LENGTH REQUIRED',
    412: 'PRECONDITION FAILED',
    413: 'REQUEST ENTITY TOO LARGE',
    414: 'REQUEST-URI TOO LONG',
    415: 'UNSUPPORTED MEDIA TYPE',
    416: 'REQUESTED RANGE NOT SATISFIABLE',
    417: 'EXPECTATION FAILED',
    500: 'INTERNAL SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT',
    505: 'HTTP VERSION NOT SUPPORTED',
}


# Exceptions and Events

class BottleException(Exception):
    """ A base class for exceptions used by bottle."""
    pass


class HTTPError(BottleException):
    """ A way to break the execution and instantly jump to an error handler. """

    def __init__(self, status, text):
        self.output = text
        self.http_status = int(status)

    def __str__(self):
        return self.output


class BreakTheBottle(BottleException):
    """ Not an exception, but a straight jump out of the controller code.

    Causes the WSGIHandler to instantly call start_response() and return the
    content of output """

    def __init__(self, output):
        self.output = output


# Classes

"""
class Response

self.header = HeaderDict()
self.header['Content-Type'] = value
return self.header['Content-Type']

response.header['Content-Length'] = len(output)
response.header.add('Set-Cookie', c.OutputString())
response.header.items()
response.header['Location'] = url
"""
class HeaderDict(dict):
    ''' A dictionary with case insensitive (titled) keys.

    You may add a list of strings to send multible headers with the same name.'''

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.title(), value)

    def __getitem__(self, key):
        return dict.__getitem__(self, key.title())

    def __delitem__(self, key):
        return dict.__delitem__(self, key.title())

    def __contains__(self, key):
        return dict.__contains__(self, key.title())

    def items(self):
        """ Returns a list of (key, value) tuples """
        for key, values in dict.items(self):
            if not isinstance(values, list):  # 全部转为 list
                values = [values]
            for value in values:
                yield (key, str(value))

    def add(self, key, value):
        """ Adds a new header without deleting old ones """
        if isinstance(value, list):
            for v in value:
                self.add(key, v)
        elif key in self:
            if isinstance(self[key], list):
                self[key].append(value)
            else:
                self[key] = [self[key], value]
        else:
            self[key] = [value]


# 暂时不需要继承 threading.local
# class Request(threading.local):
class Request():
    """ Represents a single request using thread-local namespace. """

    def bind(self, environ):
        """ Binds the enviroment of the current request to this request handler """
        self._environ = environ
        self._GET = None
        self._POST = None
        self._GETPOST = None
        self._COOKIES = None
        self.path = self._environ.get('PATH_INFO', '/').strip()
        if not self.path.startswith('/'):
            self.path = '/' + self.path

    @property
    def method(self):
        ''' Returns the request method (GET,POST,PUT,DELETE,...) '''
        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def query_string(self):
        ''' Content of QUERY_STRING '''
        return self._environ.get('QUERY_STRING', '')

    @property
    def input_length(self):
        ''' Content of CONTENT_LENGTH '''
        try:
            return int(self._environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            return 0

    @property
    def GET(self):
        """Returns a dict with GET parameters."""
        if self._GET is None:
            raw_dict = parse_qs(self.query_string, keep_blank_values=1)  # 好像有bug，不应该是 self.query，应该是 self.query_string
            print 'raw_dict: {}'.format(raw_dict)  # raw_dict: {'q': ['w'], 'a': ['s']}
            self._GET = {}
            for key, value in raw_dict.items():
                if len(value) == 1:
                    self._GET[key] = value[0]
                else:
                    self._GET[key] = value
        return self._GET  # {'q': 'w', 'a': 's'}

    @property
    def POST(self):
        """Returns a dict with parsed POST data."""
        if self._POST is None:
            # 'wsgi.input': <socket._fileobject object at 0x1991050>,
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            print 'raw_data: {}'.format(raw_data)
            print type(raw_data)
            self._POST = {}

            """
            Traceback (most recent call last):
              File "evolution_0006.py", line 403, in WSGIHandler
                output = handler(**args)
              File "evolution_0006.py", line 657, in say
                name = request.POST['name']
              File "evolution_0006.py", line 221, in POST
                for key, value in raw_data:
            ValueError: too many values to unpack
            """

            """
            for key, value in raw_data:
                if value.filename:
                    self._POST[key] = value
                elif isinstance(value, list):
                    self._POST[key] = [v.value for v in value]
                else:
                    self._POST[key] = value.value
            """

            for key in raw_data:
                print 'key: {}'.format(key)
                print raw_data[key]  # FieldStorage('name', None, 'user')
                print type(raw_data[key])  # <type 'instance'>
                if raw_data[key].filename:
                    print 'filename: {}'.format(raw_data[key].filename)
                    self._POST[key] = raw_data[key]
                elif isinstance(raw_data[key], list):
                    print 'list: {}'.format(raw_data[key])
                    self._POST[key] = [v.value for v in raw_data[key]]
                else:
                    print 'raw_data[key].value'
                    self._POST[key] = raw_data[key].value
        """
        curl -F "name=user" -F "password=test" http://localhost:8080/hello
        raw_data: FieldStorage(None, None, [FieldStorage('name', None, 'user'), FieldStorage('password', None, 'test')])
        <type 'instance'>
        key: password
        FieldStorage('password', None, 'test')
        <type 'instance'>
        raw_data[key].value
        key: name
        FieldStorage('name', None, 'user')
        <type 'instance'>
        raw_data[key].value
        
        curl -X POST -d "name=comewords&content=articleContent" http://localhost:8080/hello 
        raw_data: FieldStorage(None, None, [MiniFieldStorage('name', 'comewords'), MiniFieldStorage('content', 'articleContent')])
        <type 'instance'>
        key: content
        MiniFieldStorage('content', 'articleContent')
        <type 'instance'>
        raw_data[key].value
        key: name
        MiniFieldStorage('name', 'comewords')
        <type 'instance'>
        raw_data[key].value
        
        现在暂时不能同时上传文件和post参数
        curl -X POST -F "file=@/root/work/lanzw_frame/evolution/evolution_0001/static/ling.png" -d "name=comewords" http://localhost:8080/hello
        Warning: You can only select one HTTP request!
        
        curl -X POST -F "file=@/root/work/lanzw_frame/evolution/evolution_0001/static/ling.png" http://localhost:8080/hello
        <b>Error:</b> Internal server error.
        raw_data: FieldStorage(None, None, [FieldStorage('file', 'ling.png', '\x89PNG\r\n\x1a\n')])
        <type 'instance'>
        key: file
        FieldStorage('file', 'ling.png', '\x89PNG\r\n\x1a\n')
        <type 'instance'>
        filename: ling.png
        
        curl -X POST -F "name=@/root/work/lanzw_frame/evolution/evolution_0001/static/ling.png" http://localhost:8080/hello
        Hello FieldStorage('file', 'ling.png', '\x89PNG\r\n\x1a\n')!
        raw_data: FieldStorage(None, None, [FieldStorage('file', 'ling.png', '\x89PNG\r\n\x1a\n')])
        <type 'instance'>
        key: name
        FieldStorage('file', 'ling.png', '\x89PNG\r\n\x1a\n')
        <type 'instance'>
        filename: ling.png
        
        curl -X POST -H "Content-Type:application/json" -d '"name":"comewords","content":"articleContent"' http://localhost:8080/hello
        <b>Error:</b> Internal server error.
        raw_data: FieldStorage(None, None, '"name":"comewords","content":"articleContent"')
        <type 'instance'>
        Traceback (most recent call last):
          File "evolution_0006.py", line 479, in WSGIHandler
            global request
          File "evolution_0006.py", line 733, in say
          File "evolution_0006.py", line 245, in POST
            for key in raw_data:
          File "/usr/lib64/python2.7/cgi.py", line 517, in __iter__
            return iter(self.keys())
          File "/usr/lib64/python2.7/cgi.py", line 582, in keys
            raise TypeError, "not indexable"
        TypeError: not indexable

        Error (500) on '/hello': not indexable
        
        curl -F "name=user" -F "password=test1" -F "password=test2" -F "password=test3" http://localhost:8080/hello
        curl -F "name=user" -F "password=test" -F "password=test" -F "password=test" http://localhost:8080/hello
        <b>Error:</b> Internal server error.
        raw_data: FieldStorage(None, None, [FieldStorage('name', None, 'user'), FieldStorage('password', None, 'test'), FieldStorage('password', None, 'test'), FieldStorage('password', None, 'test')])
        <type 'instance'>
        key: password
        [FieldStorage('password', None, 'test'), FieldStorage('password', None, 'test'), FieldStorage('password', None, 'test')]
        <type 'list'>
        Traceback (most recent call last):
          File "evolution_0006.py", line 515, in WSGIHandler
            output = handler(**args)
          File "evolution_0006.py", line 769, in say
            name = request.POST['name']
          File "evolution_0006.py", line 249, in POST
            if raw_data[key].filename:
        AttributeError: 'list' object has no attribute 'filename'

        Error (500) on '/hello': 'list' object has no attribute 'filename'
        
        
        curl -X POST -d "name=comewords&content=articleContent1&content=articleContent2&content=articleContent3" http://localhost:8080/hello
        <b>Error:</b> Internal server error.
        raw_data: FieldStorage(None, None, [MiniFieldStorage('name', 'comewords'), MiniFieldStorage('content', 'articleContent1'), MiniFieldStorage('content', 'articleContent2'), MiniFieldStorage('content', 'articleContent3')])
        <type 'instance'>
        key: content
        [MiniFieldStorage('content', 'articleContent1'), MiniFieldStorage('content', 'articleContent2'), MiniFieldStorage('content', 'articleContent3')]
        <type 'list'>
        Traceback (most recent call last):
          File "evolution_0006.py", line 530, in WSGIHandler
            output = handler(**args)
          File "evolution_0006.py", line 784, in say
            name = request.POST['name']
          File "evolution_0006.py", line 249, in POST
            if raw_data[key].filename:
        AttributeError: 'list' object has no attribute 'filename'
        
        Error (500) on '/hello': 'list' object has no attribute 'filename'
        
        """
        return self._POST

    @property
    def params(self):  # 返回值有 bug
        ''' Returns a mix of GET and POST data. POST overwrites GET '''
        if self._GETPOST is None:
            self._GETPOST = dict(self.GET)
            self._GETPOST.update(self.POST)

    @property
    def COOKIES(self):
        """Returns a dict with COOKIES."""
        if self._COOKIES is None:
            raw_dict = Cookie.SimpleCookie(self._environ.get('HTTP_COOKIE', ''))
            self._COOKIES = {}
            for cookie in raw_dict.values():
                self._COOKIES[cookie.key] = cookie.value
        return self._COOKIES


# 暂时不需要继承 threading.local
# class Response(threading.local):
class Response():
    """ Represents a single response using thread-local namespace. """

    def bind(self):
        """ Clears old data and creates a brand new Response object """
        self._COOKIES = None

        self.status = 200
        self.header = HeaderDict()
        self.content_type = 'text/html'
        self.error = None

    @property
    def COOKIES(self):
        if not self._COOKIES:
            self._COOKIES = Cookie.SimpleCookie()
        return self._COOKIES

    def set_cookie(self, key, value, **kargs):
        """ Sets a Cookie. Optional settings: expires, path, comment, domain, max-age, secure, version, httponly """
        self.COOKIES[key] = value
        for k in kargs:
            self.COOKIES[key][k] = kargs[k]

    def get_content_type(self):
        '''Gives access to the 'Content-Type' header and defaults to 'text/html'.'''
        return self.header['Content-Type']

    def set_content_type(self, value):
        self.header['Content-Type'] = value

    content_type = property(get_content_type, set_content_type, None, get_content_type.__doc__)


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
    url = '/' + url.strip().lstrip("/")
    # Search for static routes first
    route = ROUTES_SIMPLE.get(method, {}).get(url, None)
    if route:
        return (route, {})

    # Now search regexp routes
    routes = ROUTES_REGEXP.get(method, [])
    for i in xrange(len(routes)):
        match = routes[i][0].match(url)
        if match:
            handler = routes[i][1]
            if i > 0 and OPTIMIZER and random.random() <= 0.001:
                # Every 1000 requests, we swap the matching route with its predecessor.
                # Frequently used routes will slowly wander up the list.
                routes[i - 1], routes[i] = routes[i], routes[i - 1]
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


# Error handling

def set_error_handler(code, handler):
    """ Sets a new error handler. """
    code = int(code)
    ERROR_HANDLER[code] = handler


def error(code=500):
    """ Decorator for error handler. Same as set_error_handler(code, handler)."""

    def wrapper(handler):
        set_error_handler(code, handler)
        return handler

    return wrapper


# Actual WSGI Stuff

def WSGIHandler(environ, start_response):
    """The bottle WSGI-handler."""
    global request
    global response
    print '\n\n 开始处理请求'
    print 'environ: {}'.format(environ)
    print 'request: {}'.format(id(request))
    print 'response: {}'.format(id(response))
    request.bind(environ)
    response.bind()
    try:
        print 'request.path: {} request.method: {}'.format(request.path, request.method)
        handler, args = match_url(request.path, request.method)
        print 'handler: {} args: {}'.format(handler, args)  # handler: <function say at 0x2189ed8> args: {'name': 'huzhi'}
        output = handler(**args)
        print 'output: {}'.format(output)  # output: Hello huzhi!
    except BreakTheBottle, shard:  # BreakTheBottle(open(filename, 'r'))
        output = shard.output
    except Exception, exception:  # 主要是 HTTPError 异常
        print traceback.format_exc()
        response.status = getattr(exception, 'http_status', 500)
        errorhandler = ERROR_HANDLER.get(response.status, None)
        if errorhandler:
            try:
                output = errorhandler(exception)
            except:
                output = "Exception within error handler! Application stopped."
        else:
            if DEBUG:
                output = "Exception %s: %s" % (exception.__class__.__name__, str(exception))
            else:
                output = "Unhandled exception: Application stopped."

        # 服务器内部错误处理办法，这个错误信息会打印到错误输出中，不会打印到客户端
        if response.status == 500:
            request._environ['wsgi.errors'].write("Error (500) on '%s': %s\n" % (request.path, exception))

    """
    到此为止 output 主要有以下三种类型：
    strings
    open(filename, 'r')
    yield
    """

    """
    if hasattr(output, 'read'):
        if 'wsgi.file_wrapper' in environ:
            output = environ['wsgi.file_wrapper'](output)
        else:
            output = iter(lambda: output.read(8192), '')

    if hasattr(output, '__len__') and 'Content-Length' not in response.header:
        response.header['Content-Length'] = len(output)
    """

    """
    这样计算出来的的长度更准确
    判断 Content-Length 是否存在可以防止覆盖框架使用者设置的 Content-Length 头信息
    有时框架使用者会自己设置 Content-Length 信息，此时不能覆盖
    """

    """
    if hasattr(output, 'fileno') and 'Content-Length' not in response.header:
        size = os.fstat(output.fileno()).st_size
        response.header['Content-Length'] = size
    """

    if hasattr(output, 'read'):
        fileoutput = output
        if 'wsgi.file_wrapper' in environ:
            output = environ['wsgi.file_wrapper'](fileoutput)
        else:
            output = iter(lambda: fileoutput.read(8192), '')

    for c in response.COOKIES.values():
        response.header.add('Set-Cookie', c.OutputString())

    status = '%d %s' % (response.status, HTTP_CODES[response.status])
    start_response(status, list(response.header.items()))
    return output


# Server adapter

class ServerAdapter(object):
    def __init__(self, host='127.0.0.1', port=8080, **kargs):
        self.host = host
        self.port = int(port)
        self.options = kargs

    def __repr__(self):
        return "%s (%s:%d)" % (self.__class__.__name__, self.host, self.port)

    def run(self, handler):
        pass


class WSGIRefServer(ServerAdapter):
    # server.run(WSGIHandler)
    def run(self, handler):
        from wsgiref.simple_server import make_server
        srv = make_server(self.host, self.port, handler)
        srv.serve_forever()


class CherryPyServer(ServerAdapter):
    # server.run(WSGIHandler)
    def run(self, handler):
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
        server.start()


class FlupServer(ServerAdapter):
    # server.run(WSGIHandler)
    def run(self, handler):
        from flup.server.fcgi import WSGIServer
        WSGIServer(handler, bindAddress=(self.host, self.port)).run()


class FapwsServer(ServerAdapter):
    """ Extreamly fast Webserver using libev (see http://william-os4y.livejournal.com/)
        Experimental ... """
    def run(self, handler):
        import fapws._evwsgi as evwsgi
        from fapws import base
        import sys
        evwsgi.start(self.host, self.port)
        evwsgi.set_base_module(base)
        def app(environ, start_response):
            environ['wsgi.multiprocess'] = False
            return handler(environ, start_response)
        evwsgi.wsgi_cb(('',app))
        evwsgi.run()


class PasteServer(ServerAdapter):
    # server.run(WSGIHandler)
    def run(self, handler):
        from paste import httpserver
        # httpserver.serve(handler, host=self.host, port=str(self.port))
        # Added access logging for PasterServer
        from paste.translogger import TransLogger
        app = TransLogger(handler)
        httpserver.serve(app, host=self.host, port=str(self.port))


# run(host='localhost', port=8080)
# run(host='localhost', port=8080, quiet=True)
# def run(server=WSGIRefServer, host='127.0.0.1', port=8080, **kargs):
def run(server=WSGIRefServer, host='127.0.0.1', port=8080, optinmize=False, **kargs):
    """ Runs bottle as a web server, using Python's built-in wsgiref implementation by default.

    You may choose between WSGIRefServer, CherryPyServer, FlupServer and
    PasteServer or write your own server adapter.
    """

    # Changed route optimisation to be turned off by default and added a switch to run() to turn it on again.
    global OPTIMIZER

    OPTIMIZER = bool(optinmize)

    quiet = bool('quiet' in kargs and kargs['quiet'])
    print 'quiet: {}'.format(quiet)

    # Instanciate server, if it is a class instead of an instance
    if isinstance(server, type) and issubclass(server, ServerAdapter):
        server = server(host=host, port=port, **kargs)

    if not isinstance(server, ServerAdapter):
        raise RuntimeError("Server must be a subclass of ServerAdapter")

    if not quiet:
        print 'Bottle server starting up (using %s)...' % repr(server)
        print 'Listening on http://%s:%d/' % (server.host, server.port)
        print 'Use Ctrl-C to quit.'
        print

    try:
        server.run(WSGIHandler)
    except KeyboardInterrupt:
        print "Shuting down..."


# Helper

def abort(code=500, text='Unknown Error: Appliction stopped.'):
    """ Aborts execution and causes a HTTP error. """
    raise HTTPError(code, text)


def redirect(url, code=307):
    """ Aborts execution and causes a 307 redirect """
    response.status = code
    response.header['Location'] = url
    raise BreakTheBottle("")


def send_file(filename, root, guessmime=True, mimetype='text/plain'):
    """ Aborts execution and sends a static files as response. """
    root = os.path.abspath(root) + '/'
    filename = os.path.normpath(filename).strip('/')
    filename = os.path.join(root, filename)

    if not filename.startswith(root):
        abort(401, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        abort(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        abort(401, "You do not have permission to access this file.")

    if guessmime:
        guess = mimetypes.guess_type(filename)[0]
        if guess:
            response.content_type = guess
        elif mimetype:
            response.content_type = mimetype
    elif mimetype:
        response.content_type = mimetype

    # TODO: Add Last-Modified header (Wed, 15 Nov 1995 04:58:08 GMT)
    stats = os.stat(filename)
    if 'Content-Length' not in response.header:
        response.header['Content-Length'] = stats.st_size
    if 'Last-Modified' not in response.header:
        ts = time.gmtime(stats.st_mtime)
        ts = time.strftime("%a, %d %b %Y %H:%M:%S +0000", ts)
        response.header['Last-Modified'] = ts

    raise BreakTheBottle(open(filename, 'r'))


# Default error handler

@error(500)
def error500(exception):
    """If an exception is thrown, deal with it and present an error page."""
    if DEBUG:
        return "<br>\n".join(traceback.format_exc(10).splitlines()).replace('  ', '&nbsp;&nbsp;')
    else:
        return """<b>Error:</b> Internal server error."""

"""
@error(404)
def error404(exception):
    yield '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
    yield '<html><head><title>Error 404: Not found</title>'
    yield '</head><body><h1>Error 404: Not found</h1>'
    yield '<p>The requested URL %s was not found on this server.</p>' % request.path
    yield '</body></html>'
"""

# 之所以能这样写是因为装饰器没有对 error_http 函数做任何操作，是原样返回 error_http 函数
@error(401)
@error(404)
def error_http(exception):
    status = response.status
    name = HTTP_CODES.get(status,'Unknown').title()
    url = request.path
    """If an exception is thrown, deal with it and present an error page."""
    yield '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
    yield '<html><head><title>Error %d: %s</title>' % (status, name)
    yield '</head><body><h1>Error %d: %s</h1>' % (status, name)
    yield '<p>Sorry, the requested URL %s caused an error.</p>' % url
    yield '</body></html>'

# Last but not least

request = Request()
response = Response()

if __name__ == "__main__":

    @route('/')
    def index():
        return 'Hello World!'

    @route('/hello/:name')
    def say(name):
        print request.GET
        return 'Hello %s!' % name

    @route('/hello', method='POST')
    def say():
        name = request.POST['name']
        return 'Hello %s!' % name

    print "\n\n"
    print "启动内置服务器"
    # run(host='localhost', port=8080)
    run(host='0.0.0.0', port=8080, quiet=True)
    # run(server=CherryPyServer, host='0.0.0.0', port=8080, quiet=False)
    # run(server=PasteServer, host='0.0.0.0', port=8080, quiet=False)
    # run(server=FlupServer, host='0.0.0.0', port=8080, quiet=False)

    """
    开始处理请求
    10.0.1.1 - - [31/Jul/2019 18:54:56] "GET /hello/huzhi HTTP/1.1" 200 12

    开始处理请求
    10.0.1.1 - - [31/Jul/2019 18:55:06] "GET /favicon.ico HTTP/1.1" 404 220
    
    curl 'http://localhost:8080/hello/huzhi'
    environ: {
    'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5', 
    'SCRIPT_NAME': '', 
    'REQUEST_METHOD': 'GET', 
    'SERVER_PROTOCOL': 'HTTP/1.1', 
    'HOME': '/root', 
    'LANG': 'en_US.UTF-8', 
    'SHELL': '/bin/bash', 
    'HISTSIZE': '1000', 
    'SERVER_PORT': '8080', 
    'XDG_RUNTIME_DIR': '/run/user/0', 
    'HTTP_HOST': '10.0.8.10:8080', 
    'HTTP_UPGRADE_INSECURE_REQUESTS': '1', 
    'HTTP_CACHE_CONTROL': 'max-age=0', 
    'XDG_SESSION_ID': '3', 
    'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', 
    'wsgi.version': (1, 0), 
    'wsgi.run_once': False, 
    'SSH_TTY': '/dev/pts/0', 
    'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7f58125951e0>, 
    'HOSTNAME': 'huzhi-code', 
    'HTTP_ACCEPT_LANGUAGE': 'zh-CN,zh;q=0.9', 
    'MAIL': '/var/spool/mail/root', 
    'LS_COLORS': '45:*.xspf=38;5;45:', 
    'PATH_INFO': '/hello/huzhi', 
    'wsgi.multiprocess': False, 
    'LESSOPEN': '||/usr/bin/lesspipe.sh %s', 
    'SSH_CLIENT': '10.0.1.1 65248 22', 
    'LOGNAME': 'root', 
    'USER': 'root', 
    'QUERY_STRING': '', 
    'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin', 
    'TERM': 'xterm-256color', 
    'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36', 
    'HTTP_CONNECTION': 'keep-alive', 
    'SERVER_NAME': 'huzhi-code', 
    'REMOTE_ADDR': '10.0.1.1', 
    'SHLVL': '1', 
    'wsgi.url_scheme': 'http', 
    'CONTENT_LENGTH': '', 
    'wsgi.input': <socket._fileobject object at 0x1fed0d0>, 
    'wsgi.multithread': True, 
    '_': '/usr/bin/python', 
    'SSH_CONNECTION': '10.0.1.1 65248 10.0.8.10 22', 
    'GATEWAY_INTERFACE': 'CGI/1.1', 
    'OLDPWD': '/root/work/lanzw_frame', 
    'HISTCONTROL': 'ignoredups', 
    'PWD': '/root/work/lanzw_frame/evolution', 
    'CONTENT_TYPE': 'text/plain', 
    'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x204bce8>, 
    'REMOTE_HOST': 'gateway', 
    'HTTP_ACCEPT_ENCODING': 'gzip, deflate'
    }
    
    curl 'http://localhost:8080/hello/huzhi?q=w&a=s'
    environ: 
    {
    'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5', 
    'SCRIPT_NAME': '', 
    'REQUEST_METHOD': 'GET', 
    'SERVER_PROTOCOL': 'HTTP/1.1', 
    'HOME': '/root', 
    'LANG': 'en_US.UTF-8', 
    'SHELL': '/bin/bash', 
    'HISTSIZE': '1000', 
    'SERVER_PORT': '8080', 
    'XDG_RUNTIME_DIR': '/run/user/0', 
    'HTTP_HOST': 'localhost:8080', 
    'XDG_SESSION_ID': '83', 
    'HTTP_ACCEPT': '*/*', 
    'wsgi.version': (1, 0), 
    'wsgi.run_once': False, 
    'SSH_TTY': '/dev/pts/0', 
    'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7f0e2a1071e0>, 
    'HOSTNAME': 'huzhi-code', 
    'MAIL': '/var/spool/mail/root', 
    'LS_COLORS': '',
    'PATH_INFO': '/hello/lanzhiwang', 
    'wsgi.multiprocess': False, 
    'LESSOPEN': '||/usr/bin/lesspipe.sh %s', 
    'SSH_CLIENT': '10.0.1.1 52315 22', 
    'LOGNAME': 'root', 
    'USER': 'root', 
    'QUERY_STRING': 'q=w&a=s', 
    'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin', 
    'TERM': 'xterm-256color', 
    'HTTP_USER_AGENT': 'curl/7.29.0', 
    'SERVER_NAME': 'huzhi-code', 
    'REMOTE_ADDR': '127.0.0.1', 
    'SHLVL': '1', 
    'wsgi.url_scheme': 'http', 
    'CONTENT_LENGTH': '', 
    'wsgi.input': <socket._fileobject object at 0x207a050>, 
    'wsgi.multithread': True, 
    '_': '/usr/bin/python', 
    'SSH_CONNECTION': '10.0.1.1 52315 10.0.8.10 22', 
    'GATEWAY_INTERFACE': 'CGI/1.1', 
    'OLDPWD': '/root/work/lanzw_frame/evolution/evolution_0001', 
    'HISTCONTROL': 'ignoredups', 
    'PWD': '/root/work/lanzw_frame/evolution/evolution_0006', 
    'CONTENT_TYPE': 'text/plain', 
    'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x20d3db8>, 
    'REMOTE_HOST': 'localhost.localdomain'
    }
    
    curl -F "name=user" -F "password=test" http://localhost:8080/hello
    environ: 
    {
    'SERVER_SOFTWARE': 'WSGIServer/0.1 Python/2.7.5', 
    'SCRIPT_NAME': '', 
    'REQUEST_METHOD': 'POST', 
    'SERVER_PROTOCOL': 'HTTP/1.1', 
    'HOME': '/root', 
    'LANG': 'en_US.UTF-8', 
    'SHELL': '/bin/bash', 
    'HISTSIZE': '1000', 
    'SERVER_PORT': '8080', 
    'XDG_RUNTIME_DIR': '/run/user/0', 
    'HTTP_HOST': 'localhost:8080', 
    'XDG_SESSION_ID': '83', 
    'HTTP_ACCEPT': '*/*', 
    'wsgi.version': (1, 0), 
    'wsgi.run_once': False, 
    'SSH_TTY': '/dev/pts/0', 
    'wsgi.errors': <open file '<stderr>', mode 'w' at 0x7f2594baa1e0>, 
    'HOSTNAME': 'huzhi-code', 
    'MAIL': '/var/spool/mail/root', 
    'LS_COLORS': 'rs=0:di=38;5;27:ln=38;5;51:mh=44;38;5;15:pi=40;38;5;11:so=38;5;13:do=38;5;5:bd=48;5;232;38;5;11:cd=48;5;232;38;5;3:or=48;5;232;38;5;9:mi=05;48;5;232;38;5;15:su=48;5;196;38;5;15:sg=48;5;11;38;5;16:ca=48;5;196;38;5;226:tw=48;5;10;38;5;16:ow=48;5;10;38;5;21:st=48;5;21;38;5;15:ex=38;5;34:*.tar=38;5;9:*.tgz=38;5;9:*.arc=38;5;9:*.arj=38;5;9:*.taz=38;5;9:*.lha=38;5;9:*.lz4=38;5;9:*.lzh=38;5;9:*.lzma=38;5;9:*.tlz=38;5;9:*.txz=38;5;9:*.tzo=38;5;9:*.t7z=38;5;9:*.zip=38;5;9:*.z=38;5;9:*.Z=38;5;9:*.dz=38;5;9:*.gz=38;5;9:*.lrz=38;5;9:*.lz=38;5;9:*.lzo=38;5;9:*.xz=38;5;9:*.bz2=38;5;9:*.bz=38;5;9:*.tbz=38;5;9:*.tbz2=38;5;9:*.tz=38;5;9:*.deb=38;5;9:*.rpm=38;5;9:*.jar=38;5;9:*.war=38;5;9:*.ear=38;5;9:*.sar=38;5;9:*.rar=38;5;9:*.alz=38;5;9:*.ace=38;5;9:*.zoo=38;5;9:*.cpio=38;5;9:*.7z=38;5;9:*.rz=38;5;9:*.cab=38;5;9:*.jpg=38;5;13:*.jpeg=38;5;13:*.gif=38;5;13:*.bmp=38;5;13:*.pbm=38;5;13:*.pgm=38;5;13:*.ppm=38;5;13:*.tga=38;5;13:*.xbm=38;5;13:*.xpm=38;5;13:*.tif=38;5;13:*.tiff=38;5;13:*.png=38;5;13:*.svg=38;5;13:*.svgz=38;5;13:*.mng=38;5;13:*.pcx=38;5;13:*.mov=38;5;13:*.mpg=38;5;13:*.mpeg=38;5;13:*.m2v=38;5;13:*.mkv=38;5;13:*.webm=38;5;13:*.ogm=38;5;13:*.mp4=38;5;13:*.m4v=38;5;13:*.mp4v=38;5;13:*.vob=38;5;13:*.qt=38;5;13:*.nuv=38;5;13:*.wmv=38;5;13:*.asf=38;5;13:*.rm=38;5;13:*.rmvb=38;5;13:*.flc=38;5;13:*.avi=38;5;13:*.fli=38;5;13:*.flv=38;5;13:*.gl=38;5;13:*.dl=38;5;13:*.xcf=38;5;13:*.xwd=38;5;13:*.yuv=38;5;13:*.cgm=38;5;13:*.emf=38;5;13:*.axv=38;5;13:*.anx=38;5;13:*.ogv=38;5;13:*.ogx=38;5;13:*.aac=38;5;45:*.au=38;5;45:*.flac=38;5;45:*.mid=38;5;45:*.midi=38;5;45:*.mka=38;5;45:*.mp3=38;5;45:*.mpc=38;5;45:*.ogg=38;5;45:*.ra=38;5;45:*.wav=38;5;45:*.axa=38;5;45:*.oga=38;5;45:*.spx=38;5;45:*.xspf=38;5;45:', 
    'PATH_INFO': '/hello', 
    'wsgi.multiprocess': False, 
    'LESSOPEN': '||/usr/bin/lesspipe.sh %s', 
    'SSH_CLIENT': '10.0.1.1 52315 22', 
    'LOGNAME': 'root', 
    'USER': 'root', 
    'QUERY_STRING': '', 
    'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin', 
    'TERM': 'xterm-256color', 
    'HTTP_USER_AGENT': 'curl/7.29.0', 
    'SERVER_NAME': 'huzhi-code', 
    'REMOTE_ADDR': '127.0.0.1', 
    'SHLVL': '1', 
    'wsgi.url_scheme': 'http', 
    'CONTENT_LENGTH': '143', 
    'wsgi.input': <socket._fileobject object at 0x1991050>, 
    'wsgi.multithread': True, 
    'HTTP_EXPECT': '100-continue', 
    '_': '/usr/bin/python', 
    'SSH_CONNECTION': '10.0.1.1 52315 10.0.8.10 22', 
    'GATEWAY_INTERFACE': 'CGI/1.1', 
    'OLDPWD': '/root/work/lanzw_frame/evolution/evolution_0001', 
    'HISTCONTROL': 'ignoredups', 
    'PWD': '/root/work/lanzw_frame/evolution/evolution_0006', 
    'CONTENT_TYPE': 'multipart/form-data; boundary=----------------------------16c2480e2eb2', 
    'wsgi.file_wrapper': <class wsgiref.util.FileWrapper at 0x19eadb8>, 
    'REMOTE_HOST': 'localhost.localdomain'
    }
    
    """