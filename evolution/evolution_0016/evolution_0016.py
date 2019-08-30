# -*- coding: utf-8 -*-
"""

"""


__author__ = 'Marcel Hellkamp'
__version__ = '0.9.dev'
__license__ = 'MIT'

import base64
import sys
import cgi
import threading
import warnings
from urllib import quote as urlquote
from urlparse import urlunsplit
import functools
from tempfile import TemporaryFile
from Cookie import SimpleCookie
import hmac


try:
    from collections import MutableMapping as DictMixin
except ImportError: # pragma: no cover
    from UserDict import DictMixin

try: from urlparse import parse_qs
except ImportError: # pragma: no cover
    from cgi import parse_qs

try: import cPickle as pickle
except ImportError: # pragma: no cover
    import pickle

try:
    from json import dumps as json_dumps
except ImportError: # pragma: no cover
    try:
        from simplejson import dumps as json_dumps
    except ImportError: # pragma: no cover
        try:
            from django.utils.simplejson import dumps as json_dumps
        except ImportError: # pragma: no cover
            json_dumps = None


if sys.version_info >= (3,0,0): # pragma: no cover
    # See Request.POST
    from io import BytesIO
    from io import TextIOWrapper

    # NCTextIOWrapper(self.body, encoding='ISO-8859-1', newline='\n')
    class NCTextIOWrapper(TextIOWrapper):
        ''' Garbage collecting an io.TextIOWrapper(buffer) instance closes the
            wrapped buffer. This subclass keeps it open. '''
        def close(self): pass
    def touni(x, enc='utf8'):
        """ Convert anything to unicode """
        return str(x, encoding=enc) if isinstance(x, bytes) else str(x)
else:
    from StringIO import StringIO as BytesIO
    bytes = str
    NCTextIOWrapper = None
    def touni(x, enc='utf8'):
        """ Convert anything to unicode """
        return x if isinstance(x, unicode) else unicode(str(x), encoding=enc)

def tob(data, enc='utf8'):
    """ Convert anything to bytes """
    return data.encode(enc) if isinstance(data, unicode) else bytes(data)

# Convert strings and unicode to native strings
if sys.version_info >= (3,0,0):
    tonat = touni
else:
    tonat = tob
tonat.__doc__ = """ Convert anything to native strings """





# Backward compatibility
# depr("Request._environ renamed to Request.environ")
def depr(message, critical=False):
    if critical:
        raise DeprecationWarning(message)
    warnings.warn(message, DeprecationWarning, stacklevel=3)


# Small helpers

def makelist(data):
    pass


class DictProperty(object):

    # DictProperty('environ', 'bottle.headers', read_only=True)
    def __init__(self, attr, key=None, read_only=False):
        self.attr = attr
        self.key = key
        self.read_only = read_only

    """
    d = DictProperty('environ', 'bottle.headers', read_only=True)
    headers = d(headers)
    """
    def __call__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter = func
        self.key = self.key or func.__name__
        return self

    def __get__(self, obj, cls):
        if not obj:
            return self
        key = self.key
        storage = getattr(obj, self.attr)
        if key not in storage:
            storage[key] = self.getter(obj)
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
    pass


class lazy_attribute(object):
    pass


###############################################################################
# Exceptions and Events ########################################################
###############################################################################

class BottleException(Exception):
    pass


class HTTPResponse(BottleException):
    pass


class HTTPError(HTTPResponse):
    pass


###############################################################################
# Routing ######################################################################
###############################################################################

class RouteError(BottleException):
    pass


class RouteSyntaxError(RouteError):
    pass


class RouteBuildError(RouteError):
    pass

class Router(object):
    pass


###############################################################################
# Application Object ###########################################################
###############################################################################

