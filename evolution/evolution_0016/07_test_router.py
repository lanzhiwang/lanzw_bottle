# -*- coding: utf-8 -*-

import re
import functools


class HTTPError(object):
    pass


class BottleException(Exception):
    """ A base class for exceptions used by bottle. """
    pass


class RouteError(BottleException):
    """ This is a base class for all routing related exceptions """


class RouteSyntaxError(RouteError):
    """ The route parser found something not supported by this router """


class RouteBuildError(RouteError):
    """ The route could not been built """


class lazy_attribute(object):  # Does not need configuration -> lower-case name
    ''' A property that caches itself to the class object. '''

    def __init__(self, func):
        functools.update_wrapper(self, func, updated=[])
        self.getter = func

    def __get__(self, obj, cls):
        value = self.getter(cls)
        setattr(cls, self.__name__, value)
        return value


class Router(object):
    default = '[^/]+'

    @lazy_attribute
    def syntax(cls):
        return re.compile(r'(?<!\\):([a-zA-Z_][a-zA-Z_0-9]*)?(?:#(.*?)#)?')

    """
    等价于
    syntax = lazy_attribute(syntax)
    syntax = re.compile(r'(?<!\\):([a-zA-Z_][a-zA-Z_0-9]*)?(?:#(.*?)#)?')
    """

    def __init__(self):
        self.routes = {}  # A {rule: {method: target}} mapping
        self.rules = []  # An ordered list of rules
        self.named = {}  # A name->(rule, build_info) mapping
        self.static = {}  # Cache for static routes: {path: {method: target}}
        self.dynamic = []  # Cache for dynamic routes. See _compile()


    """
    self.router.add(rule, verb, len(self.routes), name=name)

    add('/static', method, target, name=None)
    add('/\\:its/:#.+#/:test/:name#[a-z]+#/', method, target, name=None)
    add('/:test', method, target, name=None)
    add(':test/', method, target, name=None)
    add('/:test/', method, target, name=None)
    add('test', method, target, name=None)
    add(':#anon#/match', method, target, name=None)
    add('/alpha/:abc', method, target, name=None)
    add('/alnum/:md5', method, target, name=None)
    add('/func(:param)', method, target, name=None)
    add('/func2(:param#(foo|bar)#)', method, target, name=None)
    add('/:test/:name#[a-z]+#/', method, target, name=None)
    add('/anon/:#.#', method, target, name=None)
    """
    def add(self, rule, method, target, name=None):
        ''' Add a new route or overwrite an existing target. '''
        # print 'routes: {}'.format(self.routes)
        # print 'rules: {}'.format(self.rules)
        # print 'named: {}'.format(self.named)
        # print 'static: {}'.format(self.static)
        # print 'dynamic: {}'.format(self.dynamic)
        # print '-----------' * 10

        if rule in self.routes:
            self.routes[rule][method.upper()] = target
        else:
            self.routes[rule] = {method.upper(): target}
            self.rules.append(rule)
            if self.static or self.dynamic:  # Clear precompiler cache.
                self.static, self.dynamic = {}, {}
        if name:
            self.named[name] = (rule, None)

    """
    routes: 
    {
    '/\\:its/:#.+#/:test/:name#[a-z]+#/': {'PUT': 10, 'POST': 9, 'ALL': 12, 'HEAD': 11, 'GET': 8}, 
    '/func(:param)': {'GET': 7}, 
    '/static': {'ALL': 5, 'GET': 1, 'HEAD': 4, 'PUT': 3, 'POST': 2, 'DELETE': 6}, 
    '/': {'GET': 0}
    }
        
    named: 
    {
    'name10': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name11': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name12': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name6': ('/static', None), 
    'name7': ('/func(:param)', None), 
    'name4': ('/static', None), 
    'name5': ('/static', None), 
    'name2': ('/static', None), 
    'name3': ('/static', None), 
    'name0': ('/', None), 
    'name1': ('/static', None), 
    'name8': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name9': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None)
    }
    """
    def delete(self, rule, method=None):
        ''' Delete an existing route. Omit `method` to delete all targets. '''
        if rule not in self.routes and rule in self.named:
            rule = self.named[rule][0]
        if rule in self.routes:
            if method:
                del self.routes[rule][method]
            else:
                self.routes[rule].clear()
            if not self.routes[rule]:
                del self.routes[rule]
                self.rules.remove(rule)

    def build(self, _name, *anon, **args):
        ''' Return a string that matches a named route. Use keyword arguments
            to fill out named wildcards. Remaining arguments are appended as a
            query string. Raises RouteBuildError or KeyError.'''
        if _name not in self.named:
            raise RouteBuildError("No route with that name.", _name)
        rule, pairs = self.named[_name]
        if not pairs:
            token = self.syntax.split(rule)
            parts = [p.replace('\\:', ':') for p in token[::3]]
            names = token[1::3]
            if len(parts) > len(names): names.append(None)
            pairs = zip(parts, names)
            self.named[_name] = (rule, pairs)
        try:
            anon = list(anon)
            url = [s if k is None
                   else s + str(args.pop(k)) if k else s + str(anon.pop())
                   for s, k in pairs]
        except IndexError:
            msg = "Not enough arguments to fill out anonymous wildcards."
            raise RouteBuildError(msg)
        except KeyError, e:
            raise RouteBuildError(*e.args)

        if args: url += ['?', urlencode(args.iteritems())]
        return ''.join(url)

    """
    env = {'PATH_INFO': '/static', 'REQUEST_METHOD': 'get'}
    env = {'PATH_INFO': '/:its/a/cruel/world/', 'REQUEST_METHOD': 'get'}
    
    env = {'PATH_INFO': path, 'REQUEST_METHOD': method}
    match(env)
    """
    def match(self, environ):
        ''' Return a (target, url_agrs) tuple or raise HTTPError(404/405). '''
        targets, urlargs = self._match_path(environ)
        # print 'targets:{}, urlargs:{}'.format(targets, urlargs)
        # targets:{'ALL': 5, 'GET': 1, 'HEAD': 4, 'PUT': 3, 'POST': 2, 'DELETE': 6}, urlargs:{}
        if not targets:
            raise HTTPError(404, "Not found: " + environ['PATH_INFO'])
        environ['router.url_args'] = urlargs
        method = environ['REQUEST_METHOD'].upper()
        if method in targets:
            return targets[method], urlargs
        if method == 'HEAD' and 'GET' in targets:
            return targets['GET'], urlargs
        if 'ANY' in targets:
            return targets['ANY'], urlargs
        allowed = [verb for verb in targets if verb != 'ANY']
        if 'GET' in allowed and 'HEAD' not in allowed:
            allowed.append('HEAD')
        raise HTTPError(405, "Method not allowed.",
                        header=[('Allow', ",".join(allowed))])


    """
    env = {'PATH_INFO': '/static', 'REQUEST_METHOD': 'get'}
    env = {'PATH_INFO': '/:its/a/cruel/world/', 'REQUEST_METHOD': 'get'}
    """
    def _match_path(self, environ):
        # print 'static: {}'.format(self.static)
        # print 'dynamic: {}'.format(self.dynamic)
        """
        static: {}
        dynamic: []
        
        static: 
        {
        '/static': {'ALL': 5, 'GET': 1, 'HEAD': 4, 'PUT': 3, 'POST': 2, 'DELETE': 6}, 
        '/': {'GET': 0}
        }
        dynamic: [(<_sre.SRE_Pattern object at 0x1d96200>, [(<_sre.SRE_Pattern object at 0x7f99881eebf8>, {'GET': 7}), (<_sre.SRE_Pattern object at 0x1d80850>, {'ALL': 12, 'GET': 8, 'HEAD': 11, 'PUT': 10, 'POST': 9, 'DELETE': 13})])]
        [(                                                    ), (), ()]
        [(<re>, [                                            ]), (), ()]
        [(<re>, [(                                      ), ()]), (), ()]
        [(<re>, [(<re>, {method: target, method: target}), ()]), (), ()]
        """

        ''' Optimized PATH_INFO matcher. '''
        path = environ['PATH_INFO'] or '/'  # /:its/a/cruel/world/

        # Assume we are in a warm state. Search compiled rules first.
        match = self.static.get(path)
        if match:
            return match, {}

        for combined, rules in self.dynamic:
            # print combined  # <_sre.SRE_Pattern object at 0x1d96200>
            # print rules  # [(<_sre.SRE_Pattern object at 0x7f99881eebf8>, {'GET': 7}), (<_sre.SRE_Pattern object at 0x1d80850>, {'ALL': 12, 'GET': 8, 'HEAD': 11, 'PUT': 10, 'POST': 9, 'DELETE': 13})]
            match = combined.match(path)
            if not match:
                continue
            gpat, match = rules[match.lastindex - 1]
            return match, gpat.match(path).groupdict() if gpat else {}

        # Lazy-check if we are really in a warm state. If yes, stop here.
        if self.static or self.dynamic or not self.routes:
            return None, {}

        # Cold state: We have not compiled any rules yet. Do so and try again.
        if not environ.get('wsgi.run_once'):
            self._compile()
            return self._match_path(environ)

        # For run_once (CGI) environments, don't compile. Just check one by one.
        epath = path.replace(':', '\\:')  # Turn path into its own static rule.
        match = self.routes.get(epath)  # This returns static rule only.
        if match:
            return match, {}
        for rule in self.rules:
            #: Skip static routes to reduce re.compile() calls.
            if rule.count(':') < rule.count('\\:'):
                continue
            match = self._compile_pattern(rule).match(path)
            if match:
                return self.routes[rule], match.groupdict()
        return None, {}

    """
    env = {'PATH_INFO': '/static', 'REQUEST_METHOD': 'get'}
    env = {'PATH_INFO': '/:its/a/cruel/world/', 'REQUEST_METHOD': 'get'}
    """
    def _compile(self):
        ''' Prepare static and dynamic search structures. '''
        self.static = {}
        self.dynamic = []

        def fpat_sub(m):
            return m.group(0) if len(m.group(1)) % 2 else m.group(1) + '(?:'

        # rules: ['/', '/static', '/func(:param)', '/\\:its/:#.+#/:test/:name#[a-z]+#/']
        """
        routes: 
        {
        '/\\:its/:#.+#/:test/:name#[a-z]+#/': {'PUT': 10, 'POST': 9, 'ALL': 12, 'HEAD': 11, 'GET': 8}, 
        '/func(:param)': {'GET': 7}, 
        '/static': {'ALL': 5, 'GET': 1, 'HEAD': 4, 'PUT': 3, 'POST': 2, 'DELETE': 6}, 
        '/': {'GET': 0}
        }
        """
        for rule in self.rules:
            target = self.routes[rule]
            if not self.syntax.search(rule):
                self.static[rule.replace('\\:', ':')] = target
                continue
            gpat = self._compile_pattern(rule)
            fpat = re.sub(r'(\\*)(\(\?P<[^>]*>|\((?!\?))', fpat_sub, gpat.pattern)
            gpat = gpat if gpat.groupindex else None
            try:
                combined = '%s|(%s)' % (self.dynamic[-1][0].pattern, fpat)
                self.dynamic[-1] = (re.compile(combined), self.dynamic[-1][1])
                self.dynamic[-1][1].append((gpat, target))
            except (AssertionError, IndexError), e:  # AssertionError: Too many groups
                self.dynamic.append((re.compile('(^%s$)' % fpat),
                                     [(gpat, target)]))
            except re.error, e:
                raise RouteSyntaxError("Could not add Route: %s (%s)" % (rule, e))

    # '/'
    # '/static'
    # '/func(:param)'
    # '/\\:its/:#.+#/:test/:name#[a-z]+#/'
    def _compile_pattern(self, rule):
        ''' Return a regular expression with named groups for each wildcard. '''
        out = ''
        for i, part in enumerate(self.syntax.split(rule)):
            if i % 3 == 0:
                out += re.escape(part.replace('\\:', ':'))
            elif i % 3 == 1:
                out += '(?P<%s>' % part if part else '(?:'
            else:
                out += '%s)' % (part or '[^/]+')
        return re.compile('^%s$' % out)



