import unittest
import sys, os.path
from bottle import request, response
from Cookie import SimpleCookie
try:
    from urlparse import parse_qs
except ImportError: # pragma: no cover
    from cgi import parse_qs
import cgi


"""
>>> sys.version_info
sys.version_info(major=2, minor=7, micro=5, releaselevel='final', serial=0)
>>>
"""
if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO


t = dict()
t['a=a'] = {'a': 'a'}
t['a=a; b=b'] = {'a': 'a', 'b':'b'}
t['a=a; a=b'] = {'a': 'b'}
print(t)
"""
{
    'a=a': {'a': 'a'},
    'a=a; b=b': {'a': 'a', 'b': 'b'},
    'a=a; a=b': {'a': 'b'}
}
"""
for k, v in t.iteritems():
    print(k, v)
    raw_dict = SimpleCookie(k)
    print(raw_dict)
    _COOKIES = {}
    for cookie in raw_dict.itervalues():
        print(cookie)
        _COOKIES[cookie.key] = cookie.value
        print(_COOKIES)
"""
('a=a', {'a': 'a'})
Set-Cookie: a=a
Set-Cookie: a=a
{'a': 'a'}
('a=a; b=b', {'a': 'a', 'b': 'b'})
Set-Cookie: a=a
Set-Cookie: b=b
Set-Cookie: a=a
{'a': 'a'}
Set-Cookie: b=b
{'a': 'a', 'b': 'b'}
('a=a; a=b', {'a': 'b'})
Set-Cookie: a=b
Set-Cookie: a=b
{'a': 'b'}
"""


sq = 'a=a&b=b&c=c'
qd = {'a':'a', 'b':'b','c':'c'}
e = {}
e['wsgi.input'] = StringIO(sq)
e['wsgi.input'].seek(0)
e['QUERY_STRING'] = sq
print(e)  # {'QUERY_STRING': 'a=a&b=b&c=c', 'wsgi.input': <StringIO.StringIO instance at 0x7f500f1b3830>}
request.bind(e)
print(request.GET)  # {'a': 'a', 'c': 'c', 'b': 'b'}
print(request.POST)  # {'a': 'a', 'c': 'c', 'b': 'b'}
print(request.params)  # {'a': 'a', 'c': 'c', 'b': 'b'}
print(parse_qs(e['QUERY_STRING'], keep_blank_values=True))  # {'a': ['a'], 'c': ['c'], 'b': ['b']}
print(parse_qs('a=a&a=1', keep_blank_values=True))  # {'a': ['a', '1']}