class Bottle(object):
    def __init__(self, catchall=True, autojson=True, config=None):
        self.routes = []
        self.callbacks = {}
        self.router = Router()

        self.mounts = {}
        self.error_handler = {}
        self.catchall = catchall
        self.config = config or {}
        self.serve = True
        self.castfilter = []
        if autojson and json_dumps:
            self.add_filter(dict, dict2json)
        self.hooks = {'before_request': [], 'after_request': []}

    def optimize(self, *a, **ka):
        depr("Bottle.optimize() is obsolete.")

    def mount(self, app, script_path):
        ''' Mount a Bottle application to a specific URL prefix '''
        if not isinstance(app, Bottle):
            raise TypeError('Only Bottle instances are supported for now.')
        script_path = '/'.join(filter(None, script_path.split('/')))
        path_depth = script_path.count('/') + 1
        if not script_path:
            raise TypeError('Empty script_path. Perhaps you want a merge()?')
        for other in self.mounts:
            if other.startswith(script_path):
                raise TypeError('Conflict with existing mount: %s' % other)
        @self.route('/%s/:#.*#' % script_path, method="ANY")
        def mountpoint():
            request.path_shift(path_depth)
            return app.handle(request.environ)
        self.mounts[script_path] = app

    def handle(self, environ):
        """ Execute the handler bound to the specified url and method and return
        its output. If catchall is true, exceptions are catched and returned as
        HTTPError(500) objects. """
        if not self.serve:
            return HTTPError(503, "Server stopped")
        try:
            handler, args = self.match(environ)
            return handler(**args)
        except HTTPResponse, e:
            return e
        except Exception, e:
            if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError))\
            or not self.catchall:
                raise
            return HTTPError(500, 'Unhandled exception', e, format_exc(10))

    def _cast(self, out, request, response, peek=None):
        """ Try to convert the parameter into something WSGI compatible and set
        correct HTTP headers when possible.
        Support: False, str, unicode, dict, HTTPResponse, HTTPError, file-like,
        iterable of strings and iterable of unicodes
        """
        # Filtered types (recursive, because they may return anything)
        for testtype, filterfunc in self.castfilter:
            if isinstance(out, testtype):
                return self._cast(filterfunc(out), request, response)

        # Empty output is done here
        if not out:
            response.headers['Content-Length'] = 0
            return []
        # Join lists of byte or unicode strings. Mixed lists are NOT supported
        if isinstance(out, (tuple, list))\
        and isinstance(out[0], (bytes, unicode)):
            out = out[0][0:0].join(out) # b'abc'[0:0] -> b''
        # Encode unicode strings
        if isinstance(out, unicode):
            out = out.encode(response.charset)
        # Byte Strings are just returned
        if isinstance(out, bytes):
            response.headers['Content-Length'] = str(len(out))
            return [out]
        # HTTPError or HTTPException (recursive, because they may wrap anything)
        if isinstance(out, HTTPError):
            out.apply(response)
            return self._cast(self.error_handler.get(out.status, repr)(out), request, response)
        if isinstance(out, HTTPResponse):
            out.apply(response)
            return self._cast(out.output, request, response)

        # File-like objects.
        if hasattr(out, 'read'):
            if 'wsgi.file_wrapper' in request.environ:
                return request.environ['wsgi.file_wrapper'](out)
            elif hasattr(out, 'close') or not hasattr(out, '__iter__'):
                return WSGIFileWrapper(out)

        # Handle Iterables. We peek into them to detect their inner type.
        try:
            out = iter(out)
            first = out.next()
            while not first:
                first = out.next()
        except StopIteration:
            return self._cast('', request, response)
        except HTTPResponse, e:
            first = e
        except Exception, e:
            first = HTTPError(500, 'Unhandled exception', e, format_exc(10))
            if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError))\
            or not self.catchall:
                raise
        # These are the inner types allowed in iterator or generator objects.
        if isinstance(first, HTTPResponse):
            return self._cast(first, request, response)
        if isinstance(first, bytes):
            return itertools.chain([first], out)
        if isinstance(first, unicode):
            return itertools.imap(lambda x: x.encode(response.charset),
                                  itertools.chain([first], out))
        return self._cast(HTTPError(500, 'Unsupported response type: %s'\
                                         % type(first)), request, response)

    def wsgi(self, environ, start_response):
        """ The bottle WSGI-interface. """
        try:
            environ['bottle.app'] = self
            request.bind(environ)
            response.bind()
            out = self.handle(environ)
            out = self._cast(out, request, response)
            # rfc2616 section 4.3
            if response.status in (100, 101, 204, 304) or request.method == 'HEAD':
                if hasattr(out, 'close'): out.close()
                out = []
            status = '%d %s' % (response.status, HTTP_CODES[response.status])
            start_response(status, response.headerlist)
            return out
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            if not self.catchall: raise
            err = '<h1>Critical error while processing request: %s</h1>' \
                  % environ.get('PATH_INFO', '/')
            if DEBUG:
                err += '<h2>Error:</h2>\n<pre>%s</pre>\n' % repr(e)
                err += '<h2>Traceback:</h2>\n<pre>%s</pre>\n' % format_exc(10)
            environ['wsgi.errors'].write(err) #TODO: wsgi.error should not get html
            start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html')])
            return [tob(err)]

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)


    def hander_wsgi(self, environ, start_response):
        # return self.wsgi(environ, start_response)
        try:
            environ['bottle.app'] = self
            request.bind(environ)
            response.bind()

            ###########################################################
            # out = self.handle(environ)
            if not self.serve:
                out = HTTPError(503, "Server stopped")

            try:
                handler, args = self.match(environ)
                out = handler(**args)
            except HTTPResponse, e:
                out = e
            except Exception, e:
                if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError)) or not self.catchall:
                    raise
                out = HTTPError(500, 'Unhandled exception', e, format_exc(10))
            ###########################################################

            ###########################################################
            # out = self._cast(out, request, response)

            for testtype, filterfunc in self.castfilter:
                if isinstance(out, testtype):
                    return self._cast(filterfunc(out), request, response)

            # Empty output is done here
            if not out:
                response.headers['Content-Length'] = 0
                return []
            # Join lists of byte or unicode strings. Mixed lists are NOT supported
            if isinstance(out, (tuple, list)) and isinstance(out[0], (bytes, unicode)):
                out = out[0][0:0].join(out)  # b'abc'[0:0] -> b''
            # Encode unicode strings
            if isinstance(out, unicode):
                out = out.encode(response.charset)
            # Byte Strings are just returned
            if isinstance(out, bytes):
                response.headers['Content-Length'] = str(len(out))
                return [out]
            # HTTPError or HTTPException (recursive, because they may wrap anything)
            if isinstance(out, HTTPError):
                out.apply(response)
                return self._cast(self.error_handler.get(out.status, repr)(out), request, response)
            if isinstance(out, HTTPResponse):
                out.apply(response)
                return self._cast(out.output, request, response)

            # File-like objects.
            if hasattr(out, 'read'):
                if 'wsgi.file_wrapper' in request.environ:
                    return request.environ['wsgi.file_wrapper'](out)
                elif hasattr(out, 'close') or not hasattr(out, '__iter__'):
                    return WSGIFileWrapper(out)

            # Handle Iterables. We peek into them to detect their inner type.
            try:
                out = iter(out)
                first = out.next()
                while not first:
                    first = out.next()
            except StopIteration:
                return self._cast('', request, response)
            except HTTPResponse, e:
                first = e
            except Exception, e:
                first = HTTPError(500, 'Unhandled exception', e, format_exc(10))
                if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError)) \
                        or not self.catchall:
                    raise
            # These are the inner types allowed in iterator or generator objects.
            if isinstance(first, HTTPResponse):
                return self._cast(first, request, response)
            if isinstance(first, bytes):
                return itertools.chain([first], out)
            if isinstance(first, unicode):
                return itertools.imap(lambda x: x.encode(response.charset),
                                      itertools.chain([first], out))
            return self._cast(HTTPError(500, 'Unsupported response type: %s' \
                                        % type(first)), request, response)

            ###########################################################



            # rfc2616 section 4.3
            if response.status in (100, 101, 204, 304) or request.method == 'HEAD':
                if hasattr(out, 'close'): out.close()
                out = []
            status = '%d %s' % (response.status, HTTP_CODES[response.status])
            start_response(status, response.headerlist)
            return out
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            if not self.catchall: raise
            err = '<h1>Critical error while processing request: %s</h1>' \
                  % environ.get('PATH_INFO', '/')
            if DEBUG:
                err += '<h2>Error:</h2>\n<pre>%s</pre>\n' % repr(e)
                err += '<h2>Traceback:</h2>\n<pre>%s</pre>\n' % format_exc(10)
            environ['wsgi.errors'].write(err) #TODO: wsgi.error should not get html
            start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html')])
            return [tob(err)]







