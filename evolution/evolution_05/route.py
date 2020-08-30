import re
from pprint import pprint

class BottleException(Exception):
    """ A base class for exceptions used by bottle. """
    pass


class RouteError(BottleException):
    """ This is a base class for all routing related exceptions """


class RouteSyntaxError(RouteError):
    """ The route parser found something not supported by this router """


class RouteBuildError(RouteError):
    """ The route could not been build """


class Route(object):
    syntax = re.compile(r'(.*?)(?<!\\):([a-zA-Z_]+)?(?:#(.*?)#)?')
    default = '[^/]+'

    def __init__(self, route, target, name=None, static=False):
        self.route = route
        self.target = target
        self.name = name
        self._static = static
        self._tokens = None

    @classmethod
    def tokenise(cls, route):
        """
        tokenise(self.route)
        """
        match = None
        for match in cls.syntax.finditer(route):
            pre, name, rex = match.groups()
            if pre:
                yield ('TXT', pre.replace('\\:',':'))
            if rex and name:
                yield ('VAR', (rex, name))
            elif name:
                yield ('VAR', (cls.default, name))
            elif rex:
                yield ('ANON', rex)
        if not match:
            yield ('TXT', route.replace('\\:',':'))
        elif match.end() < len(route):
            yield ('TXT', route[match.end():].replace('\\:',':'))

    def tokens(self):
        if not self._tokens:
            self._tokens = list(self.tokenise(self.route))
        return self._tokens

    def is_dynamic(self):
        if not self._static:
            for token, value in self.tokens():
                if token != 'TXT':
                    return True
        self._static = True
        return False

    @property
    def static(self):
        return not self.is_dynamic()

    def format_str(self):
        if self.static:
            return self.route.replace('%','%%')
        out, i = '', 0
        for token, value in self.tokens():
            if token == 'TXT':
                out += value.replace('%','%%')
            elif token == 'ANON':
                out += '%%(anon%d)s' % i; i+=1
            elif token == 'VAR':
                out += '%%(%s)s' % value[1]
        return out

    def group_re(self):
        out = ''
        for token, data in self.tokens():
            if token == 'TXT':
                out += re.escape(data)
            elif token == 'VAR':
                out += '(?P<%s>%s)' % (data[1], data[0])
            elif token == 'ANON':
                out += '(?:%s)' % data
        return out

    def flat_re(self):
        return re.sub(r'\(\?P<[^>]*>|\((?!\?)', '(?:', self.group_re())

    def __repr__(self):
        return self.route

    def __eq__(self, other):
        return self.route == other.route\
           and self.static == other.static\
           and self.name == other.name\
           and self.target == other.target


# for t in [
#     [('/static', 'static'), {}],
#     [('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'handler'), {}],
#     [('/:test', 'notail'), {}],
#     [(':test/', 'nohead'), {}],
#     [(':test', 'fullmatch'), {}],
#     [('/:#anon#/match', 'anon'), {}],
#     [('/:test/:name#[a-z]+#/', 'handler'), {'name': 'testroute'}],
#     [('/anon/:#.#', 'handler'), {'name': 'anonroute'}]
#     ]:
#     print(t)
#     route = Route(*t[0], **t[1])
#     print(route)
#     print('route.route: %r' % route.route)
#     print('route.target: %r' % route.target)
#     print('route.name: %r' % route.name)
#     print('route._static: %r' % route._static)
#     print('route._tokens: %r' % route._tokens)
#     print()
#     print('Route.tokenise(%r): %r' % (route.route, list(Route.tokenise(route.route))))
#     print('route.tokens(): %r' % route.tokens())
#     print('route.is_dynamic(): %r' % route.is_dynamic())
#     print('route.static: %r' % route.static)
#     print('route.format_str(): %r' % route.format_str())
#     print('route.group_re(): %r' % route.group_re())
#     print('route.flat_re(): %r' % route.flat_re())
#     print('=========================')

