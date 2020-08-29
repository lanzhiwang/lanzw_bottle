"""
bottle.py is a one-file micro web framework inspired by itty.py (Daniel Lindsley)

Licence (MIT)
-------------

    Copyright (c) 2009, Marcel Hellkamp.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.


Example
-------

    from bottle import route, run, request, response

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

    run(host='localhost', port=8080)

"""

__author__ = 'Marcel Hellkamp'
__version__ = ('0', '3', '2')
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
ERROR_HANDLER = {}
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
    def __init__(self, output):  # BreakTheBottle(open(filename, 'r'))
        self.output = output






# Classes

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

    def get(self, key):
        return dict.get(self, key.title())

    def items(self):
        """ Returns a list of (key, value) tuples """
        for key, values in dict.items(self):
            if not isinstance(values, list):
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


class Request(threading.local):
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
            raw_dict = parse_qs(self.query, keep_blank_values=1)
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
    def params(self):
        ''' Returns a mix of GET and POST data. POST overwrites GET '''
        if self._GETPOST is None:
            self._GETPOST = dict(self.GET)
            self._GETPOST.update(self.POST)

    @property
    def COOKIES(self):
        """Returns a dict with COOKIES."""
        if self._COOKIES is None:
            raw_dict = Cookie.SimpleCookie(self._environ.get('HTTP_COOKIE',''))
            self._COOKIES = {}
            for cookie in raw_dict.values():
                self._COOKIES[cookie.key] = cookie.value
        return self._COOKIES


class Response(threading.local):
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
    print(route)
    route = route.strip().lstrip('$^/ ').rstrip('$^ ')
    print(route)
    route = re.sub(
        r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)',
        r'(?P<\1>\g<re>)',
        route)
    print(route)
    route = re.sub(
        r':([a-zA-Z_]+)',
        r'(?P<\1>[^/]+)',
        route)
    print(route)
    return re.compile('^/%s$' % route)

# for route in ['/user/(?P<id>[0-9]+)', '/user/:id/:action', '/user/:id#[0-9]+#']:
#     compile_route(route)
#     print()
"""
/user/(?P<id>[0-9]+)
user/(?P<id>[0-9]+)
user/(?P<id>[0-9]+)
user/(?P<id>[0-9]+)
()
/user/:id/:action
user/:id/:action
user/:id/:action
user/(?P<id>[^/]+)/(?P<action>[^/]+)
()
/user/:id#[0-9]+#
user/:id#[0-9]+#
user/(?P<id>[0-9]+)
user/(?P<id>[0-9]+)
()
"""



import re

regex = re.compile(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)')

for route in ['user/(?P<id>[0-9]+)', 'user/:id/:action', 'user/:id#[0-9]+#']:
    print(route)
    match = regex.match(route)
    print('  ', match.groups())
    print()





def match_url(url, method='GET'):
    """Returns the first matching handler and a parameter dict or raises HTTPError(404).
    
    This reorders the ROUTING_REGEXP list every 1000 requests. To turn this off, use OPTIMIZER=False"""
    url = '/' + url.strip().lstrip("/")
    # Search for static routes first
    # {'POST': {'/': <function index at 0x23137d0>}}
    route = ROUTES_SIMPLE.get(method,{}).get(url,None)
    if route:
      return (route, {})
    
    # Now search regexp routes
    # {'GET': [[<_sre.SRE_Pattern object at 0x22cb200>, <function say at 0x23138c0>]]}
    routes = ROUTES_REGEXP.get(method,[])
    for i in xrange(len(routes)):
        match = routes[i][0].match(url)
        if match:
            handler = routes[i][1]
            if i > 0 and OPTIMIZER and random.random() <= 0.001:
                # Every 1000 requests, we swap the matching route with its predecessor.
                # Frequently used routes will slowly wander up the list.
                routes[i-1], routes[i] = routes[i], routes[i-1]
            return handler, match.groupdict()
    raise HTTPError(404, "Not found")


def add_route(route, handler, method='GET', simple=False):
    """ Adds a new route to the route mappings.

        Example:
        def hello():
          return "Hello world!"
        add_route(r'/hello', hello)"""
    method = method.strip().upper()
    print(method)
    print(re.match(r'^/(\w+/)*\w*$', route))
    if re.match(r'^/(\w+/)*\w*$', route) or simple:
        print(ROUTES_SIMPLE)
        ROUTES_SIMPLE.setdefault(method, {})[route] = handler
        print(ROUTES_SIMPLE)
    else:
        route = compile_route(route)
        print(route)
        print(ROUTES_REGEXP)
        ROUTES_REGEXP.setdefault(method, []).append([route, handler])
        print(ROUTES_REGEXP)


def route(url, **kargs):
    """ Decorator for request handler. Same as add_route(url, handler)."""
    def wrapper(handler):
        add_route(url, handler, **kargs)
        return handler
    return wrapper

"""
@route('/')
def index():
    return 'Hello World!'

@route('/hello/:name')
def say(name):
    return 'Hello %s!' % name
"""

# def index():
#     return 'Hello World!'
# wrapper = route('/', method='POST')
# index = wrapper(index)

# def say(name):
#     return 'Hello %s!' % name
# wrapper = route('/hello/:name', method='get')
# say = wrapper(say)

"""
[root@lanzhiwang-centos7 evolution_01]# python bottle.py
POST
<_sre.SRE_Match object at 0x23138a0>
{}
{'POST': {'/': <function index at 0x23137d0>}}
GET
None
<_sre.SRE_Pattern object at 0x22cb200>
{}
{'GET': [[<_sre.SRE_Pattern object at 0x22cb200>, <function say at 0x23138c0>]]}
[root@lanzhiwang-centos7 evolution_01]#
"""

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