###############################################################################
# HTTP and WSGI Tools ##########################################################
###############################################################################

class Request(threading.local, DictMixin):
    def __init__(self, environ=None):
        self.bind(environ or {}, )

    def bind(self, environ):
        self.environ = environ
        # These attributes are used anyway, so it is ok to compute them here
        self.path = '/' + environ.get('PATH_INFO', '/').lstrip('/')
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def _environ(self):
        depr("Request._environ renamed to Request.environ")
        return self.environ

    def copy(self):
        return Request(self.environ.copy())

    def path_shift(self, shift=1):
        script_name = self.environ.get('SCRIPT_NAME','/')
        self['SCRIPT_NAME'], self.path = path_shift(script_name, self.path, shift)
        self['PATH_INFO'] = self.path

    def __getitem__(self, key):
        return self.environ[key]

    def __delitem__(self, key):
        self[key] = ""
        del(self.environ[key])

    def __iter__(self):
        return iter(self.environ)

    def __len__(self):
        return len(self.environ)

    def keys(self):
        return self.environ.keys()

    def __setitem__(self, key, value):
        """ Shortcut for Request.environ.__setitem__ """
        self.environ[key] = value
        todelete = []
        if key in ('PATH_INFO', 'REQUEST_METHOD'):
            self.bind(self.environ)
        elif key == 'wsgi.input':
            todelete = ('body', 'forms', 'files', 'params')
        elif key == 'QUERY_STRING':
            todelete = ('get', 'params')
        elif key.startswith('HTTP_'):
            todelete = ('headers', 'cookies')

        for key in todelete:
            if 'bottle.' + key in self.environ:
                del self.environ['bottle.' + key]

    @property
    def query_string(self):
        """ The part of the URL following the '?'. """
        return self.environ.get('QUERY_STRING', '')

    @property
    def fullpath(self):
        """ Request path including SCRIPT_NAME (if present). """
        return self.environ.get('SCRIPT_NAME', '').rstrip('/') + self.path

    @property
    def url(self):
        scheme = self.environ.get('wsgi.url_scheme', 'http')
        host = self.environ.get('HTTP_X_FORWARDED_HOST')
        host = host or self.environ.get('HTTP_HOST', None)
        if not host:
            host = self.environ.get('SERVER_NAME')
            port = self.environ.get('SERVER_PORT', '80')
            if (scheme, port) not in (('https', '443'), ('http', '80')):
                host += ':' + port
        parts = (scheme, host, urlquote(self.fullpath), self.query_string, '')
        return urlunsplit(parts)

    @property
    def content_length(self):
        """ Content-Length header as an integer, -1 if not specified """
        return int(self.environ.get('CONTENT_LENGTH', '') or -1)

    @property
    def header(self):
        depr("The Request.header property was renamed to Request.headers")
        return self.headers

    @DictProperty('environ', 'bottle.headers', read_only=True)
    def headers(self):
        ''' Request HTTP Headers stored in a :cls:`HeaderDict`. '''
        return WSGIHeaderDict(self.environ)
    """
    d = DictProperty('environ', 'bottle.headers', read_only=True)
    headers = d(headers)
    """

    @DictProperty('environ', 'bottle.get', read_only=True)
    def GET(self):
        """ The QUERY_STRING parsed into an instance of :class:`MultiDict`. """
        data = parse_qs(self.query_string, keep_blank_values=True)
        get = self.environ['bottle.get'] = MultiDict()
        for key, values in data.iteritems():
            for value in values:
                get[key] = value
        return get

    @DictProperty('environ', 'bottle.post', read_only=True)
    def POST(self):
        """ The combined values from :attr:`forms` and :attr:`files`. Values are
            either strings (form values) or instances of
            :class:`cgi.FieldStorage` (file uploads).
        """
        post = MultiDict()
        safe_env = {'QUERY_STRING': ''}  # Build a safe environment for cgi
        for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
            if key in self.environ: safe_env[key] = self.environ[key]
        if NCTextIOWrapper:
            fb = NCTextIOWrapper(self.body, encoding='ISO-8859-1', newline='\n')
        else:
            fb = self.body
        data = cgi.FieldStorage(fp=fb, environ=safe_env, keep_blank_values=True)
        for item in data.list or []:
            post[item.name] = item if item.filename else item.value
        return post

    @DictProperty('environ', 'bottle.forms', read_only=True)
    def forms(self):
        """ POST form values parsed into an instance of :class:`MultiDict`.

            This property contains form values parsed from an `url-encoded`
            or `multipart/form-data` encoded POST request bidy. The values are
            native strings.
        """
        forms = MultiDict()
        for name, item in self.POST.iterallitems():
            if not hasattr(item, 'filename'):
                forms[name] = item
        return forms

    @DictProperty('environ', 'bottle.files', read_only=True)
    def files(self):
        """ File uploads parsed into an instance of :class:`MultiDict`.

            This property contains file uploads parsed from an
            `multipart/form-data` encoded POST request body. The values are
            instances of :class:`cgi.FieldStorage`.
        """
        files = MultiDict()
        for name, item in self.POST.iterallitems():
            if hasattr(item, 'filename'):
                files[name] = item
        return files

    @DictProperty('environ', 'bottle.params', read_only=True)
    def params(self):
        """ A combined :class:`MultiDict` with values from :attr:`forms` and
            :attr:`GET`. File-uploads are not included. """
        params = MultiDict(self.GET)
        for key, value in self.forms.iterallitems():
            params[key] = value
        return params

    @DictProperty('environ', 'bottle.body', read_only=True)
    def _body(self):
        """ The HTTP request body as a seekable file-like object.

            This property returns a copy of the `wsgi.input` stream and should
            be used instead of `environ['wsgi.input']`.
         """
        maxread = max(0, self.content_length)
        stream = self.environ['wsgi.input']
        body = BytesIO() if maxread < MEMFILE_MAX else TemporaryFile(mode='w+b')
        while maxread > 0:
            part = stream.read(min(maxread, MEMFILE_MAX))
            if not part:
                break
            body.write(part)
            maxread -= len(part)
        self.environ['wsgi.input'] = body
        body.seek(0)
        return body

    @property
    def body(self):
        self._body.seek(0)
        return self._body

    @property
    def auth(self):  # TODO: Tests and docs. Add support for digest. namedtuple?
        return parse_auth(self.headers.get('Authorization', ''))

    @DictProperty('environ', 'bottle.cookies', read_only=True)
    def COOKIES(self):
        """ Cookies parsed into a dictionary. Secure cookies are NOT decoded
            automatically. See :meth:`get_cookie` for details.
        """
        raw_dict = SimpleCookie(self.headers.get('Cookie', ''))
        cookies = {}
        for cookie in raw_dict.itervalues():
            cookies[cookie.key] = cookie.value
        return cookies

    def get_cookie(self, key, secret=None):
        """ Return the content of a cookie. To read a `Secure Cookies`, use the
            same `secret` as used to create the cookie (see
            :meth:`Response.set_cookie`). If anything goes wrong, None is
            returned.
        """
        value = self.COOKIES.get(key)
        if secret and value:
            dec = cookie_decode(value, secret) # (key, value) tuple or None
            return dec[1] if dec and dec[0] == key else None
        return value or None

    @property
    def is_ajax(self):
        ''' True if the request was generated using XMLHttpRequest '''
        # TODO: write tests
        return self.header.get('X-Requested-With') == 'XMLHttpRequest'