"""
[('/static', 'static'), {}]
/static
route.route: '/static'
route.target: 'static'
route.name: None
route._static: False
route._tokens: None
()
Route.tokenise('/static'): [('TXT', '/static')]
route.tokens(): [('TXT', '/static')]
route.is_dynamic(): False
route.static: True
route.format_str(): '/static'
route.group_re(): '\\/static'
route.flat_re(): '\\/static'
=========================
[('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'handler'), {}]
/\:its/:#.+#/:test/:name#[a-z]+#/
route.route: '/\\:its/:#.+#/:test/:name#[a-z]+#/'
route.target: 'handler'
route.name: None
route._static: False
route._tokens: None
()
Route.tokenise('/\\:its/:#.+#/:test/:name#[a-z]+#/'): [('TXT', '/:its/'), ('ANON', '.+'), ('TXT', '/'), ('VAR', ('[^/]+', 'test')), ('TXT', '/'), ('VAR', ('[a-z]+', 'name')), ('TXT', '/')]
route.tokens(): [('TXT', '/:its/'), ('ANON', '.+'), ('TXT', '/'), ('VAR', ('[^/]+', 'test')), ('TXT', '/'), ('VAR', ('[a-z]+', 'name')), ('TXT', '/')]
route.is_dynamic(): True
route.static: False
route.format_str(): '/:its/%(anon0)s/%(test)s/%(name)s/'
route.group_re(): '\\/\\:its\\/(?:.+)\\/(?P<test>[^/]+)\\/(?P<name>[a-z]+)\\/'
route.flat_re(): '\\/\\:its\\/(?:.+)\\/(?:[^/]+)\\/(?:[a-z]+)\\/'
=========================
[('/:test', 'notail'), {}]
/:test
route.route: '/:test'
route.target: 'notail'
route.name: None
route._static: False
route._tokens: None
()
Route.tokenise('/:test'): [('TXT', '/'), ('VAR', ('[^/]+', 'test'))]
route.tokens(): [('TXT', '/'), ('VAR', ('[^/]+', 'test'))]
route.is_dynamic(): True
route.static: False
route.format_str(): '/%(test)s'
route.group_re(): '\\/(?P<test>[^/]+)'
route.flat_re(): '\\/(?:[^/]+)'
=========================
[(':test/', 'nohead'), {}]
:test/
route.route: ':test/'
route.target: 'nohead'
route.name: None
route._static: False
route._tokens: None
()
Route.tokenise(':test/'): [('VAR', ('[^/]+', 'test')), ('TXT', '/')]
route.tokens(): [('VAR', ('[^/]+', 'test')), ('TXT', '/')]
route.is_dynamic(): True
route.static: False
route.format_str(): '%(test)s/'
route.group_re(): '(?P<test>[^/]+)\\/'
route.flat_re(): '(?:[^/]+)\\/'
=========================
[(':test', 'fullmatch'), {}]
:test
route.route: ':test'
route.target: 'fullmatch'
route.name: None
route._static: False
route._tokens: None
()
Route.tokenise(':test'): [('VAR', ('[^/]+', 'test'))]
route.tokens(): [('VAR', ('[^/]+', 'test'))]
route.is_dynamic(): True
route.static: False
route.format_str(): '%(test)s'
route.group_re(): '(?P<test>[^/]+)'
route.flat_re(): '(?:[^/]+)'
=========================
[('/:#anon#/match', 'anon'), {}]
/:#anon#/match
route.route: '/:#anon#/match'
route.target: 'anon'
route.name: None
route._static: False
route._tokens: None
()
Route.tokenise('/:#anon#/match'): [('TXT', '/'), ('ANON', 'anon'), ('TXT', '/match')]
route.tokens(): [('TXT', '/'), ('ANON', 'anon'), ('TXT', '/match')]
route.is_dynamic(): True
route.static: False
route.format_str(): '/%(anon0)s/match'
route.group_re(): '\\/(?:anon)\\/match'
route.flat_re(): '\\/(?:anon)\\/match'
=========================
[('/:test/:name#[a-z]+#/', 'handler'), {'name': 'testroute'}]
/:test/:name#[a-z]+#/
route.route: '/:test/:name#[a-z]+#/'
route.target: 'handler'
route.name: 'testroute'
route._static: False
route._tokens: None
()
Route.tokenise('/:test/:name#[a-z]+#/'): [('TXT', '/'), ('VAR', ('[^/]+', 'test')), ('TXT', '/'), ('VAR', ('[a-z]+', 'name')), ('TXT', '/')]
route.tokens(): [('TXT', '/'), ('VAR', ('[^/]+', 'test')), ('TXT', '/'), ('VAR', ('[a-z]+', 'name')), ('TXT', '/')]
route.is_dynamic(): True
route.static: False
route.format_str(): '/%(test)s/%(name)s/'
route.group_re(): '\\/(?P<test>[^/]+)\\/(?P<name>[a-z]+)\\/'
route.flat_re(): '\\/(?:[^/]+)\\/(?:[a-z]+)\\/'
=========================
[('/anon/:#.#', 'handler'), {'name': 'anonroute'}]
/anon/:#.#
route.route: '/anon/:#.#'
route.target: 'handler'
route.name: 'anonroute'
route._static: False
route._tokens: None
()
Route.tokenise('/anon/:#.#'): [('TXT', '/anon/'), ('ANON', '.')]
route.tokens(): [('TXT', '/anon/'), ('ANON', '.')]
route.is_dynamic(): True
route.static: False
route.format_str(): '/anon/%(anon0)s'
route.group_re(): '\\/anon\\/(?:.)'
route.flat_re(): '\\/anon\\/(?:.)'
=========================
"""


