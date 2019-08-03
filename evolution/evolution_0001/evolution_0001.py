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
import re
import random
import Cookie
import threading

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

DEBUG = False
OPTIMIZER = True
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
            raw_dict = parse_qs(self.query, keep_blank_values=1)  # 好像有bug，不应该是 self.query，应该是 self.query_string
            self._GET = {}
            for key, value in raw_dict.items():
                if len(value) == 1:
                    self._GET[key] = value[0]
                else:
                    self._GET[key] = value
        return self._GET

    @property
    def POST(self):
        """Returns a dict with parsed POST data."""
        if self._POST is None:
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            self._POST = {}
            for key, value in raw_data:
                if value.filename:
                    self._POST[key] = value
                elif isinstance(value, list):
                    self._POST[key] = [v.value for v in value]
                else:
                    self._POST[key] = value.value
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
    # print 'environ: {}'.format(environ)
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

        # 服务器内部错误处理办法
        if response.status == 500:
            request._environ['wsgi.errors'].write("Error (500) on '%s': %s\n" % (request.path, exception))

    """
    到此为止 output 主要有以下三种类型：
    strings
    open(filename, 'r')
    yield
    """
    if hasattr(output, 'read'):
        if 'wsgi.file_wrapper' in environ:
            output = environ['wsgi.file_wrapper'](output)
        else:
            output = iter(lambda: output.read(8192), '')

    if hasattr(output, '__len__') and 'Content-Length' not in response.header:
        response.header['Content-Length'] = len(output)

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


class PasteServer(ServerAdapter):
    # server.run(WSGIHandler)
    def run(self, handler):
        from paste import httpserver
        httpserver.serve(handler, host=self.host, port=str(self.port))


# run(host='localhost', port=8080)
# run(host='localhost', port=8080, quiet=True)
def run(server=WSGIRefServer, host='127.0.0.1', port=8080, **kargs):
    """ Runs bottle as a web server, using Python's built-in wsgiref implementation by default.

    You may choose between WSGIRefServer, CherryPyServer, FlupServer and
    PasteServer or write your own server adapter.
    """

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
    raise BreakTheBottle(open(filename, 'r'))


# Default error handler

@error(500)
def error500(exception):
    """If an exception is thrown, deal with it and present an error page."""
    if DEBUG:
        return str(exception)
    else:
        return """<b>Error:</b> Internal server error."""


@error(404)
def error404(exception):
    """If an exception is thrown, deal with it and present an error page."""
    yield '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
    yield '<html><head><title>Error 404: Not found</title>'
    yield '</head><body><h1>Error 404: Not found</h1>'
    yield '<p>The requested URL %s was not found on this server.</p>' % request.path
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
    """