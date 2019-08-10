import unittest
import sys, os.path
# print __file__  # test_routes.py
# print os.path.abspath(__file__)  # /root/work/lanzw_frame/evolution/evolution_0011_v_0.0.3/test/test_routes.py
TESTDIR = os.path.dirname(os.path.abspath(__file__))
# print TESTDIR  # /root/work/lanzw_frame/evolution/evolution_0011_v_0.0.3/test/
DISTDIR = os.path.dirname(TESTDIR)
# print DISTDIR  # /root/work/lanzw_frame/evolution/evolution_0011_v_0.0.3
# print sys.path
sys.path.insert(0, TESTDIR)
sys.path.insert(0, DISTDIR)
# print sys.path

from evolution_0011 import route, add_route, match_url, compile_route, ROUTES_REGEXP, ROUTES_SIMPLE

class TestRoutes(unittest.TestCase):

    def test_static(self):
        """ Routes: Static routes """ 
        token = 'abc'
        routes = ['','/','/abc','abc','/abc/','/abc/def','/abc/def.ghi']
        for r in routes:
            print r
            add_route(r, token, simple=True)
            print ROUTES_SIMPLE
        """
        ''
        {'GET': {'': 'abc'}}
        /
        {'GET': {'': 'abc'}}
        /abc
        {'GET': {'': 'abc', 'abc': 'abc'}}
        abc
        {'GET': {'': 'abc', 'abc': 'abc'}}
        /abc/
        {'GET': {'': 'abc', 'abc': 'abc', 'abc/': 'abc'}}
        /abc/def
        {'GET': {'': 'abc', 'abc': 'abc', 'abc/def': 'abc', 'abc/': 'abc'}}
        /abc/def.ghi
        {'GET': {'': 'abc', 'abc/def.ghi': 'abc', 'abc': 'abc', 'abc/def': 'abc', 'abc/': 'abc'}}
        """
        self.assertTrue('GET' in ROUTES_SIMPLE)
        r = [r for r in ROUTES_SIMPLE['GET'].values() if r == 'abc']
        self.assertEqual(5, len(r))
        for r in routes:
            print 'match_url(r): {}'.format(match_url(r))
            """
            match_url(r): ('abc', {})
            match_url(r): ('abc', {})
            match_url(r): ('abc', {})
            match_url(r): ('abc', {})
            match_url(r): ('abc', {})
            match_url(r): ('abc', {})
            match_url(r): ('abc', {})
            """
            self.assertEqual(token, match_url(r)[0])

    def test_dynamic(self):
        """ Routes: Dynamic routes """ 
        token = 'abcd'
        add_route('/:a/:b', token)
        print "ROUTES_REGEXP: {}".format(ROUTES_REGEXP)
        # ROUTES_REGEXP: {'GET': [[<_sre.SRE_Pattern object at 0x1b2f3b0>, 'abcd']]}
        self.assertTrue('GET' in ROUTES_REGEXP)

        print "match_url('/aa/bb'): {}".format(match_url('/aa/bb'))
        # match_url('/aa/bb'): ('abcd', {'a': 'aa', 'b': 'bb'})

        print "match_url('/aa'): {}".format(match_url('/aa'))
        # match_url('/aa'): (None, None)

        self.assertEqual(token, match_url('/aa/bb')[0])
        self.assertEqual(None, match_url('/aa')[0])
        self.assertEqual(repr({'a':'aa','b':'bb'}), repr(match_url('/aa/bb')[1]))


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestRoutes))

if __name__ == '__main__':
    unittest.main()