class Response(threading.local):
    pass


###############################################################################
# Common Utilities #############################################################
###############################################################################

class MultiDict(DictMixin):
    """ A dict that remembers old values for each key """
    # collections.MutableMapping would be better for Python >= 2.6
    def __init__(self, *a, **k):
        self.dict = dict()
        for k, v in dict(*a, **k).iteritems():
            self[k] = v

    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def __delitem__(self, key):
        del self.dict[key]

    def keys(self):
        return self.dict.keys()

    def __getitem__(self, key):
        return self.get(key, KeyError, -1)

    def __setitem__(self, key, value): self.append(key, value)

    def append(self, key, value):
        self.dict.setdefault(key, []).append(value)

    def replace(self, key, value):
        self.dict[key] = [value]

    def getall(self, key):
        return self.dict.get(key) or []

    def get(self, key, default=None, index=-1):
        if key not in self.dict and default != KeyError:
            return [default][index]
        return self.dict[key][index]

    def iterallitems(self):
        for key, values in self.dict.iteritems():
            for value in values:
                yield key, value


class HeaderDict(MultiDict):
    pass


class WSGIHeaderDict(DictMixin):

    def __init__(self, environ):
        self.environ = environ

    def _ekey(self, key): # Translate header field name to environ key.
        return 'HTTP_' + key.replace('-','_').upper()

    def raw(self, key, default=None):
        ''' Return the header value as is (may be bytes or unicode). '''
        return self.environ.get(self._ekey(key), default)

    def __getitem__(self, key):
        return tonat(self.environ[self._ekey(key)], 'latin1')

    def __setitem__(self, key, value):
        raise TypeError("%s is read-only." % self.__class__)

    def __delitem__(self, key):
        raise TypeError("%s is read-only." % self.__class__)

    def __iter__(self):
        for key in self.environ:
            if key[:5] == 'HTTP_':
                yield key[5:].replace('_', '-').title()

    def keys(self):
        return list(self)

    def __len__(self):
        return len(list(self))

    def __contains__(self, key):
        return self._ekey(key) in self.environ



