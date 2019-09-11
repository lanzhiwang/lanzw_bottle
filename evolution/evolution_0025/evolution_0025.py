#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, functools, base64, hmac, pickle, os, re

from unicodedata import normalize

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
    from http.cookies import SimpleCookie
    from collections import MutableMapping as DictMixin

    from urllib.parse import unquote as urlunquote
    urlunquote = functools.partial(urlunquote, encoding='latin1')

    json_loads = lambda s: json_lds(touni(s))

else: # 2.x
    from Cookie import SimpleCookie
    from urllib import unquote as urlunquote
    if py25:
        from UserDict import DictMixin
    else: # 2.6, 2.7
        from collections import MutableMapping as DictMixin

    json_loads = json_lds



def tob(s, enc='utf8'):
    return s.encode(enc) if isinstance(s, unicode) else bytes(s)

def touni(s, enc='utf8', err='strict'):
    return s.decode(enc, err) if isinstance(s, bytes) else unicode(s)

tonat = touni if py3k else tob


# Workaround for the missing "as" keyword in py3k.
def _e(): return sys.exc_info()[1]
"""
>>> import sys
>>> sys.exc_info()
(None, None, None)
>>>
"""


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



# THE END
