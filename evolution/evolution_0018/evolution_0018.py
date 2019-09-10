# -*- coding: utf-8 -*-

import functools

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


class Router(object):
    pass


class Request(object):
    pass


class Response(object):
    pass


request = Request()

response = Response()


def dict2json(d):
    response.content_type = 'application/json'
    return json_dumps(d)


def makelist(data):
    if isinstance(data, (tuple, list, set, dict)): return list(data)
    elif data: return [data]
    else: return []


def view(tpl, **tplo):
    pass


def yieldroutes(func):
    """ Return a generator for routes that match the signature (name, args)
    of the func parameter. This may yield more than one route if the function
    takes optional keyword arguments. The output is best described by example::

        a()         -> '/a'
        b(x, y)     -> '/b/:x/:y'
        c(x, y=5)   -> '/c/:x' and '/c/:x/:y'
        d(x=5, y=6) -> '/d' and '/d/:x' and '/d/:x/:y'
    """
    import inspect  # Expensive module. Only import if necessary.
    path = '/' + func.__name__.replace('__', '/').lstrip('/')
    spec = inspect.getargspec(func)
    argc = len(spec[0]) - len(spec[3] or [])
    path += ('/:%s' * argc) % tuple(spec[0][:argc])
    yield path
    for arg in spec[0][argc:]:
        path += '/:%s' % arg
        yield path


class Bottle(object):
    def __init__(self, catchall=True, autojson=True, config=None):
        self.routes = []  # List of installed routes including metadata.
        # self.routes.append(cfg)

        self.router = Router()  # Maps requests to self.route indices.
        self.ccache = {}  # Cache for callbacks with plugins applied.

        self.plugins = []  # List of installed plugins.
        self.plugins.append(self._add_hook_wrapper)
        # plugins = [_add_hook_wrapper]

        self.mounts = {}
        self.error_handler = {}
        #: If true, most exceptions are catched and returned as :exc:`HTTPError`
        self.catchall = catchall

        self.config = config or {}
        # config.update(apply=plugins, skip=skiplist)
        # cfg.update(rule=rule, method=verb, callback=callback)

        self.serve = True

        self.castfilter = []
        # self.castfilter.append((ftype, func))

        if autojson and json_dumps:
            self.add_filter(dict, dict2json)

        self.hooks = {'before_request': [], 'after_request': []}

    def _add_hook_wrapper(self, func):
        ''' Add hooks to a callable. See #84 '''
        @functools.wraps(func)
        def wrapper(*a, **ka):
            for hook in self.hooks['before_request']:
                hook()
            response.output = func(*a, **ka)
            for hook in self.hooks['after_request']:
                hook()
            return response.output
        return wrapper

    def add_filter(self, ftype, func):
        ''' Register a new output filter. Whenever bottle hits a handler output
            matching `ftype`, `func` is applied to it. '''
        if not isinstance(ftype, type):
            raise TypeError("Expected type object, got %s" % type(ftype))
        self.castfilter = [(t, f) for (t, f) in self.castfilter if t != ftype]
        self.castfilter.append((ftype, func))
        self.castfilter.sort()


    def match(self, environ):
        handle, args = self.router.match(environ)
        environ['route.handle'] = handle # TODO move to router?
        environ['route.url_args'] = args
        try:
            return self.ccache[handle], args
        except KeyError:
            config = self.routes[handle]
            callback = self.ccache[handle] = self._build_callback(config)
            return callback, args

    def _build_callback(self, config):
        ''' Apply plugins to a route and return a new callable. '''
        wrapped = config['callback']
        plugins = self.plugins + config.get('apply', [])
        skip    = config['skip']
        try:
            for plugin in reversed(plugins):
                if True in skip:
                    break
                if plugin in skip or type(plugin) in skip:
                    continue
                if getattr(plugin, 'name', True) in skip:
                    continue
                if hasattr(plugin, 'apply'):
                    wrapped = plugin.apply(wrapped, self, config)
                else:
                    wrapped = plugin(wrapped)
                if not wrapped:
                    break
                functools.update_wrapper(wrapped, config['callback'])
            return wrapped
        except PluginReset: # A plugin may have changed the config dict inplace.
            return self.build_handler(config) # Apply all plugins again.


    def route(self, path=None, method='GET', callback=None, name=None,
              apply=None, skip=None, **config):

        if callable(path):
            path, callback = None, path

        plugins = makelist(apply)
        # plugins = [apply]

        skiplist = makelist(skip)
        # skiplist = [skip]

        if 'decorate' in config:  # decorate=[revdec, titledec]
            plugins += makelist(config.pop('decorate'))
        # plugins = [apply, decorate]

        if 'template' in config:  # template='test {{a}} {{b}}', template_opts={'b': 6}
            tpl, tplo = config.pop('template'), config.pop('template_opts', {})
            plugins.insert(0, view(tpl, **tplo))
        # plugins = [view(tpl, **tplo), apply, decorate]

        if config.pop('no_hooks', False):  # no_hooks=True
            skiplist.append(self._add_hook_wrapper)
        # skiplist = [skip, _add_hook_wrapper]

        static = config.pop('static', False)  # depr 0.9

        config.update(apply=plugins, skip=skiplist)

        def decorator(callback):
            # route(['/a','/b'])
            for rule in makelist(path) or yieldroutes(callback):
                for verb in makelist(method):
                    verb = verb.upper()
                    cfg = config.copy()
                    cfg.update(rule=rule, method=verb, callback=callback)
                    self.routes.append(cfg)
                    handle = self.routes.index(cfg)
                    self.router.add(rule, verb, handle, name=name, static=static)
            return callback

        # bottle.route(callback=test)
        if callback:
            return decorator(callback)
        else:
            return decorator

    def handle(self, environ, method='GET'):
        """ Execute the first matching route callback and return the result.
            :exc:`HTTPResponse` exceptions are catched and returned. If :attr:`Bottle.catchall` is true, other exceptions are catched as
            well and returned as :exc:`HTTPError` instances (500).
        """
        if isinstance(environ, str):
            depr("Bottle.handle() takes an environ dictionary.") # v0.9
            environ = {'PATH_INFO': environ, 'REQUEST_METHOD': method.upper()}
        if not self.serve:
            return HTTPError(503, "Server stopped")
        try:
            callback, args = self.match(environ)
            return callback(**args)
        except HTTPResponse, r:
            return r
        except PluginReset: # Route reset requested by the callback or a plugin.
            del self.ccache[handle]
            return self.handle(environ) # Try again.
        except (KeyboardInterrupt, SystemExit, MemoryError):
            raise
        except Exception, e:
            if not self.catchall: raise
            return HTTPError(500, "Internal Server Error", e, format_exc(10))

        try:
            return (self.handler or self.build_handler())(**args)
        except RouteReset:
            self.reset()
            return self(**args)