# Default error handler

# @error(500)
def error500(exception):
    """If an exception is thrown, deal with it and present an error page."""
    if DEBUG:
        return str(exception)
    else:
        return """<b>Error:</b> Internal server error."""

# wrapper = error(500)
# error500 = wrapper(error500)


# @error(404)
def error404(exception):
    """If an exception is thrown, deal with it and present an error page."""
    yield '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
    yield '<html><head><title>Error 404: Not found</title>'
    yield '</head><body><h1>Error 404: Not found</h1>'
    yield '<p>The requested URL %s was not found on this server.</p>' % request.path
    yield '</body></html>'

wrapper = error(404)
error404 = wrapper(error404)
# print(ERROR_HANDLER) # {404: <function error404 at 0x1d6d9b0>, 500: <function error500 at 0x1d6d8c0>}














# Last but not least

request = Request()
response = Response()


# Actual WSGI Stuff

def WSGIHandler(environ, start_response):
    """The bottle WSGI-handler."""
    global request
    global response
    print(request)
    print(response)
    request.bind(environ)
    response.bind()
    try:
        print(request.path, request.method)
        handler, args = match_url(request.path, request.method)
        output = handler(**args)
    except BreakTheBottle as shard:  # redirect send_file
        output = shard.output
    except Exception as exception:
        response.status = getattr(exception, 'http_status', 500)
        print(response.status)
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

        if response.status == 500:
            request._environ['wsgi.errors'].write("Error (500) on '%s': %s\n" % (request.path, exception))
    print(output)

    print(hasattr(output, 'read'))
    if hasattr(output, 'read'):  # send_file
        if 'wsgi.file_wrapper' in environ:
            output = environ['wsgi.file_wrapper'](output)
        else:
            output =  iter(lambda: output.read(8192), '')

    print(hasattr(output, '__len__'))
    if hasattr(output, '__len__') and 'Content-Length' not in response.header:
        response.header['Content-Length'] = len(output)

    for c in response.COOKIES.values():
      response.header.add('Set-Cookie', c.OutputString())

    status = '%d %s' % (response.status, HTTP_CODES[response.status])
    start_response(status, list(response.header.items()))
    print(output)
    return output

"""
[root@lanzhiwang-centos7 evolution_01]# python bottle.py
Bottle server starting up (using WSGIRefServer (localhost:8080))...
Listening on http://localhost:8080/
Use Ctrl-C to quit.

<__main__.Request object at 0x12fd600>
<__main__.Response object at 0x12fdb48>
('/', 'GET')
404
<generator object error404 at 0x13649b0>
False
False
<generator object error404 at 0x13649b0>
127.0.0.1 - - [28/Aug/2020 20:05:26] "GET / HTTP/1.1" 404 209
^CShuting down...
[root@lanzhiwang-centos7 evolution_01]#
"""





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
    def run(self, handler):
        from wsgiref.simple_server import make_server
        srv = make_server(self.host, self.port, handler)
        srv.serve_forever()


class CherryPyServer(ServerAdapter):
    def run(self, handler):
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((self.host, self.port), handler)
        server.start()


class FlupServer(ServerAdapter):
    def run(self, handler):
       from flup.server.fcgi import WSGIServer
       WSGIServer(handler, bindAddress=(self.host, self.port)).run()


class PasteServer(ServerAdapter):
    def run(self, handler):
        from paste import httpserver
        httpserver.serve(handler, host=self.host, port=str(self.port))


def run(server=WSGIRefServer, host='127.0.0.1', port=8080, **kargs):
    """ Runs bottle as a web server, using Python's built-in wsgiref implementation by default.
    
    You may choose between WSGIRefServer, CherryPyServer, FlupServer and
    PasteServer or write your own server adapter.
    """

    quiet = bool('quiet' in kargs and kargs['quiet'])

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

# run(host='localhost', port=8080, quiet=False)




# Helper

def abort(code=500, text='Unknown Error: Appliction stopped.'):
    """ Aborts execution and causes a HTTP error. """
    raise HTTPError(code, text)


def redirect(url, code=307):
    """ Aborts execution and causes a 307 redirect """
    response.status = code
    response.header['Location'] = url
    raise BreakTheBottle("")


def send_file(filename, root, guessmime = True, mimetype = 'text/plain'):
    """ Aborts execution and sends a static files as response. """
    print(filename, root)  # ('bottle.py', '')
    root = os.path.abspath(root) + '/'
    filename = os.path.normpath(filename).strip('/')
    filename = os.path.join(root, filename)
    print(filename, root)
    # ('/root/work/code/lanzw_bottle/evolution/evolution_01/bottle.py', '/root/work/code/lanzw_bottle/evolution/evolution_01/')

    if not filename.startswith(root):
        abort(401, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        abort(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        abort(401, "You do not have permission to access this file.")

    # fp = open(filename, 'r')
    # print(hasattr(fp, 'read'))  # True

    if guessmime:
        # print(mimetypes.guess_type(filename))  # ('text/x-python', None)
        guess = mimetypes.guess_type(filename)[0]
        if guess:
            response.content_type = guess
        elif mimetype:
            response.content_type = mimetype
    elif mimetype:
        response.content_type = mimetype

    # TODO: Add Last-Modified header (Wed, 15 Nov 1995 04:58:08 GMT)
    raise BreakTheBottle(open(filename, 'r'))


basename = os.path.basename(__file__)
root = os.path.dirname(__file__)
send_file(basename, root)



# len(__file__) == 600  :D
