#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, functools, base64, hmac, pickle, os, re, cgi, warnings, threading, email, time

from unicodedata import normalize
from tempfile import TemporaryFile

try: from simplejson import dumps as json_dumps, loads as json_lds
except ImportError: # pragma: no cover
    try: from json import dumps as json_dumps, loads as json_lds
    except ImportError:
        try: from django.utils.simplejson import dumps as json_dumps, loads as json_lds
        except ImportError:
            def json_dumps(data):
                raise ImportError("JSON support requires Python 2.6 or simplejson.")
            json_lds = json_dumps


py   = sys.version_info
py3k = py >= (3, 0, 0)
py25 = py <  (2, 6, 0)
py31 = (3, 1, 0) <= py < (3, 2, 0)

if py3k:
    from urllib.parse import urljoin, SplitResult as UrlSplitResult
    from http.cookies import SimpleCookie
    from collections import MutableMapping as DictMixin
    from io import BytesIO

    from urllib.parse import urlencode, quote as urlquote, unquote as urlunquote

    urlunquote = functools.partial(urlunquote, encoding='latin1')

    json_loads = lambda s: json_lds(touni(s))

    unicode = str

else: # 2.x
    from Cookie import SimpleCookie
    from urllib import urlencode, quote as urlquote, unquote as urlunquote
    from StringIO import StringIO as BytesIO
    from urlparse import urljoin, SplitResult as UrlSplitResult
    if py25:
        from UserDict import DictMixin
    else: # 2.6, 2.7
        from collections import MutableMapping as DictMixin

    json_loads = json_lds
    unicode = unicode



def tob(s, enc='utf8'):
    return s.encode(enc) if isinstance(s, unicode) else bytes(s)

def touni(s, enc='utf8', err='strict'):
    return s.decode(enc, err) if isinstance(s, bytes) else unicode(s)

tonat = touni if py3k else tob

if py31:
    from io import TextIOWrapper
    class NCTextIOWrapper(TextIOWrapper):
        def close(self): pass # Keep wrapped buffer open.


# Workaround for the missing "as" keyword in py3k.
def _e(): return sys.exc_info()[1]
"""
>>> import sys
>>> sys.exc_info()
(None, None, None)
>>>
"""


def depr(message, hard=False):
    warnings.warn(message, DeprecationWarning, stacklevel=3)


class DictProperty(object):
    # DictProperty('environ', 'bottle.app', read_only=True)
    def __init__(self, attr, key=None, read_only=False):
        self.attr = attr
        self.key = key
        self.read_only = read_only

    def __call__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter = func
        self.key = self.key or func.__name__
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self
        key = self.key
        storage = getattr(obj, self.attr)
        if key not in storage:
            storage[key] = self.getter(obj)
        return storage[key]

    def __set__(self, obj, value):
        if self.read_only:
            raise AttributeError("Read-Only property.")
        getattr(obj, self.attr)[self.key] = value

    def __delete__(self, obj):
        if self.read_only:
            raise AttributeError("Read-Only property.")
        del getattr(obj, self.attr)[self.key]


class cached_property(object):
    ''' A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property. '''

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value




###############################################################################
# Exceptions and Events ########################################################
###############################################################################

class BottleException(Exception):
    """ A base class for exceptions used by bottle. """
    pass






###############################################################################
# Routing ######################################################################
###############################################################################





###############################################################################
# Application Object ###########################################################
###############################################################################









###############################################################################
# HTTP and WSGI Tools ##########################################################
###############################################################################

