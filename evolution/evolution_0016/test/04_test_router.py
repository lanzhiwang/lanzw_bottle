# -*- coding: utf-8 -*-

import sys, os
test_root = os.path.dirname(os.path.abspath(__file__))  # /root/work/lanzw_frame/evolution/evolution_0016/test
os.chdir(test_root)
# print os.path.dirname(test_root)  # /root/work/lanzw_frame/evolution/evolution_0016
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

import unittest
import bottle

class TestRouter(unittest.TestCase):
    CGI=False
    
    def setUp(self):
        self.r = bottle.Router()
    
    def add(self, path, target, method='GET', **ka):
        self.r.add(path, method, target, **ka)

    def match(self, path, method='GET'):
        env = {'PATH_INFO': path, 'REQUEST_METHOD': method}
        if self.CGI:
            env['wsgi.run_once'] = 'true'
        return self.r.match(env)

    def assertMatches(self, rule, url, **args):
        self.add(rule, id(args))
        target, urlargs = self.match(url)
        # print 'rule: {}'.format(rule)
        # print 'url: {}'.format(url)
        # print 'args: {}'.format(args)
        # print 'id(args): {}'.format(id(args))
        # print 'target: {}'.format(target)
        # print 'urlargs: {}'.format(urlargs)
        # print '----------------' * 10

        """
        rule: /static
        url: /static
        args: {}
        id(args): 37874928
        target: 37874928
        urlargs: {}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /\:its/:#.+#/:test/:name#[a-z]+#/
        url: /:its/a/cruel/world/
        args: {'test': 'cruel', 'name': 'world'}
        id(args): 37407584
        target: 37407584
        urlargs: {'test': 'cruel', 'name': 'world'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /:test
        url: /test
        args: {'test': 'test'}
        id(args): 37882640
        target: 37882640
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: :test/
        url: test/
        args: {'test': 'test'}
        id(args): 37896688
        target: 37896688
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /:test/
        url: /test/
        args: {'test': 'test'}
        id(args): 37899760
        target: 37899760
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: :test
        url: test
        args: {'test': 'test'}
        id(args): 37902016
        target: 37902016
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /:#anon#/match
        url: /anon/match
        args: {}
        id(args): 37907024
        target: 37907024
        urlargs: {}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ...rule: /func(:param)
        url: /func(foo)
        args: {'param': 'foo'}
        id(args): 37899184
        target: 37899184
        urlargs: {'param': 'foo'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /func2(:param#(foo|bar)#)
        url: /func2(foo)
        args: {'param': 'foo'}
        id(args): 37894336
        target: 37894336
        urlargs: {'param': 'foo'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /func2(:param#(foo|bar)#)
        url: /func2(bar)
        args: {'param': 'bar'}
        id(args): 37924864
        target: 37924864
        urlargs: {'param': 'bar'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        .rule: /alpha/:abc
        url: /alpha/alpha
        args: {'abc': 'alpha'}
        id(args): 37894624
        target: 37894624
        urlargs: {'abc': 'alpha'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /alnum/:md5
        url: /alnum/sha1
        args: {'md5': 'sha1'}
        id(args): 37907968
        target: 37907968
        urlargs: {'md5': 'sha1'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        .rule: /static
        url: /static
        args: {}
        id(args): 37924288
        target: 37924288
        urlargs: {}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /\:its/:#.+#/:test/:name#[a-z]+#/
        url: /:its/a/cruel/world/
        args: {'test': 'cruel', 'name': 'world'}
        id(args): 37885680
        target: 37885680
        urlargs: {'test': 'cruel', 'name': 'world'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /:test
        url: /test
        args: {'test': 'test'}
        id(args): 37928544
        target: 37928544
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: :test/
        url: test/
        args: {'test': 'test'}
        id(args): 37927968
        target: 37927968
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /:test/
        url: /test/
        args: {'test': 'test'}
        id(args): 37927680
        target: 37927680
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: :test
        url: test
        args: {'test': 'test'}
        id(args): 37924576
        target: 37924576
        urlargs: {'test': 'test'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /:#anon#/match
        url: /anon/match
        args: {}
        id(args): 37929120
        target: 37929120
        urlargs: {}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ...rule: /func(:param)
        url: /func(foo)
        args: {'param': 'foo'}
        id(args): 37936832
        target: 37936832
        urlargs: {'param': 'foo'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /func2(:param#(foo|bar)#)
        url: /func2(foo)
        args: {'param': 'foo'}
        id(args): 37937984
        target: 37937984
        urlargs: {'param': 'foo'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /func2(:param#(foo|bar)#)
        url: /func2(bar)
        args: {'param': 'bar'}
        id(args): 37939024
        target: 37939024
        urlargs: {'param': 'bar'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        .rule: /alpha/:abc
        url: /alpha/alpha
        args: {'abc': 'alpha'}
        id(args): 37937696
        target: 37937696
        urlargs: {'abc': 'alpha'}
        ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        rule: /alnum/:md5s
        url: /alnum/sha1
        args: {'md5': 'sha1'}
        id(args): 37941744
        target: 37941744
        urlargs: {'md5': 'sha1'}
        """

        self.assertEqual(id(args), target)
        self.assertEqual(args, urlargs)

    def testBasic(self):
        self.assertMatches('/static', '/static')
        self.assertMatches('/\\:its/:#.+#/:test/:name#[a-z]+#/',
                           '/:its/a/cruel/world/',
                           test='cruel', name='world')
        self.assertMatches('/:test', '/test', test='test') # No tail
        self.assertMatches(':test/', 'test/', test='test') # No head
        self.assertMatches('/:test/', '/test/', test='test') # Middle
        self.assertMatches(':test', 'test', test='test') # Full wildcard
        self.assertMatches('/:#anon#/match', '/anon/match') # Anon wildcards
        self.assertRaises(bottle.HTTPError, self.match, '//no/m/at/ch/')

    def testWildcardNames(self):
        self.assertMatches('/alpha/:abc', '/alpha/alpha', abc='alpha')
        self.assertMatches('/alnum/:md5', '/alnum/sha1', md5='sha1')

    def testParentheses(self):
        self.assertMatches('/func(:param)', '/func(foo)', param='foo')
        self.assertMatches('/func2(:param#(foo|bar)#)', '/func2(foo)', param='foo')
        self.assertMatches('/func2(:param#(foo|bar)#)', '/func2(bar)', param='bar')
        self.assertRaises(bottle.HTTPError, self.match, '/func2(baz)')

    def testErrorInPattern(self):
        self.assertRaises(Exception, self.assertMatches, '/:bug#(#/', '/foo/')

    def testBuild(self):
        add = self.add
        build = self.r.build
        add('/:test/:name#[a-z]+#/', 'handler', name='testroute')
        add('/anon/:#.#', 'handler', name='anonroute')
        url = build('testroute', test='hello', name='world')
        self.assertEqual('/hello/world/', url)
        self.assertRaises(bottle.RouteBuildError, build, 'test')
        # RouteBuildError: No route found with name 'test'.
        self.assertRaises(bottle.RouteBuildError, build, 'testroute')
        # RouteBuildError: Missing parameter 'test' in route 'testroute'
        #self.assertRaises(bottle.RouteBuildError, build, 'testroute', test='hello', name='1234')
        # RouteBuildError: Parameter 'name' does not match pattern for route 'testroute': '[a-z]+'
        #self.assertRaises(bottle.RouteBuildError, build, 'anonroute')
        # RouteBuildError: Anonymous pattern found. Can't generate the route 'anonroute'.

class TestRouterInCGIMode(TestRouter):
    CGI = True


if __name__ == '__main__': #pragma: no cover
    unittest.main()
