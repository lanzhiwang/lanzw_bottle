# -*- coding: utf-8 -*-

import functools


class DictProperty(object):

    # DictProperty('environ', 'bottle.headers', read_only=True)
    def __init__(self, attr, key=None, read_only=False):
        self.attr = attr  # 'environ'
        self.key = key  # bottle.headers
        self.read_only = read_only  # True

    # d = DictProperty('environ', 'bottle.headers', read_only=True)
    # headers = d(headers)
    def __call__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter = func  # headers
        self.key = self.key or func.__name__  # bottle.headers
        return self

    def __get__(self, obj, cls):
        if not obj:  # 类名直接调用返回 DictProperty 对象
            return self
        key = self.key  # # bottle.headers
        storage = getattr(obj, self.attr)  # request 的 environ 属性
        if key not in storage:
            storage[key] = self.getter(obj)  # request.environ['bottle.headers'] =
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
    ''' A property that, if accessed, replaces itself with the computed
        value. Subsequent accesses won't call the getter again. '''
    d = DictProperty('__dict__')
    r = d(func)
    return r


class Request():
    def __init__(self, environ=None):
        """ Create a new Request instance.

            You usually don't do this but use the global `bottle.request`
            instance instead.
        """
        self.bind(environ or {}, )

    def bind(self, environ):
        """ Bind a new WSGI environment.

            This is done automatically for the global `bottle.request`
            instance on every request.
        """
        self.environ = environ
        # These attributes are used anyway, so it is ok to compute them here
        self.path = '/' + environ.get('PATH_INFO', '/').lstrip('/')
        self.method = environ.get('REQUEST_METHOD', 'GET').upper()


    @DictProperty('environ', 'bottle.headers', read_only=True)
    def headers(self):
        ''' Request HTTP Headers stored in a :cls:`HeaderDict`. '''
        return WSGIHeaderDict(self.environ)

    """
    等价于
    d = DictProperty('environ', 'bottle.headers', read_only=True)
    headers = d(headers)
    
    self.headers
    self.headers = 
    del self.headers
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
            if not part: break
            body.write(part)
            maxread -= len(part)
        self.environ['wsgi.input'] = body
        body.seek(0)
        return body

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