class BaseRequest(object):

    __slots__ = ('environ')

    MEMFILE_MAX = 102400

    def __init__(self, environ=None):
        self.environ = {} if environ is None else environ
        self.environ['bottle.request'] = self

    # app = DictProperty('environ', 'bottle.app', read_only=True)(app)   # return DictProperty
    # self.app
    # environ['bottle.app']
    @DictProperty('environ', 'bottle.app', read_only=True)
    def app(self):
        raise RuntimeError('This request is not connected to an application.')

    # environ['bottle.route']
    @DictProperty('environ', 'bottle.route', read_only=True)
    def route(self):
        raise RuntimeError('This request is not connected to a route.')

    @DictProperty('environ', 'route.url_args', read_only=True)
    def url_args(self):
        raise RuntimeError('This request is not connected to a route.')

    @property
    def path(self):
        return '/' + self.environ.get('PATH_INFO', '').lstrip('/')

    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD', 'GET').upper()

    @DictProperty('environ', 'bottle.request.headers', read_only=True)
    def headers(self):
        return WSGIHeaderDict(self.environ)

    def get_header(self, name, default=None):
        return self.headers.get(name, default)

    @DictProperty('environ', 'bottle.request.cookies', read_only=True)
    def cookies(self):
        cookies = SimpleCookie(self.environ.get('HTTP_COOKIE', '')).values()
        return FormsDict((c.key, c.value) for c in cookies)  # {key: [], key: []}

    def get_cookie(self, key, default=None, secret=None):
        value = self.cookies.get(key)
        if secret and value:
            dec = cookie_decode(value, secret) # (key, value) tuple or None
            return dec[1] if dec and dec[0] == key else default
        return value or default

    @DictProperty('environ', 'bottle.request.query', read_only=True)
    def query(self):
        get = self.environ['bottle.get'] = FormsDict()
        pairs = _parse_qsl(self.environ.get('QUERY_STRING', ''))
        for key, value in pairs:
            get[key] = value
        return get

    @DictProperty('environ', 'bottle.request.forms', read_only=True)
    def forms(self):
        """ Form values parsed from an `url-encoded` or `multipart/form-data`
            encoded POST or PUT request body. The result is returned as a
            :class:`FormsDict`. All keys and values are strings. File uploads
            are stored separately in :attr:`files`. """
        forms = FormsDict()
        for name, item in self.POST.allitems():
            if not isinstance(item, FileUpload):
                forms[name] = item
        return forms

    @DictProperty('environ', 'bottle.request.params', read_only=True)
    def params(self):
        """ A :class:`FormsDict` with the combined values of :attr:`query` and
            :attr:`forms`. File uploads are stored in :attr:`files`. """
        params = FormsDict()
        for key, value in self.query.allitems():
            params[key] = value
        for key, value in self.forms.allitems():
            params[key] = value
        return params

    @DictProperty('environ', 'bottle.request.files', read_only=True)
    def files(self):
        """ File uploads parsed from `multipart/form-data` encoded POST or PUT
            request body. The values are instances of :class:`FileUpload`.

        """
        files = FormsDict()
        for name, item in self.POST.allitems():
            if isinstance(item, FileUpload):
                files[name] = item
        return files

    @DictProperty('environ', 'bottle.request.json', read_only=True)
    def json(self):
        ctype = self.environ.get('CONTENT_TYPE', '').lower().split(';')[0]
        if ctype == 'application/json':
            b = self._get_body_string()
            if not b:
                return None
            return json_loads(b)
        return None

    # body_iter(read_func, self.MEMFILE_MAX)
    def _iter_body(self, read, bufsize):
        maxread = max(0, self.content_length)
        while maxread:
            part = read(min(maxread, bufsize))
            if not part:
                break
            yield part
            maxread -= len(part)

    # body_iter(read_func, self.MEMFILE_MAX)
    def _iter_chunked(self, read, bufsize):
        err = HTTPError(400, 'Error while parsing chunked transfer body.')
        rn, sem, bs = tob('\r\n'), tob(';'), tob('')
        while True:
            header = read(1)
            while header[-2:] != rn:
                c = read(1)
                header += c
                if not c: raise err
                if len(header) > bufsize: raise err
            size, _, _ = header.partition(sem)
            try:
                maxread = int(tonat(size.strip()), 16)
            except ValueError:
                raise err
            if maxread == 0: break
            buff = bs
            while maxread > 0:
                if not buff:
                    buff = read(min(maxread, bufsize))
                part, buff = buff[:maxread], buff[maxread:]
                if not part: raise err
                yield part
                maxread -= len(part)
            if read(2) != rn:
                raise err

    @DictProperty('environ', 'bottle.request.body', read_only=True)
    def _body(self):
        if self.chunked:
            body_iter = self._iter_chunked
        else:
            body_iter = self._iter_body
        # body_iter = self._iter_chunked if self.chunked else self._iter_body

        read_func = self.environ['wsgi.input'].read

        body = BytesIO()
        body_size = 0
        is_temp_file = False

        for part in body_iter(read_func, self.MEMFILE_MAX):
            body.write(part)
            body_size += len(part)
            if not is_temp_file and body_size > self.MEMFILE_MAX:
                body, tmp = TemporaryFile(mode='w+b'), body
                body.write(tmp.getvalue())
                del tmp
                is_temp_file = True
        self.environ['wsgi.input'] = body
        body.seek(0)
        return body

    def _get_body_string(self):
        ''' read body until content-length or MEMFILE_MAX into a string. Raise
            HTTPError(413) on requests that are to large. '''
        clen = self.content_length
        if clen > self.MEMFILE_MAX:
            raise HTTPError(413, 'Request to large')
        if clen < 0:
            clen = self.MEMFILE_MAX + 1
        data = self.body.read(clen)
        if len(data) > self.MEMFILE_MAX: # Fail fast
            raise HTTPError(413, 'Request to large')
        return data

    @property
    def body(self):
        """ The HTTP request body as a seek-able file-like object. Depending on
            :attr:`MEMFILE_MAX`, this is either a temporary file or a
            :class:`io.BytesIO` instance. Accessing this property for the first
            time reads and replaces the ``wsgi.input`` environ variable.
            Subsequent accesses just do a `seek(0)` on the file object. """
        self._body.seek(0)
        return self._body

    @property
    def chunked(self):
        ''' True if Chunked transfer encoding was. '''
        return 'chunked' in self.environ.get('HTTP_TRANSFER_ENCODING', '').lower()

    #: An alias for :attr:`query`.
    GET = query

    @DictProperty('environ', 'bottle.request.post', read_only=True)
    def POST(self):
        post = FormsDict()
        # We default to application/x-www-form-urlencoded for everything that
        # is not multipart and take the fast path (also: 3.1 workaround)
        if not self.content_type.startswith('multipart/'):
            pairs = _parse_qsl(tonat(self._get_body_string(), 'latin1'))
            for key, value in pairs:
                post[key] = value
            return post

        safe_env = {'QUERY_STRING': ''}  # Build a safe environment for cgi
        for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
            if key in self.environ:
                safe_env[key] = self.environ[key]
        args = dict(fp=self.body, environ=safe_env, keep_blank_values=True)
        if py31:
            args['fp'] = NCTextIOWrapper(args['fp'], encoding='utf8', newline='\n')
        elif py3k:
            args['encoding'] = 'utf8'

        data = cgi.FieldStorage(**args)
        self['_cgi.FieldStorage'] = data  # http://bugs.python.org/issue18394#msg207958
        data = data.list or []
        for item in data:
            if item.filename:
                post[item.name] = FileUpload(item.file, item.name,
                                             item.filename, item.headers)
            else:
                post[item.name] = item.value
        return post

    @property
    def url(self):
        return self.urlparts.geturl()

    @DictProperty('environ', 'bottle.request.urlparts', read_only=True)
    def urlparts(self):
        env = self.environ
        http = env.get('HTTP_X_FORWARDED_PROTO') or env.get('wsgi.url_scheme', 'http')
        host = env.get('HTTP_X_FORWARDED_HOST') or env.get('HTTP_HOST')
        if not host:
            # HTTP 1.1 requires a Host-header. This is for HTTP/1.0 clients.
            host = env.get('SERVER_NAME', '127.0.0.1')
            port = env.get('SERVER_PORT')
            if port and port != ('80' if http == 'http' else '443'):
                host += ':' + port
        path = urlquote(self.fullpath)
        return UrlSplitResult(http, host, path, env.get('QUERY_STRING'), '')

    @property
    def fullpath(self):
        """ Request path including :attr:`script_name` (if present). """
        return urljoin(self.script_name, self.path.lstrip('/'))

    @property
    def query_string(self):
        return self.environ.get('QUERY_STRING', '')

    @property
    def script_name(self):
        script_name = self.environ.get('SCRIPT_NAME', '').strip('/')
        return '/' + script_name + '/' if script_name else '/'

    def path_shift(self, shift=1):
        script = self.environ.get('SCRIPT_NAME','/')
        self['SCRIPT_NAME'], self['PATH_INFO'] = path_shift(script, self.path, shift)

    @property
    def content_length(self):
        return int(self.environ.get('CONTENT_LENGTH') or -1)

    @property
    def content_type(self):
        return self.environ.get('CONTENT_TYPE', '').lower()

    @property
    def is_xhr(self):
        requested_with = self.environ.get('HTTP_X_REQUESTED_WITH', '')
        return requested_with.lower() == 'xmlhttprequest'

    @property
    def is_ajax(self):
        ''' Alias for :attr:`is_xhr`. "Ajax" is not the right term. '''
        return self.is_xhr

    @property
    def auth(self):
        """ HTTP authentication data as a (user, password) tuple. This
            implementation currently supports basic (not digest) authentication
            only. If the authentication happened at a higher level (e.g. in the
            front web-server or a middleware), the password field is None, but
            the user field is looked up from the ``REMOTE_USER`` environ
            variable. On any errors, None is returned. """
        basic = parse_auth(self.environ.get('HTTP_AUTHORIZATION', ''))
        if basic:
            return basic
        ruser = self.environ.get('REMOTE_USER')
        if ruser:
            return (ruser, None)
        return None

    @property
    def remote_route(self):
        """ A list of all IPs that were involved in this request, starting with
            the client IP and followed by zero or more proxies. This does only
            work if all proxies support the ```X-Forwarded-For`` header. Note
            that this information can be forged by malicious clients. """
        proxy = self.environ.get('HTTP_X_FORWARDED_FOR')
        if proxy:
            return [ip.strip() for ip in proxy.split(',')]
        remote = self.environ.get('REMOTE_ADDR')
        return [remote] if remote else []

    @property
    def remote_addr(self):
        """ The client IP as a string. Note that this information can be forged
            by malicious clients. """
        route = self.remote_route
        return route[0] if route else None

    def copy(self):
        """ Return a new :class:`Request` with a shallow :attr:`environ` copy. """
        return Request(self.environ.copy())

    def get(self, value, default=None):
        return self.environ.get(value, default)

    def __getitem__(self, key):
        return self.environ[key]

    def __delitem__(self, key):
        self[key] = ""; del(self.environ[key])

    def __iter__(self):
        return iter(self.environ)

    def __len__(self):
        return len(self.environ)

    def keys(self):
        return self.environ.keys()

    def __setitem__(self, key, value):
        """ Change an environ value and clear all caches that depend on it. """

        if self.environ.get('bottle.request.readonly'):
            raise KeyError('The environ dictionary is read-only.')

        self.environ[key] = value
        todelete = ()

        if key == 'wsgi.input':
            todelete = ('body', 'forms', 'files', 'params', 'post', 'json')
        elif key == 'QUERY_STRING':
            todelete = ('query', 'params')
        elif key.startswith('HTTP_'):
            todelete = ('headers', 'cookies')

        for key in todelete:
            self.environ.pop('bottle.request.'+key, None)

    def __repr__(self):
        return '<%s: %s %s>' % (self.__class__.__name__, self.method, self.url)

    def __getattr__(self, name):
        ''' Search in self.environ for additional user defined attributes. '''
        try:
            var = self.environ['bottle.request.ext.%s'%name]
            return var.__get__(self) if hasattr(var, '__get__') else var
        except KeyError:
            raise AttributeError('Attribute %r not defined.' % name)

    def __setattr__(self, name, value):
        if name == 'environ':
            return object.__setattr__(self, name, value)
        self.environ['bottle.request.ext.%s'%name] = value