class Router(object):
    def __init__(self):
        self.routes = []     # List of all installed routes
        self.static = dict() # Cache for static routes
        self.dynamic = []    # Cache structure for dynamic routes
        self.named = dict()  # Cache for named routes and their format strings

    def add(self, *a, **ka):
        if a and isinstance(a[0], Route):
            route = a[0]
        else:
            route = Route(*a, **ka)

        self.routes.append(route)
        if route.name:
            self.named[route.name] = route.format_str()
        if route.static:
            self.static[route.route] = route.target
            return
        gpatt = route.group_re()
        fpatt = route.flat_re()
        try:
            if '(?P' in gpatt:
                gregexp = re.compile('^(%s)$' % gpatt)
            else:
                gregexp = None

            combined = '%s|(^%s$)' % (self.dynamic[-1][0].pattern, fpatt)
            self.dynamic[-1] = (
                re.compile(combined),
                self.dynamic[-1][1]
            )
            self.dynamic[-1][1].append((route.target, gregexp))
        except (AssertionError, IndexError) as e: # AssertionError: Too many groups
            self.dynamic.append(
                (
                    re.compile('(^%s$)' % fpatt),
                    [(route.target, gregexp)]
                )
            )
        except re.error as e:
            raise RouteSyntaxError("Could not add Route: %s (%s)" % (route, e))

    def match(self, uri):
        if uri in self.static:
            return self.static[uri], {}
        for combined, subroutes in self.dynamic:
            match = combined.match(uri)
            if not match:
                continue
            target, groups = subroutes[match.lastindex - 1]
            if groups:
                groups = groups.match(uri).groupdict()
            else:
                groups = {}
            return target, groups
        return None, {}

    def build(self, route_name, **args):
        """
        url = build('testroute', test='hello', name='world')
        url = '/hello/world/'
        """
        try:
            """
            self.named = {
                'anonroute': '/anon/%(anon0)s',
                'testroute': '/%(test)s/%(name)s/'
            }
            """
            return self.named[route_name] % args
        except KeyError:
            raise RouteBuildError("No route found with name '%s'." % route_name)

    def __eq__(self, other):
        return self.routes == other.routes

    def __str__(self):
        return 'routes: %r\nstatic: %r\ndynamic: %r\nnamed: %r' % (self.routes, self.static, self.dynamic, self.named)

    def __repr__(self):
        return 'routes: %r\n, static: %r\n, dynamic: %r\n, named: %r' % (self.routes, self.static, self.dynamic, self.named)