class AppStack(list):
    pass


class WSGIFileWrapper(object):
    pass


###############################################################################
# Application Helper ###########################################################
###############################################################################

def dict2json(d):
    pass


def abort(code=500, text='Unknown Error: Application stopped.'):
    pass


def redirect(url, code=303):
    pass

def send_file(*a, **k):
    pass


def static_file(filename, root, guessmime=True, mimetype=None, download=False):
    pass


###############################################################################
# HTTP Utilities and MISC (TODO) ###############################################
###############################################################################

def debug(mode=True):
    pass


def parse_date(ims):
    pass

# parse_auth(self.headers.get('Authorization', ''))
def parse_auth(header):
    """ Parse rfc2617 HTTP authentication header string (basic) and return (user,pass) tuple or None"""
    try:
        method, data = header.split(None, 1)
        if method.lower() == 'basic':
            name, pwd = base64.b64decode(data).split(':', 1)
            return name, pwd
    except (KeyError, ValueError, TypeError):
        return None

def _lscmp(a, b):
    pass


def cookie_encode(data, key):
    pass

# cookie_decode(value, secret)
def cookie_decode(data, key):
    ''' Verify and decode an encoded string. Return an object or None.'''
    data = tob(data)
    if cookie_is_encoded(data):
        sig, msg = data.split(tob('?'), 1)
        if _lscmp(sig[1:], base64.b64encode(hmac.new(key, msg).digest())):
            return pickle.loads(base64.b64decode(msg))
    return None