def _hkey(key):
    if '\n' in key or '\r' in key or '\0' in key:
        raise ValueError("Header names must not contain control characters: %r" % key)
    return key.title().replace('_', '-')


def _hval(value):
    value = tonat(value)
    if '\n' in value or '\r' in value or '\0' in value:
        raise ValueError("Header value must not contain control characters: %r" % value)
    return value


class HeaderProperty(object):
    # content_type = HeaderProperty('Content-Type')
    # content_length = HeaderProperty('Content-Length', reader=int, default=-1)
    def __init__(self, name, reader=None, writer=None, default=''):
        self.name = name
        self.default = default
        self.reader = reader
        self.reader = writer
        self.__doc__ = 'Current value of the %r header.' % name.title()

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.get_header(self.name, self.default)
        return self.reader(value) if self.reader else value

    def __set__(self, obj, value):
        obj[self.name] = self.writer(value) if self.writer else value

    def __delete__(self, obj):
        del obj[self.name]


class BaseResponse(object):
    pass


Request = BaseRequest
Response = BaseResponse


def local_property(name=None):
    if name:
        depr('local_property() is deprecated and will be removed.') #0.12
    ls = threading.local()
    def fget(self):
        try:
            return ls.var
        except AttributeError:
            raise RuntimeError("Request context not initialized.")

    def fset(self, value):
        ls.var = value

    def fdel(self):
        del ls.var

    return property(fget, fset, fdel, 'Thread-local property')