class TestEnviron(unittest.TestCase):

    def test_path(self):
        """ Environ: PATH_INFO """
        t = dict()
        t[''] = '/'
        t['bla'] = '/bla'
        t['bla/'] = '/bla/'
        t['/bla'] = '/bla'
        t['/bla/'] = '/bla/'
        # print(t)
        """
        {
            '': '/',
            '/bla/': '/bla/',
            'bla': '/bla',
            '/bla': '/bla',
            'bla/': '/bla/'
        }
        """
        for k, v in t.iteritems():
            request.bind({'PATH_INFO': k})
            self.assertEqual(v, request.path)
        request.bind({})
        self.assertEqual('/', request.path)


    def test_ilength(self):
        """ Environ: CONTENT_LENGTH """
        t = dict()
        t[''] = 0
        t['0815'] = 815
        t['-666'] = 0
        t['0'] = 0
        t['a'] = 0
        # print(t)
        """
        {
            '': 0,
            '0': 0,
            '0815': 815,
            '-666': 0,
            'a': 0
        }
        """
        for k, v in t.iteritems():
            request.bind({'CONTENT_LENGTH': k})
            self.assertEqual(v, request.input_length)
        request.bind({})
        self.assertEqual(0, request.input_length)

    def test_cookie(self):
        """ Environ: COOKIES """
        t = dict()
        t['a=a'] = {'a': 'a'}
        t['a=a; b=b'] = {'a': 'a', 'b':'b'}
        t['a=a; a=b'] = {'a': 'b'}
        # print(t)
        """
        {
            'a=a': {'a': 'a'},
            'a=a; b=b': {'a': 'a', 'b': 'b'},
            'a=a; a=b': {'a': 'b'}
        }
        """
        for k, v in t.iteritems():
            request.bind({'HTTP_COOKIE': k})
            self.assertEqual(v, request.COOKIES)

    def test_getpost(self):
        """ Environ: GET and POST (simple) """
        sq = 'a=a&b=b&c=c'
        qd = {'a':'a', 'b':'b','c':'c'}
        e = {}
        e['wsgi.input'] = StringIO(sq)
        e['wsgi.input'].seek(0)
        e['QUERY_STRING'] = sq
        request.bind(e)
        self.assertEqual(qd, request.GET)
        self.assertEqual(qd, request.POST)
        self.assertEqual(qd, request.params)

    def test_multigetpost(self):
        """ Environ: GET and POST (multi values) """ 
        sq = 'a=a&a=1'
        qd = {'a':['a','1']}
        e = {}
        e['wsgi.input'] = StringIO(sq)
        e['wsgi.input'].seek(0)
        e['QUERY_STRING'] = sq
        request.bind(e)
        self.assertEqual(qd, request.GET)
        self.assertEqual(qd, request.POST)
        self.assertEqual(qd, request.params)

    def test_multipart(self):
        """ Environ: POST (multipart files and multible values per key) """

        e = {}
        e['SERVER_PROTOCOL'] = "HTTP/1.1"
        e['REQUEST_METHOD'] = 'POST'
        e['CONTENT_TYPE'] = 'multipart/form-data; boundary=----------------314159265358979323846'
        e['wsgi.input']  = '------------------314159265358979323846\n'
        e['wsgi.input'] += 'Content-Disposition: form-data; name=test.txt; filename=test.txt\n'
        e['wsgi.input'] += 'Content-Type: application/octet-stream; charset=ISO-8859-1\n'
        e['wsgi.input'] += 'Content-Transfer-Encoding: binary\n'
        e['wsgi.input'] += 'This is a test.\n'
        e['wsgi.input'] += '------------------314159265358979323846\n'
        e['wsgi.input'] += 'Content-Disposition: form-data; name=sample.txt; filename=sample.txt\n'
        e['wsgi.input'] += 'Content-Type: text/plain; charset=ISO-8859-1\n'
        e['wsgi.input'] += 'Content-Transfer-Encoding: binary\n'
        e['wsgi.input'] += 'This is a sample\n'
        e['wsgi.input'] += '------------------314159265358979323846\n'
        e['wsgi.input'] += 'Content-Disposition: form-data; name=sample.txt; filename=sample2.txt\n'
        e['wsgi.input'] += 'Content-Type: text/plain; charset=ISO-8859-1\n'
        e['wsgi.input'] += 'Content-Transfer-Encoding: binary\n'
        e['wsgi.input'] += 'This is a second sample\n'
        e['wsgi.input'] += '------------------314159265358979323846--\n'
        e['CONTENT_LENGTH'] = len(e['wsgi.input'])
        e['wsgi.input'] = StringIO(e['wsgi.input'])
        e['wsgi.input'].seek(0)
        request.bind(e)
        self.assertTrue(e['CONTENT_LENGTH'], request.input_length)
        self.assertTrue('test.txt' in request.POST)
        self.assertTrue('sample.txt' in request.POST)
        self.assertEqual('This is a test.', request.POST['test.txt'].file.read())
        self.assertEqual('test.txt', request.POST['test.txt'].filename)
        self.assertEqual(2, len(request.POST['sample.txt']))
        self.assertEqual('This is a sample', request.POST['sample.txt'][0].file.read())
        self.assertEqual('This is a second sample', request.POST['sample.txt'][1].file.read())

 
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestEnviron))

if __name__ == '__main__':
    unittest.main()