def cookie_is_encoded(data):
    return bool(data.startswith(tob('!')) and tob('?') in data)


def yieldroutes(func):
    pass



def path_shift(script_name, path_info, shift=1):
    if shift == 0:
        return script_name, path_info

    pathlist = path_info.strip('/').split('/')
    scriptlist = script_name.strip('/').split('/')
    if pathlist and pathlist[0] == '':
        pathlist = []
    if scriptlist and scriptlist[0] == '':
        scriptlist = []

    if shift > 0 and shift <= len(pathlist):
        moved = pathlist[:shift]
        scriptlist = scriptlist + moved
        pathlist = pathlist[shift:]

    elif shift < 0 and shift >= -len(scriptlist):
        moved = scriptlist[shift:]
        pathlist = moved + pathlist
        scriptlist = scriptlist[:shift]

    else:
        empty = 'SCRIPT_NAME' if shift < 0 else 'PATH_INFO'
        raise AssertionError("Cannot shift. Nothing left from %s" % empty)

    new_script_name = '/' + '/'.join(scriptlist)
    new_path_info = '/' + '/'.join(pathlist)
    if path_info.endswith('/') and pathlist:
        new_path_info += '/'
    return new_script_name, new_path_info



# Decorators
# TODO: Replace default_app() with app()

def validate(**vkargs):
    pass


def auth_basic(check, realm="private", text="Access denied"):
    pass


def make_default_app_wrapper(name):
    pass


for name in 'route get post put delete error mount hook'.split():
    globals()[name] = make_default_app_wrapper(name)
url = make_default_app_wrapper('get_url')
del name


def default():
    pass


###############################################################################
# Server Adapter ###############################################################
###############################################################################

class ServerAdapter(object):
    pass


class CGIServer(ServerAdapter):
    pass


class FlupFCGIServer(ServerAdapter):
    pass


class WSGIRefServer(ServerAdapter):
    pass


class CherryPyServer(ServerAdapter):
    pass


class PasteServer(ServerAdapter):
    pass


class MeinheldServer(ServerAdapter):
    pass


class FapwsServer(ServerAdapter):
    pass


class TornadoServer(ServerAdapter):
    pass


class AppEngineServer(ServerAdapter):
    pass


class TwistedServer(ServerAdapter):
    pass


class DieselServer(ServerAdapter):
    pass


