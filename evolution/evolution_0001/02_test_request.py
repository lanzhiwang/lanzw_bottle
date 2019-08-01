#!/usr/bin/env python
# -*- coding: utf-8 -*-


import wsgiref.util
import cgi
import Cookie
import threading

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

# from evolution_0001 import Request

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
            # raw_dict = parse_qs(self.query, keep_blank_values=1)
            raw_dict = parse_qs(self.query_string, keep_blank_values=1)
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
            raw_dict = Cookie.SimpleCookie(self._environ.get('HTTP_COOKIE', ''))
            self._COOKIES = {}
            for cookie in raw_dict.values():
                self._COOKIES[cookie.key] = cookie.value
        return self._COOKIES


if __name__ == "__main__":
    request = Request()
    env = {}
    wsgiref.util.setup_testing_defaults(env)
    # print env
    """
    {
    'wsgi.multiprocess': 0, 
    'wsgi.version': (1, 0), 
    'SERVER_NAME': '127.0.0.1', 
    'wsgi.run_once': 0, 
    'wsgi.errors': <StringIO.StringIO instance at 0x7f85f8cc8560>, 
    'wsgi.multithread': 0, 
    'SCRIPT_NAME': '', 
    'wsgi.url_scheme': 'http', 
    'wsgi.input': <StringIO.StringIO instance at 0x7f85f8cc8680>, 
    'REQUEST_METHOD': 'GET', 
    'HTTP_HOST': '127.0.0.1', 
    'PATH_INFO': '/', 
    'SERVER_PORT': '80', 
    'SERVER_PROTOCOL': 'HTTP/1.0'
    }
    """

    request.bind(env)
    print request.method  # GET  <- REQUEST_METHOD
    print request.query_string  #   <- QUERY_STRING
    print request.input_length  # 0  <- CONTENT_LENGTH
    print request.GET  # {}  <- parse_qs(self.query_string, keep_blank_values=1)
    print request.POST  # {}  <- cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
    print request.params  # None  <-
    print request.COOKIES  # {}  <- Cookie.SimpleCookie(self._environ.get('HTTP_COOKIE', ''))
    print request.path  # /  <- PATH_INFO