if __name__ == '__main__':
    r = Router()
    add = r.add

    add('/', 'get', 0, name='name0')
    add('/static', 'get', 1, name='name1')
    add('/static', 'post', 2, name='name2')
    add('/static', 'put', 3, name='name3')
    add('/static', 'head', 4, name='name4')
    add('/static', 'all', 5, name='name5')
    add('/static', 'delete', 6, name='name6')

    add('/func(:param)', 'get', 7, name='name7')
    add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'get', 8, name='name8')
    add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'post', 9, name='name9')
    add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'put', 10, name='name10')
    add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'head', 11, name='name11')
    add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'all', 12, name='name12')
    add('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'delete', 13, name='name13')

    """
    routes: 
    {
    '/\\:its/:#.+#/:test/:name#[a-z]+#/': {'PUT': 10, 'POST': 9, 'ALL': 12, 'HEAD': 11, 'GET': 8}, 
    '/func(:param)': {'GET': 7}, 
    '/static': {'ALL': 5, 'GET': 1, 'HEAD': 4, 'PUT': 3, 'POST': 2, 'DELETE': 6}, 
    '/': {'GET': 0}
    }
    
    rules: ['/', '/static', '/func(:param)', '/\\:its/:#.+#/:test/:name#[a-z]+#/']
    
    named: 
    {
    'name10': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name11': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name12': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name6': ('/static', None), 
    'name7': ('/func(:param)', None), 
    'name4': ('/static', None), 
    'name5': ('/static', None), 
    'name2': ('/static', None), 
    'name3': ('/static', None), 
    'name0': ('/', None), 
    'name1': ('/static', None), 
    'name8': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None), 
    'name9': ('/\\:its/:#.+#/:test/:name#[a-z]+#/', None)
    }
    
    static: {}
    dynamic: []
    """

    env = {'PATH_INFO': '/:its/a/cruel/world/', 'REQUEST_METHOD': 'get'}
    print r.match(env)  # (8, {'test': 'cruel', 'name': 'world'})