class LocalRequest(BaseRequest):
    ''' A thread-local subclass of :class:`BaseRequest` with a different
        set of attributes for each thread. There is usually only one global
        instance of this class (:data:`request`). If accessed during a
        request/response cycle, this instance always refers to the *current*
        request (even on a multithreaded server). '''
    bind = BaseRequest.__init__
    environ = local_property()  # property(fget, fset, fdel, 'Thread-local property')


class HTTPResponse(Response, BottleException):
    def __init__(self, body='', status=None, headers=None, **more_headers):
        super(HTTPResponse, self).__init__(body, status, headers, **more_headers)

    def apply(self, response):
        response._status_code = self._status_code
        response._status_line = self._status_line
        response._headers = self._headers
        response._cookies = self._cookies
        response.body = self.body


class HTTPError(HTTPResponse):
    default_status = 500
    def __init__(self, status=None, body=None, exception=None, traceback=None,
                 **options):
        self.exception = exception
        self.traceback = traceback
        super(HTTPError, self).__init__(body, status, **options)




###############################################################################
# Plugins ######################################################################
###############################################################################



###############################################################################
# Common Utilities #############################################################
###############################################################################



class MultiDict(DictMixin):
    def __init__(self, *a, **k):
        self.dict = dict((k, [v]) for (k, v) in dict(*a, **k).items())

    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def __delitem__(self, key):
        del self.dict[key]

    def __getitem__(self, key):
        return self.dict[key][-1]

    def __setitem__(self, key, value):
        self.append(key, value)

    def keys(self):
        return self.dict.keys()

    if py3k:
        def values(self):
            return (v[-1] for v in self.dict.values())

        def items(self):
            return ((k, v[-1]) for k, v in self.dict.items())

        def allitems(self):
            return ((k, v) for k, vl in self.dict.items() for v in vl)

        iterkeys = keys
        itervalues = values
        iteritems = items
        iterallitems = allitems

    else:
        def values(self):
            return [v[-1] for v in self.dict.values()]

        def items(self):
            return [(k, v[-1]) for k, v in self.dict.items()]

        def iterkeys(self):
            return self.dict.iterkeys()

        def itervalues(self):
            return (v[-1] for v in self.dict.itervalues())

        def iteritems(self):
            return ((k, v[-1]) for k, v in self.dict.iteritems())

        def iterallitems(self):
            return ((k, v) for k, vl in self.dict.iteritems() for v in vl)

        def allitems(self):
            return [(k, v) for k, vl in self.dict.iteritems() for v in vl]

    def get(self, key, default=None, index=-1, type=None):
        try:
            val = self.dict[key][index]
            return type(val) if type else val
        except Exception:
            pass
        return default

    def append(self, key, value):
        self.dict.setdefault(key, []).append(value)

    def replace(self, key, value):
        self.dict[key] = [value]

    def getall(self, key):
        return self.dict.get(key) or []

    #: Aliases for WTForms to mimic other multi-dict APIs (Django)
    getone = get
    getlist = getall


