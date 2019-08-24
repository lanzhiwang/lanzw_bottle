#!/usr/bin/env python
# -*- coding: utf-8 -*-
from evolution_0016 import route, view, response
import evolution_0016
import markdown
import os.path
import sys
import re
import codecs
import glob
import datetime
import cgi

class Page(object):
    pagedir  = '../docs'
    cachedir = './cache'
    options = ['codehilite(force_linenos=True)', 'toc']

    def __init__(self, name):
        self.name = name
        self.filename  = os.path.join(self.pagedir,  self.name+'.md')
        self.cachename = os.path.join(self.cachedir, self.name+'.html')

    @property
    def exists(self):
        return os.path.exists(self.filename)

    @property
    def rawfile(self):
        #if not self.exists:
        #    open(self.filename, 'w').close()
        return codecs.open(self.filename, encoding='utf8')

    @property
    def raw(self):
        return self.rawfile.read()

    @property
    def cachefile(self):
        if not os.path.exists(self.cachename) \
        or os.path.getmtime(self.filename) > os.path.getmtime(self.cachename):
           with self.rawfile as f:
               html = markdown.markdown(f.read(), self.options)
           with open(self.cachename, 'w') as f:
               f.write(html.encode('utf-8'))
        return codecs.open(self.cachename, encoding='utf8')

    @property
    def html(self):
        return self.cachefile.read()

    @property
    def title(self):
        ''' The first h1 element '''
        for m in re.finditer(r'<h1[^>]*>(.+?)</h1>', self.html):
            return m.group(1).strip()
        return self.name.replace('_',' ').title()

    @property
    def preview(self):
        for m in re.finditer(r'<p[^>]*>(.+?)</p>', self.html, re.DOTALL):
            return m.group(1).strip()
        return '<i>No preview available</i>'

    @property
    def blogtime(self):
        try:
            date, name = self.name.split('_', 1)
            year, month, day = map(int, date.split('-'))
            return datetime.date(year, month, day)
        except ValueError:
            raise AttributeError("This page is not a blogpost")

    @property
    def is_blogpost(self):
        try:
            self.blogtime
            return True
        except AttributeError:
            return False

def iter_blogposts():
    # print os.path.join(Page.pagedir, '*.md')  # ../docs/*.md
    # print glob.glob(os.path.join(Page.pagedir, '*.md'))  # ['../docs/contact.md', '../docs/docs.md']
    for post in glob.glob(os.path.join(Page.pagedir, '*.md')):
        name = os.path.basename(post)[:-3]
        if re.match(r'20[0-9]{2}-[0-9]{2}-[0-9]{2}_', name):
            # print name
            yield Page(name)

# for page in iter_blogposts():
#     print page




# Static files

# @route('/:filename#.+\.(css|js|ico|png|txt|html)#')
def static(filename):
    return evolution_0016.static_file(filename, root='./static/')

print '处理第1个路由'
print 'route(\'/:filename#.+\.(css|js|ico|png|txt|html)#\')'
route = route('/:filename#.+\.(css|js|ico|png|txt|html)#')
print 'route(static)'
route(static)



