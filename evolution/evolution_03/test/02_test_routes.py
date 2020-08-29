#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sys, os.path
from bottle import route, Bottle, BaseController
from wsgiref.util import setup_testing_defaults


class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.wsgi = Bottle()

    def test_static(self):
        """ Routes: Static routes """
        app = Bottle()
        token = 'abc'
        routes = ['','/','/abc','abc','/abc/','/abc/def','/abc/def.ghi']
        for r in routes:
            app.add_route(r, token, simple=True)
        # print(app.simple_routes)
        """
        {
            'GET': {
                '': 'abc',
                'abc/def.ghi': 'abc',
                'abc': 'abc',
                'abc/def': 'abc',
                'abc/': 'abc'
            },
            'POST': {}
        }
        """
        self.assertTrue('GET' in app.simple_routes)
        r = [r for r in app.simple_routes['GET'].values() if r == 'abc']
        self.assertEqual(5, len(r))
        for r in routes:
            self.assertEqual(token, app.match_url(r)[0])

    def test_dynamic(self):
        """ Routes: Dynamic routes """ 
        app = Bottle()
        token = 'abcd'
        app.add_route('/:a/:b', token)
        # print(app.regexp_routes)
        """
        {
            'GET': [[<_sre.SRE_Pattern object at 0x20b5c70>, 'abcd'], []],
            'POST': [[], []]
        }
        """
        self.assertTrue('GET' in app.regexp_routes)
        self.assertEqual(token, app.match_url('/aa/bb')[0])
        self.assertEqual(None, app.match_url('/aa')[0])
        self.assertEqual(repr({'a':'aa','b':'bb'}), repr(app.match_url('/aa/bb')[1]))

    def test_default(self):
        """ Routes: Decorator and default routes """
        app = Bottle()
        token = 'abc'
        @app.route('/exists')
        def test1():
            return 'test1'
        @app.default()
        def test2():
            return 'test2'
        self.assertEqual(test1, app.match_url('/exists')[0])
        self.assertNotEqual(test2, app.match_url('/exists')[0])
        self.assertEqual(test2, app.match_url('/does_not_exist')[0])
        self.assertNotEqual(test1, app.match_url('/does_not_exist')[0])

    def test_controller(self):
        """ Routes: Controller Syntax """
        """ Not testing decorator mode here because it is a SyntaxError in Python 2.5 """
        app = Bottle()
        class CTest(BaseController):
            def _no(self): return 'no'
            def yes(self): return 'yes'
            def yes2(self, test): return test
        app.add_route('/ctest/{action}', CTest)
        app.add_route('/ctest/yes/:test', CTest, action='yes2')

        # print(app.simple_routes)
        """
        {
            'GET': {
                'ctest/yes2': <bound method CTest.yes2 of <__main__.CTest object at 0x24c50d0>>,
                'ctest/yes': <bound method CTest.yes of <__main__.CTest object at 0x24c50d0>>
            }
        }
        """

        # print(app.regexp_routes)
        """
        {
            'GET': [[<_sre.SRE_Pattern object at 0x2338630>, <bound method CTest.yes2 of <__main__.CTest object at 0x24c50d0>>]]
        }

        """

        self.assertEqual(None, app.match_url('/ctest/no')[0])
        self.assertEqual(None, app.match_url('/ctest/_no')[0])
        self.assertEqual('yes', app.match_url('/ctest/yes')[0]())
        self.assertEqual('test', app.match_url('/ctest/yes/test')[0](test='test'))


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestRoutes))

if __name__ == '__main__':
    unittest.main()