class FormsDict(MultiDict):
    #: Encoding used for attribute values.
    input_encoding = 'utf8'
    #: If true (default), unicode strings are first encoded with `latin1`
    #: and then decoded to match :attr:`input_encoding`.
    recode_unicode = True

    def _fix(self, s, encoding=None):
        if isinstance(s, unicode) and self.recode_unicode: # Python 3 WSGI
            return s.encode('latin1').decode(encoding or self.input_encoding)
        elif isinstance(s, bytes): # Python 2 WSGI
            return s.decode(encoding or self.input_encoding)
        else:
            return s

    def decode(self, encoding=None):
        ''' Returns a copy with all keys and values de- or recoded to match
            :attr:`input_encoding`. Some libraries (e.g. WTForms) want a
            unicode dictionary. '''
        copy = FormsDict()
        enc = copy.input_encoding = encoding or self.input_encoding
        copy.recode_unicode = False
        for key, value in self.allitems():
            copy.append(self._fix(key, enc), self._fix(value, enc))
        return copy

    def getunicode(self, name, default=None, encoding=None):
        ''' Return the value as a unicode string, or the default. '''
        try:
            return self._fix(self[name], encoding)
        except (UnicodeError, KeyError):
            return default

    def __getattr__(self, name, default=unicode()):
        # Without this guard, pickle generates a cryptic TypeError:
        if name.startswith('__') and name.endswith('__'):
            return super(FormsDict, self).__getattr__(name)
        return self.getunicode(name, default=default)