class Bottle(object):
    """ WSGI application """

    def __init__(self, catchall=True, autojson=True, config=None):
        """ Create a new bottle instance.
            You usually don't do that. Use `bottle.app.push()` instead.
        """
        self.routes = []  # List of installed routes including metadata.
        self.callbacks = {}  # Cache for wrapped callbacks.
        self.router = Router()  # Maps to self.routes indices.

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

    def add_filter(self, ftype, func):
        ''' Register a new output filter. Whenever bottle hits a handler output
            matching `ftype`, `func` is applied to it. '''
        if not isinstance(ftype, type):
            raise TypeError("Expected type object, got %s" % type(ftype))
        self.castfilter = [(t, f) for (t, f) in self.castfilter if t != ftype]
        self.castfilter.append((ftype, func))
        self.castfilter.sort()

    def match_url(self, path, method='GET'):
        return self.match({'PATH_INFO': path, 'REQUEST_METHOD': method})

    def match(self, environ):
        """ Return a (callback, url-args) tuple or raise HTTPError. """
        target, args = self.router.match(environ)
        try:
            return self.callbacks[target], args
        except KeyError:
            callback, decorators = self.routes[target]
            wrapped = callback
            for wrapper in decorators[::-1]:
                wrapped = wrapper(wrapped)
            # for plugin in self.plugins or []:
            #    wrapped = plugin.apply(wrapped, rule)
            functools.update_wrapper(wrapped, callback)
            self.callbacks[target] = wrapped
            return wrapped, args

    def get_url(self, routename, **kargs):
        """ Return a string that matches a named route """
        scriptname = request.environ.get('SCRIPT_NAME', '').strip('/') + '/'
        location = self.router.build(routename, **kargs).lstrip('/')
        return urljoin(urljoin('/', scriptname), location)

    def route(self, path=None, method='GET', no_hooks=False, decorate=None,
              template=None, template_opts={}, callback=None, name=None,
              static=False):
        """ Decorator: Bind a callback function to a request path.

            :param path: The request path or a list of paths to listen to. See
              :class:`Router` for syntax details. If no path is specified, it
              is automatically generated from the callback signature. See
              :func:`yieldroutes` for details.
            :param method: The HTTP method (POST, GET, ...) or a list of
              methods to listen to. (default: GET)
            :param decorate: A decorator or a list of decorators. These are
              applied to the callback in reverse order (on demand only).
            :param no_hooks: If true, application hooks are not triggered
              by this route. (default: False)
            :param template: The template to use for this callback.
              (default: no template)
            :param template_opts: A dict with additional template parameters.
            :param name: The name for this route. (default: None)
            :param callback: If set, the route decorator is directly applied
              to the callback and the callback is returned instead. This
              equals ``Bottle.route(...)(callback)``.
        """
        print 'path: {}'.format(path)  # path: /:filename#.+\.(css|js|ico|png|txt|html)#
        print 'method: {}'.format(method)  # method: GET
        print 'no_hooks: {}'.format(no_hooks)  # no_hooks: False
        print 'decorate: {}'.format(decorate)  # decorate: None
        print 'template: {}'.format(template)  # template: None
        print 'template_opts: {}'.format(template_opts)  # template_opts: {}
        print 'callback: {}'.format(callback)  # callback: None
        print 'name: {}'.format(name)  # name: None
        print 'static: {}'.format(static)  # static: False

        # @route can be used without any parameters
        print 'callable(path): {}'.format(callable(path))  # callable(path): False
        if callable(path):
            path, callback = None, path
        print 'path: {}'.format(path)  # path: /:filename#.+\.(css|js|ico|png|txt|html)#
        print 'callback: {}'.format(callback)  # callback: None

        # Build up the list of decorators
        decorators = makelist(decorate)
        print 'decorate: {}'.format(decorate)  # decorate: None

        if template:
            decorators.insert(0, view(template, **template_opts))
        print 'decorate: {}'.format(decorate)  # decorate: None

        if not no_hooks:
            decorators.append(self._add_hook_wrapper)
        print 'decorate: {}'.format(decorate)  # decorate: None

        # decorators.append(partial(self.apply_plugins, skiplist))
        def wrapper(func):
            print func.__name__  # static
            print makelist(path)  # ['/:filename#.+\\.(css|js|ico|png|txt|html)#']
            print yieldroutes(func)  # <generator object yieldroutes at 0x1613870>
            for rule in makelist(path) or yieldroutes(func):
                print rule  # /:filename#.+\.(css|js|ico|png|txt|html)#

                print makelist(method)  # ['GET']
                for verb in makelist(method):
                    if static:
                        rule = rule.replace(':', '\\:')
                        depr("Use backslash to escape ':' in routes.")
                    # TODO: Prepare this for plugins
                    print self.routes  # []
                    self.router.add(rule, verb, len(self.routes), name=name)
                    self.routes.append((func, decorators))
                    print self.routes  # [(<function static at 0x17ae140>, [<bound method Bottle._add_hook_wrapper of <evolution_0016.Bottle object at 0x122e350>>])]
            return func

        if callback:
            return wrapper(callback)
        else:
            return wrapper
        # return wrapper(callback) if callback else wrapper

    def _add_hook_wrapper(self, func):
        ''' Add hooks to a callable. See #84 '''

        @functools.wraps(func)
        def wrapper(*a, **ka):
            for hook in self.hooks['before_request']: hook()
            response.output = func(*a, **ka)
            for hook in self.hooks['after_request']: hook()
            return response.output

        return wrapper

    def get(self, path=None, method='GET', **kargs):
        """ Decorator: Bind a function to a GET request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def post(self, path=None, method='POST', **kargs):
        """ Decorator: Bind a function to a POST request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def put(self, path=None, method='PUT', **kargs):
        """ Decorator: Bind a function to a PUT request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def delete(self, path=None, method='DELETE', **kargs):
        """ Decorator: Bind a function to a DELETE request path.
            See :meth:'route' for details. """
        return self.route(path, method, **kargs)

    def error(self, code=500):
        """ Decorator: Register an output handler for a HTTP error code"""

        def wrapper(handler):
            self.error_handler[int(code)] = handler
            return handler

        return wrapper

    def hook(self, name):
        """ Return a decorator that adds a callback to the specified hook. """

        def wrapper(func):
            self.add_hook(name, func)
            return func

        return wrapper

    def add_hook(self, name, func):
        ''' Add a callback from a hook. '''
        if name not in self.hooks:
            raise ValueError("Unknown hook name %s" % name)
        if name in ('after_request'):
            self.hooks[name].insert(0, func)
        else:
            self.hooks[name].append(func)

    def remove_hook(self, name, func):
        ''' Remove a callback from a hook. '''
        if name not in self.hooks:
            raise ValueError("Unknown hook name %s" % name)
        self.hooks[name].remove(func)

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
            if isinstance(e, (KeyboardInterrupt, SystemExit, MemoryError)) \
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
        if isinstance(out, (tuple, list)) \
                and isinstance(out[0], (bytes, unicode)):
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
            environ['wsgi.errors'].write(err)  # TODO: wsgi.error should not get html
            start_response('500 INTERNAL SERVER ERROR', [('Content-Type', 'text/html')])
            return [tob(err)]

    def __call__(self, environ, start_response):
        return self.wsgi(environ, start_response)