class GeventServer(ServerAdapter):
    pass


class GunicornServer(ServerAdapter):
    pass


class EventletServer(ServerAdapter):
    pass


class RocketServer(ServerAdapter):
    pass


class BjoernServer(ServerAdapter):
    pass


class AutoServer(ServerAdapter):
    pass


server_names = {
    'cgi': CGIServer,
    'flup': FlupFCGIServer,
    'wsgiref': WSGIRefServer,
    'cherrypy': CherryPyServer,
    'paste': PasteServer,
    'fapws3': FapwsServer,
    'tornado': TornadoServer,
    'gae': AppEngineServer,
    'twisted': TwistedServer,
    'diesel': DieselServer,
    'meinheld': MeinheldServer,
    'gunicorn': GunicornServer,
    'eventlet': EventletServer,
    'gevent': GeventServer,
    'rocket': RocketServer,
    'bjoern': BjoernServer,
    'auto': AutoServer,
}


###############################################################################
# Application Control ##########################################################
###############################################################################


def _load(target, **vars):
    pass


def load_app(target):
    pass


def run(app=None, server='wsgiref', host='127.0.0.1', port=8080,
        interval=1, reloader=False, quiet=False, **kargs):
    pass


class FileCheckerThread(threading.Thread):
    pass


def _reloader_child(server, app, interval):
    pass


def _reloader_observer(server, app, interval):
    pass


###############################################################################
# Template Adapters ############################################################
###############################################################################

class TemplateError(HTTPError):
    pass


class BaseTemplate(object):
    pass


class MakoTemplate(BaseTemplate):
    pass


class CheetahTemplate(BaseTemplate):
    pass


class Jinja2Template(BaseTemplate):
    pass


class SimpleTALTemplate(BaseTemplate):
    pass


class SimpleTemplate(BaseTemplate):
    pass


def template(*args, **kwargs):
    pass


mako_template = functools.partial(template, template_adapter=MakoTemplate)
cheetah_template = functools.partial(template, template_adapter=CheetahTemplate)
jinja2_template = functools.partial(template, template_adapter=Jinja2Template)
simpletal_template = functools.partial(template, template_adapter=SimpleTALTemplate)


def view(tpl_name, **defaults):
    pass


mako_view = functools.partial(view, template_adapter=MakoTemplate)
cheetah_view = functools.partial(view, template_adapter=CheetahTemplate)
jinja2_view = functools.partial(view, template_adapter=Jinja2Template)
simpletal_view = functools.partial(view, template_adapter=SimpleTALTemplate)

###############################################################################
# Constants and Globals ########################################################
###############################################################################

TEMPLATE_PATH = ['./', './views/']
TEMPLATES = {}
DEBUG = False
MEMFILE_MAX = 1024 * 100

#: A dict to map HTTP status codes (e.g. 404) to phrases (e.g. 'Not Found')
HTTP_CODES = httplib.responses
HTTP_CODES[418] = "I'm a teapot"  # RFC 2324

#: The default template used for error pages. Override with @error()
ERROR_PAGE_TEMPLATE = """
%try:
    %from bottle import DEBUG, HTTP_CODES, request
    %status_name = HTTP_CODES.get(e.status, 'Unknown').title()
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html>
        <head>
            <title>Error {{e.status}}: {{status_name}}</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans;}
              body {background-color: #fff; border: 1px solid #ddd; padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error {{e.status}}: {{status_name}}</h1>
            <p>Sorry, the requested URL <tt>{{request.url}}</tt> caused an error:</p>
            <pre>{{str(e.output)}}</pre>
            %if DEBUG and e.exception:
              <h2>Exception:</h2>
              <pre>{{repr(e.exception)}}</pre>
            %end
            %if DEBUG and e.traceback:
              <h2>Traceback:</h2>
              <pre>{{e.traceback}}</pre>
            %end
        </body>
    </html>
%except ImportError:
    <b>ImportError:</b> Could not generate the error page. Please add bottle to sys.path
%end
"""

#: A thread-save instance of :class:`Request` representing the `current` request.
request = Request()

#: A thread-save instance of :class:`Response` used to build the HTTP response.
response = Response()

#: A thread-save namepsace. Not used by Bottle.
local = threading.local()

# Initialize app stack (create first empty Bottle app)
# BC: 0.6.4 and needed for run()
app = default_app = AppStack()
app.push()