r = Router()
print(r)
for t in [
    [('/static', 'static'), {}],
    [('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'handler'), {}],
    [('/:test', 'notail'), {}],
    [(':test/', 'nohead'), {}],
    [(':test', 'fullmatch'), {}],
    [('/:#anon#/match', 'anon'), {}],
    [('/:test/:name#[a-z]+#/', 'handler'), {'name': 'testroute'}],
    [('/anon/:#.#', 'handler'), {'name': 'anonroute'}]
    ]:
    print(t)
    r.add(*t[0], **t[1])
    print(r)
    print('=========================')

"""
routes: []
static: {}
dynamic: []
named: {}
[('/static', 'static'), {}]
routes: [/static]
static: {'/static': 'static'}
dynamic: []
named: {}
=========================
[('/\\:its/:#.+#/:test/:name#[a-z]+#/', 'handler'), {}]
routes: [/static, /\:its/:#.+#/:test/:name#[a-z]+#/]
static: {'/static': 'static'}
dynamic: [
    (
        <_sre.SRE_Pattern object at 0x1eec3d0>,
        [('handler', <_sre.SRE_Pattern object at 0x1ee7290>)]
    )
]
named: {}
=========================
[('/:test', 'notail'), {}]
routes: [/static, /\:its/:#.+#/:test/:name#[a-z]+#/, /:test]
static: {'/static': 'static'}
dynamic: [
    (
        <_sre.SRE_Pattern object at 0x1ef8120>,
        [
            ('handler', <_sre.SRE_Pattern object at 0x1ee7290>),
            ('notail', <_sre.SRE_Pattern object at 0x7f274fa63cb0>)
        ]
    )
]
named: {}
=========================
[(':test/', 'nohead'), {}]
routes: [/static, /\:its/:#.+#/:test/:name#[a-z]+#/, /:test, :test/]
static: {'/static': 'static'}
dynamic: [
    (
        <_sre.SRE_Pattern object at 0x1ef3470>,
        [
            ('handler', <_sre.SRE_Pattern object at 0x1ee7290>),
            ('notail', <_sre.SRE_Pattern object at 0x7f274fa63cb0>),
            ('nohead', <_sre.SRE_Pattern object at 0x7f274fa63d78>)
        ]
    )
]
named: {}
=========================
[(':test', 'fullmatch'), {}]
routes: [/static, /\:its/:#.+#/:test/:name#[a-z]+#/, /:test, :test/, :test]
static: {'/static': 'static'}
dynamic: [
    (
        <_sre.SRE_Pattern object at 0x1efa2d0>,
        [
            ('handler', <_sre.SRE_Pattern object at 0x1ee7290>),
            ('notail', <_sre.SRE_Pattern object at 0x7f274fa63cb0>),
            ('nohead', <_sre.SRE_Pattern object at 0x7f274fa63d78>),
            ('fullmatch', <_sre.SRE_Pattern object at 0x7f274fa64ab0>)
        ]
    )
]
named: {}
=========================
[('/:#anon#/match', 'anon'), {}]
routes: [/static, /\:its/:#.+#/:test/:name#[a-z]+#/, /:test, :test/, :test, /:#anon#/match]
static: {'/static': 'static'}
dynamic: [
    (
        <_sre.SRE_Pattern object at 0x1efacc0>,
        [
            ('handler', <_sre.SRE_Pattern object at 0x1ee7290>),
            ('notail', <_sre.SRE_Pattern object at 0x7f274fa63cb0>),
            ('nohead', <_sre.SRE_Pattern object at 0x7f274fa63d78>),
            ('fullmatch', <_sre.SRE_Pattern object at 0x7f274fa64ab0>),
            ('anon', None)
        ]
    )
]
named: {}
=========================
[('/:test/:name#[a-z]+#/', 'handler'), {'name': 'testroute'}]
routes: [/static, /\:its/:#.+#/:test/:name#[a-z]+#/, /:test, :test/, :test, /:#anon#/match, /:test/:name#[a-z]+#/]
static: {'/static': 'static'}
dynamic: [
    (
        <_sre.SRE_Pattern object at 0x1efc0a0>,
        [
            ('handler', <_sre.SRE_Pattern object at 0x1ee7290>),
            ('notail', <_sre.SRE_Pattern object at 0x7f274fa63cb0>),
            ('nohead', <_sre.SRE_Pattern object at 0x7f274fa63d78>),
            ('fullmatch', <_sre.SRE_Pattern object at 0x7f274fa64ab0>),
            ('anon', None),
            ('handler', <_sre.SRE_Pattern object at 0x1efaa40>)
        ]
    )
]
named: {'testroute': '/%(test)s/%(name)s/'}
=========================
[('/anon/:#.#', 'handler'), {'name': 'anonroute'}]
routes: [/static, /\:its/:#.+#/:test/:name#[a-z]+#/, /:test, :test/, :test, /:#anon#/match, /:test/:name#[a-z]+#/, /anon/:#.#]
static: {'/static': 'static'}
dynamic: [
    (
        <_sre.SRE_Pattern object at 0x1efcb40>,
        [
            ('handler', <_sre.SRE_Pattern object at 0x1ee7290>),
            ('notail', <_sre.SRE_Pattern object at 0x7f274fa63cb0>),
            ('nohead', <_sre.SRE_Pattern object at 0x7f274fa63d78>),
            ('fullmatch', <_sre.SRE_Pattern object at 0x7f274fa64ab0>),
            ('anon', None),
            ('handler', <_sre.SRE_Pattern object at 0x1efaa40>),
            ('handler', None)
        ]
    )
]
named: {'anonroute': '/anon/%(anon0)s', 'testroute': '/%(test)s/%(name)s/'}
=========================
"""
