# -*- coding: utf-8 -*-

import sys, os
test_root = os.path.dirname(os.path.abspath(__file__))  # /root/work/lanzw_frame/evolution/evolution_0016/test
os.chdir(test_root)
# print os.path.dirname(test_root)  # /root/work/lanzw_frame/evolution/evolution_0016
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

import unittest
from bottle import send_file, static_file, HTTPError, HTTPResponse, request, response, parse_date, Bottle
import wsgiref.util
import os
import os.path
import tempfile
import time

class TestDateParser(unittest.TestCase):
    def test_rfc1123(self):
        """DateParser: RFC 1123 format"""
        ts = time.time()
        rs = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(ts))
        # print 'test_rfc1123'
        # print 'ts: {}'.format(ts)
        # print 'rs: {}'.format(rs)
        # print 'int(ts): {}'.format(int(ts))
        # print 'parse_date(rs): {}'.format(parse_date(rs))
        # print 'int(parse_date(rs): {}'.format(int(parse_date(rs)))
        # print '-------------' * 10
        """
        test_rfc1123
        ts: 1566640952.49
        rs: Sat, 24 Aug 2019 10:02:32 GMT
        int(ts): 1566640952
        parse_date(rs): 1566640952.0
        int(parse_date(rs): 1566640952
        ----------------------------------------------------------------------------------------------------------------------------------
        """
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_rfc850(self):
        """DateParser: RFC 850 format"""
        ts = time.time()
        rs = time.strftime("%A, %d-%b-%y %H:%M:%S GMT", time.gmtime(ts))
        # print 'test_rfc850'
        # print 'ts: {}'.format(ts)
        # print 'rs: {}'.format(rs)
        # print 'int(ts): {}'.format(int(ts))
        # print 'parse_date(rs): {}'.format(parse_date(rs))
        # print 'int(parse_date(rs): {}'.format(int(parse_date(rs)))
        # print '-------------' * 10
        """
        test_rfc850
        ts: 1566640952.49
        rs: Saturday, 24-Aug-19 10:02:32 GMT
        int(ts): 1566640952
        parse_date(rs): 1566640952.0
        int(parse_date(rs): 1566640952
        ----------------------------------------------------------------------------------------------------------------------------------
        """
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_asctime(self):
        """DateParser: asctime format"""
        ts = time.time()
        rs = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime(ts))
        # print 'test_asctime'
        # print 'ts: {}'.format(ts)
        # print 'rs: {}'.format(rs)
        # print 'int(ts): {}'.format(int(ts))
        # print 'parse_date(rs): {}'.format(parse_date(rs))
        # print 'int(parse_date(rs): {}'.format(int(parse_date(rs)))
        # print '-------------' * 10
        """
        test_asctime
        ts: 1566640952.49
        rs: Sat Aug 24 10:02:32 2019
        int(ts): 1566640952
        parse_date(rs): 1566640952.0
        int(parse_date(rs): 1566640952
        ----------------------------------------------------------------------------------------------------------------------------------
        """
        self.assertEqual(int(ts), int(parse_date(rs)))

    def test_bad(self):
        """DateParser: Bad format"""
        self.assertEqual(None, parse_date('Bad 123'))


class TestSendFile(unittest.TestCase):
    def setUp(self):
        e = dict()
        wsgiref.util.setup_testing_defaults(e)
        b = Bottle()
        request.bind(e)
        response.bind()

    def test_valid(self):
        """ SendFile: Valid requests"""
        # print os.path.basename(__file__)  # test_sendfile.py
        out = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(open(__file__,'rb').read(), out.output.read())

    def test_invalid(self):
        """ SendFile: Invalid requests"""
        self.assertEqual(404, static_file('not/a/file', root='./').status)
        # print os.path.join('./../', os.path.basename(__file__))  # ./../test_sendfile.py
        f = static_file(os.path.join('./../', os.path.basename(__file__)), root='./views/')
        self.assertEqual(403, f.status)
        try:
            fp, fn = tempfile.mkstemp()
            os.chmod(fn, 0)
            self.assertEqual(403, static_file(fn, root='/').status)
        finally:
            os.close(fp)
            os.unlink(fn)
            
    def test_mime(self):
        """ SendFile: Mime Guessing"""
        # print os.path.basename(__file__)  # test_sendfile.py
        f = static_file(os.path.basename(__file__), root='./')
        self.assertTrue(f.headers['Content-Type'] in ('application/x-python-code', 'text/x-python'))

        f = static_file(os.path.basename(__file__), root='./', mimetype='some/type')
        self.assertEqual('some/type', f.headers['Content-Type'])

        f = static_file(os.path.basename(__file__), root='./', guessmime=False)
        self.assertEqual('text/plain', f.headers['Content-Type'])

    def test_ims(self):
        """ SendFile: If-Modified-Since"""
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        res = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(304, res.status)
        self.assertEqual(int(os.stat(__file__).st_mtime), parse_date(res.headers['Last-Modified']))
        self.assertAlmostEqual(int(time.time()), parse_date(res.headers['Date']))
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        self.assertEqual(open(__file__,'rb').read(), static_file(os.path.basename(__file__), root='./').output.read())

    def test_download(self):
        """ SendFile: Download as attachment """
        # print os.path.basename(__file__)  # test_sendfile.py
        basename = os.path.basename(__file__)
        f = static_file(basename, root='./', download=True)
        self.assertEqual('attachment; filename="%s"' % basename, f.headers['Content-Disposition'])
        request.environ['HTTP_IF_MODIFIED_SINCE'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(100))
        f = static_file(os.path.basename(__file__), root='./')
        self.assertEqual(open(__file__,'rb').read(), f.output.read())


if __name__ == '__main__': #pragma: no cover
    unittest.main()

