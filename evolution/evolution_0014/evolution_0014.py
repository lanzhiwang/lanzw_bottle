# -*- coding: utf-8 -*-
"""
https://github.com/bottlepy/bottle/commit/6365d98e0d3c6707ccbbabed9d36d98b166f71b5#diff-ad8cb2f640fd3a70db3fc97f3044a4e6

https://github.com/bottlepy/bottle/commits/master?before=357a0cb39cb8337f8467f5396e4b7caaa7e4f25c+910&path%5B%5D=bottle.py

"""

__author__ = 'Marcel Hellkamp'
__version__ = '0.5.8'
__license__ = 'MIT'

import threading
import re
import traceback
import random
import os


try:
    try:
        from json import dumps as json_dumps
    except ImportError:
        from simplejson import dumps as json_dumps
except ImportError:
    json_dumps = None


class BottleException(Exception):
    pass


class HTTPError(BottleException):
    def __init__(self, status, text):
        self.output = text
        self.http_status = int(status)

    def __repr__(self):
        return "HTTPError(%d,%s)" % (self.http_status, repr(self.output))

    def __str__(self):
        out = []
        status = self.http_status
        name = HTTP_CODES.get(status,'Unknown').title()
        url = request.path
        out.append('<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">')
        out.append('<html><head><title>Error %d: %s</title>' % (status, name))
        out.append('</head><body><h1>Error %d: %s</h1>' % (status, name))
        out.append('<p>Sorry, the requested URL "%s" caused an error.</p>' % url)
        out.append(''.join(list(self.output)))
        out.append('</body></html>')
        return "\n".join(out)


class BreakTheBottle(BottleException):
    def __init__(self, output):
        self.output = output


# WSGI abstraction: Request and response management

_default_app = None
def default_app(newapp = None):
    global _default_app
    if newapp:
        _default_app = newapp
    if not _default_app:
        _default_app = Bottle()
    return _default_app


class Bottle(object):

    def __init__(self, catchall=True, debug=False, optimize=False, autojson=True):
        self.simple_routes = {}
        self.regexp_routes = {}
        self.default_route = None
        self.error_handler = {}
        self.optimize = optimize
        self.debug = debug
        self.autojson = autojson
        self.catchall = catchall

    def match_url(self, url, method='GET'):
        url = url.strip().lstrip("/ ")
        # Search for static routes first
        route = self.simple_routes.get(method, {}).get(url, None)
        if route:
            return (route, {})

        routes = self.regexp_routes.get(method, [])
        for i in range(len(routes)):
            match = routes[i][0].match(url)
            if match:
                handler = routes[i][1]
                if i > 0 and self.optimize and random.random() <= 0.001:
                    routes[i - 1], routes[i] = routes[i], routes[i - 1]
                return (handler, match.groupdict())
        if self.default_route:
            return (self.default_route, {})
        return (None, None)


    #   add_controller(route, handler, method=method, simple=simple, **kargs)
    def add_controller(self, route, controller, **kargs):
        if '{action}' not in route and 'action' not in kargs:
            raise BottleException('Routes to controller classes or object MUST contain an {action} placeholder or use the action-parameter')
        for action in [m for m in dir(controller) if not m.startswith('_')]:
            handler = getattr(controller,action)
            if callable(handler) and action == kargs.get('action', action):
                self.add_route(route.replace('{action}',action), handler, **kargs)


    def add_route(self, route, handler, method='GET', simple=False, **kargs):
        """ Adds a new route to the route mappings. """
        if isinstance(handler, type) and issubclass(handler, BaseController):
            handler = handler()
        if isinstance(handler, BaseController):
            self.add_controller(route, handler, method=method, simple=simple, **kargs)
            return
        method = method.strip().upper()
        route = route.strip().lstrip('$^/ ').rstrip('$^ ')
        if re.match(r'^(\w+/)*\w*$', route) or simple:
            self.simple_routes.setdefault(method, {})[route] = handler
        else:
            route = re.sub(r':([a-zA-Z_]+)(?P<uniq>[^\w/])(?P<re>.+?)(?P=uniq)',r'(?P<\1>\g<re>)',route)
            route = re.sub(r':([a-zA-Z_]+)',r'(?P<\1>[^/]+)', route)
            route = re.compile('^%s$' % route)
            self.regexp_routes.setdefault(method, []).append([route, handler])


    def route(self, url, **kargs):
        """ Decorator for request handler. Same as add_route(url, handler, **kargs)."""
        def wrapper(handler):
            self.add_route(url, handler, **kargs)
            return handler
        return wrapper

    def set_default(self, handler):
        self.default_route = handler

    def default(self):
        """ Decorator for request handler. Same as add_defroute( handler )."""
        def wrapper(handler):
            self.set_default(handler)
            return handler
        return wrapper

    def set_error_handler(self, code, handler):
        """ Adds a new error handler. """
        code = int(code)
        self.error_handler[code] = handler

    def error(self, code=500):
        """ Decorator for error handler. Same as set_error_handler(code, handler)."""
        def wrapper(handler):
            self.set_error_handler(code, handler)
            return handler
        return wrapper

    def __call__(self, environ, start_response):
        request.bind(environ)
        response.bind()
        try:
            try:
                handler, args = self.match_url(request.path, request.method)
                if not handler:
                    raise HTTPError(404, "Not found")
                output = handler(**args)
                db.close()
            except BreakTheBottle, e:
                output = e.output
            except HTTPError, e:
                response.status = e.http_status
                output = self.error_handler.get(response.status, str)(e)
            if hasattr(output, 'read'):
                output = environ.get('wsgi.file_wrapper',
                  lambda x: iter(lambda: x.read(8192), ''))(output)
            elif self.autojson and json_dumps and isinstance(output, dict):
                output = json_dumps(output)
                response.content_type = 'application/json'
            if isinstance(output, str):
                response.header['Content-Length'] = str(len(output))
                output = [output]
            if not hasattr(output, '__iter__'):
                raise TypeError('Request handler for route "%s" returned [%s],\
                which is not iterable.' % (request.path, type(output).__name__))

        except (KeyboardInterrupt, SystemExit, MemoryError):
            pass
        except Exception, e:
            response.status = 500
            if self.catchall:
                err = "Unhandled Exception: %s\n" % (repr(e))
                if self.debug:
                    err += "<h2>Traceback:</h2>\n<pre>\n"
                    err += traceback.format_exc(10)
                    err += "\n</pre>"
                output = str(HTTPError(500, err))
                request._environ['wsgi.errors'].write(err)
            else:
                raise
        status = '%d %s' % (response.status, HTTP_CODES[response.status])
        start_response(status, response.wsgiheaders())
        return output