class HeaderDict(MultiDict):

    def __init__(self, *a, **ka):
        self.dict = {}
        if a or ka:
            self.update(*a, **ka)

    def __contains__(self, key):
        return _hkey(key) in self.dict

    def __delitem__(self, key):
        del self.dict[_hkey(key)]

    def __getitem__(self, key):
        return self.dict[_hkey(key)][-1]

    def __setitem__(self, key, value):
        self.dict[_hkey(key)] = [_hval(value)]

    def append(self, key, value):
        self.dict.setdefault(_hkey(key), []).append(_hval(value))

    def replace(self, key, value):
        self.dict[_hkey(key)] = [_hval(value)]

    def getall(self, key):
        return self.dict.get(_hkey(key)) or []

    def get(self, key, default=None, index=-1):
        return MultiDict.get(self, _hkey(key), default, index)

    def filter(self, names):
        for name in (_hkey(n) for n in names):
            if name in self.dict:
                del self.dict[name]






class WSGIHeaderDict(DictMixin):
    #: List of keys that do not have a ``HTTP_`` prefix.
    cgikeys = ('CONTENT_TYPE', 'CONTENT_LENGTH')

    # WSGIHeaderDict(self.environ)
    def __init__(self, environ):
        self.environ = environ

    def _ekey(self, key):
        ''' Translate header field name to CGI/WSGI environ key. '''
        key = key.replace('-','_').upper()
        if key in self.cgikeys:
            return key
        return 'HTTP_' + key

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
            elif key in self.cgikeys:
                yield key.replace('_', '-').title()

    def keys(self): return [x for x in self]
    def __len__(self): return len(self.keys())
    def __contains__(self, key): return self._ekey(key) in self.environ



