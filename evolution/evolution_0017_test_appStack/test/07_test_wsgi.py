# -*- coding: utf-8 -*-

import sys, os
test_root = os.path.dirname(os.path.abspath(__file__))  # /root/work/lanzw_frame/evolution/evolution_0016/test
os.chdir(test_root)
# print os.path.dirname(test_root)  # /root/work/lanzw_frame/evolution/evolution_0016
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)

import unittest
import sys, os.path

print '================ begin import'
import bottle
import urllib2
from StringIO import StringIO
import thread
import time
from tools import ServerTestBase
from bottle import tob, touni, tonat

class TestWsgi(ServerTestBase):
    ''' Tests for WSGI functionality, routing and output casting (decorators) '''

    def test_get(self):
        """ WSGI: GET routes"""
        print '================ test_get'
        @bottle.route('/')
        def test(): return 'test'
        self.assertStatus(404, '/not/found')
        self.assertStatus(405, '/', post="var=value")
        self.assertBody('test', '/')


if __name__ == '__main__': #pragma: no cover
    unittest.main()