class Request(threading.local):
    pass


class Response(threading.local):
    pass


class BaseController(object):
    _singleton = None

    def __new__(cls, *a, **k):
        if not cls._singleton:
            cls._singleton = object.__new__(cls, *a, **k)
        return cls._singleton


def abort(code=500, text='Unknown Error: Appliction stopped.'):
    pass


def redirect(url, code=307):
    pass


def send_file(filename, root, guessmime = True, mimetype = 'text/plain'):
    pass


# Decorators

def validate(**vkargs):
    pass


def route(url, **kargs):
    return default_app().route(url, **kargs)


def default():
    pass


def error(code=500):
    pass



# Server adapter
"""
            object
          WSGIAdapter
CGIServer             ServerAdapter
             WSGIRefServer CherryPyServer ...
"""



class WSGIAdapter(object):
    pass


class CGIServer(WSGIAdapter):
    pass


class ServerAdapter(WSGIAdapter):
    pass


class WSGIRefServer(ServerAdapter):
    pass


class CherryPyServer(ServerAdapter):
    pass


class FlupServer(ServerAdapter):
    pass


class PasteServer(ServerAdapter):
    pass


class FapwsServer(ServerAdapter):
    pass


def run(app=None, server=WSGIRefServer, host='127.0.0.1', port=8080,
        interval=2, reloader=False,  **kargs):
    if not app:
        app = default_app()

    quiet = bool('quiet' in kargs and kargs['quiet'])

    # Instantiate server, if it is a class instead of an instance
    if isinstance(server, type):
        if issubclass(server, CGIServer):
            server = server()
        elif issubclass(server, ServerAdapter):
            server = server(host=host, port=port, **kargs)

    if not isinstance(server, WSGIAdapter):
        raise RuntimeError("Server must be a subclass of WSGIAdapter")

    if not quiet and isinstance(server, ServerAdapter):
        if not reloader or os.environ.get('BOTTLE_CHILD') == 'true':
            print 'Bottle server starting up (using %s)...' % repr(server)
            print 'Listening on http://%s:%d/' % (server.host, server.port)
            print 'Use Ctrl-C to quit.'
            print
        else:
            print 'Bottle auto reloader starting up...'

    try:
        if reloader and interval:
            pass
        else:
            server.run(app)
    except KeyboardInterrupt:
        print 'Shutting Down...'



# Templates

class BaseTemplate(object):
    pass


class MakoTemplate(BaseTemplate):
    pass


class CheetahTemplate(BaseTemplate):
    pass


class SimpleTemplate(BaseTemplate):
    pass


def template(template, template_adapter=SimpleTemplate, **args):
    pass


def mako_template(template_name, **args):
    pass


def cheetah_template(template_name, **args):
    pass



# Database

class BottleBucket(object):
    pass


class BottleDB(threading.local):
    pass



# Modul initialization and configuration

DB_PATH = './'
TEMPLATE_PATH = ['./%s.tpl', './views/%s.tpl']
TEMPLATES = {}
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

request = Request()
response = Response()
db = BottleDB()
local = threading.local()

def debug(mode=True):
    default_app().debug = bool(mode)

def optimize(mode=True):
    default_app().optimize = bool(mode)