class FileUpload(object):

    def __init__(self, fileobj, name, filename, headers=None):
        self.file = fileobj
        self.name = name
        self.raw_filename = filename
        self.headers = HeaderDict(headers) if headers else HeaderDict()

    content_type = HeaderProperty('Content-Type')
    content_length = HeaderProperty('Content-Length', reader=int, default=-1)

    def get_header(self, name, default=None):
        """ Return the value of a header within the mulripart part. """
        return self.headers.get(name, default)

    # obj.__dict__[self.func.__name__] = self.func(obj)
    # FileUpload.__dict__[filename] = self.func(obj)
    @cached_property
    def filename(self):
        fname = self.raw_filename
        if not isinstance(fname, unicode):
            fname = fname.decode('utf8', 'ignore')
        fname = normalize('NFKD', fname).encode('ASCII', 'ignore').decode('ASCII')
        fname = os.path.basename(fname.replace('\\', os.path.sep))
        fname = re.sub(r'[^a-zA-Z0-9-_.\s]', '', fname).strip()
        fname = re.sub(r'[-\s]+', '-', fname).strip('.-')
        return fname[:255] or 'empty'

    def _copy_file(self, fp, chunk_size=2**16):
        read = self.file.read
        write = fp.write
        offset = self.file.tell()
        while 1:
            buf = read(chunk_size)
            if not buf:
                break
            write(buf)
        self.file.seek(offset)

    def save(self, destination, overwrite=False, chunk_size=2**16):
        if isinstance(destination, basestring): # Except file-likes here
            if os.path.isdir(destination):
                destination = os.path.join(destination, self.filename)
            if not overwrite and os.path.exists(destination):
                raise IOError('File exists.')
            with open(destination, 'wb') as fp:
                self._copy_file(fp, chunk_size)
        else:
            self._copy_file(destination, chunk_size)



###############################################################################
# Application Helper ###########################################################
###############################################################################





###############################################################################
# HTTP Utilities and MISC (TODO) ###############################################
###############################################################################

def parse_date(ims):
    """ Parse rfc1123, rfc850 and asctime timestamps and return UTC epoch. """
    try:
        ts = email.utils.parsedate_tz(ims)
        return time.mktime(ts[:8] + (0,)) - (ts[9] or 0) - time.timezone
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

def parse_auth(header):
    """ Parse rfc2617 HTTP authentication header string (basic) and return (user,pass) tuple or None"""
    try:
        method, data = header.split(None, 1)
        if method.lower() == 'basic':
            user, pwd = touni(base64.b64decode(tob(data))).split(':',1)
            return user, pwd
    except (KeyError, ValueError):
        return None

def _parse_qsl(qs):
    r = []
    for pair in qs.replace(';','&').split('&'):
        if not pair: continue
        nv = pair.split('=', 1)
        if len(nv) != 2: nv.append('')
        key = urlunquote(nv[0].replace('+', ' '))
        value = urlunquote(nv[1].replace('+', ' '))
        r.append((key, value))
    return r


def _lscmp(a, b):
    return not sum(0 if x==y else 1 for x, y in zip(a, b)) and len(a) == len(b)


def cookie_encode(data, key):
    ''' Encode and sign a pickle-able object. Return a (byte) string '''
    msg = base64.b64encode(pickle.dumps(data, -1))
    sig = base64.b64encode(hmac.new(tob(key), msg).digest())
    return tob('!') + sig + tob('?') + msg


def cookie_decode(data, key):
    ''' Verify and decode an encoded string. Return an object or None.'''
    data = tob(data)
    if cookie_is_encoded(data):
        sig, msg = data.split(tob('?'), 1)
        if _lscmp(sig[1:], base64.b64encode(hmac.new(tob(key), msg).digest())):
            return pickle.loads(base64.b64decode(msg))
    return None


def cookie_is_encoded(data):
    ''' Return True if the argument looks like a encoded cookie.'''
    return bool(data.startswith(tob('!')) and tob('?') in data)

def path_shift(script_name, path_info, shift=1):
    ''' Shift path fragments from PATH_INFO to SCRIPT_NAME and vice versa.

        :return: The modified paths.
        :param script_name: The SCRIPT_NAME path.
        :param script_name: The PATH_INFO path.
        :param shift: The number of path fragments to shift. May be negative to
          change the shift direction. (default: 1)
    '''
    if shift == 0: return script_name, path_info
    pathlist = path_info.strip('/').split('/')
    scriptlist = script_name.strip('/').split('/')
    if pathlist and pathlist[0] == '': pathlist = []
    if scriptlist and scriptlist[0] == '': scriptlist = []
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
    if path_info.endswith('/') and pathlist: new_path_info += '/'
    return new_script_name, new_path_info


###############################################################################
# Server Adapter ###############################################################
###############################################################################





###############################################################################
# Application Control ##########################################################
###############################################################################





###############################################################################
# Template Adapters ############################################################
###############################################################################







###############################################################################
# Constants and Globals ########################################################
###############################################################################

request = LocalRequest()


# THE END
