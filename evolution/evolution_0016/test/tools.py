# -*- coding: utf-8 -*-

import sys, os
test_root = os.path.dirname(os.path.abspath(__file__))  # /root/work/lanzw_frame/evolution/evolution_0016/test
os.chdir(test_root)
# print os.path.dirname(test_root)  # /root/work/lanzw_frame/evolution/evolution_0016
sys.path.insert(0, os.path.dirname(test_root))
sys.path.insert(0, test_root)


import bottle
import threading
import urllib
import urllib2
import sys
import time
import unittest
import wsgiref
import wsgiref.simple_server
import wsgiref.util
import wsgiref.validate

from StringIO import StringIO
try:
    from io import BytesIO
except:
    BytesIO = None
    pass
import mimetypes
import uuid

# tob('b=b&c=p')
# tob('foobar')
def tob(data):
    ''' Transforms bytes or unicode into bytes. '''
    if isinstance(data, unicode):
        return data.encode('utf8')
    else:
        return data
    # return data.encode('utf8') if isinstance(data, unicode) else data


# tobs('test')
def tobs(data):
    ''' Transforms bytes or unicode into a byte stream. '''
    if BytesIO:
        return BytesIO(tob(data))
    else:
        return StringIO(tob(data))
    # return BytesIO(tob(data)) if BytesIO else StringIO(tob(data))


class ServerTestBase(unittest.TestCase):
    def setUp(self):
        ''' Create a new Bottle app set it as default_app and register it to urllib2 '''
        self.port = 8080
        self.host = 'localhost'
        self.app = bottle.app.push()
        self.wsgiapp = wsgiref.validate.validator(self.app)
        # print 'self.wsgiapp: {}'.format(self.wsgiapp)  # <function lint_app at 0x7fa97b2a8668>

    # urlopen('/cookie')
    # urlopen(route, **kargs)
    def urlopen(self, path, method='GET', post='', env=None):
        result = {'code':0, 'status':'error', 'header':{}, 'body':tob('')}
        def start_response(status, header):
            result['code'] = int(status.split()[0])
            result['status'] = status.split(None, 1)[-1]
            for name, value in header:
                name = name.title()
                if name in result['header']:
                    result['header'][name] += ', ' + value
                else:
                    result['header'][name] = value
        env = env if env else {}
        wsgiref.util.setup_testing_defaults(env)
        env['REQUEST_METHOD'] = method.upper().strip()
        env['PATH_INFO'] = path
        env['QUERY_STRING'] = ''
        if post:
            env['REQUEST_METHOD'] = 'POST'
            env['CONTENT_LENGTH'] = str(len(tob(post)))
            env['wsgi.input'].write(tob(post))
            env['wsgi.input'].seek(0)
        response = self.wsgiapp(env, start_response)
        for part in response:
            try:
                result['body'] += part
            except TypeError:
                raise TypeError('WSGI app yielded non-byte object %s', type(part))
        if hasattr(response, 'close'):
            response.close()
            del response
        return result
        
    def postmultipart(self, path, fields, files):
        env = multipart_environ(fields, files)
        return self.urlopen(path, method='POST', env=env)

    def tearDown(self):
        bottle.app.pop()

    def assertStatus(self, code, route='/', **kargs):
        self.assertEqual(code, self.urlopen(route, **kargs)['code'])

    def assertBody(self, body, route='/', **kargs):
        self.assertEqual(tob(body), self.urlopen(route, **kargs)['body'])

    def assertInBody(self, body, route='/', **kargs):
        result = self.urlopen(route, **kargs)['body']
        if tob(body) not in result:
            self.fail('The search pattern "%s" is not included in body:\n%s' % (body, result))

    def assertHeader(self, name, value, route='/', **kargs):
        self.assertEqual(value, self.urlopen(route, **kargs)['header'].get(name))

    def assertHeaderAny(self, name, route='/', **kargs):
        self.assertTrue(self.urlopen(route, **kargs)['header'].get(name, None))

    def assertInError(self, search, route='/', **kargs):
        bottle.request.environ['wsgi.errors'].errors.seek(0)
        err = bottle.request.environ['wsgi.errors'].errors.read()
        if search not in err:
            self.fail('The search pattern "%s" is not included in wsgi.error: %s' % (search, err))


def multipart_environ(fields, files):
    boundary = str(uuid.uuid1())
    # print 'boundary: {}'.format(boundary)  # boundary: 8a836306-c65e-11e9-aa5e-0050569b350e

    env = {'REQUEST_METHOD':'POST',
           'CONTENT_TYPE':  'multipart/form-data; boundary='+boundary}
    wsgiref.util.setup_testing_defaults(env)
    # print 'env: {}'.format(env)
    """
    {
    'wsgi.multiprocess': 0, 
    'wsgi.version': (1, 0), 
    'SERVER_PORT': '80', 
    'SERVER_NAME': '127.0.0.1', 
    'wsgi.run_once': 0, 
    'wsgi.errors': <StringIO.StringIO instance at 0xf8ca28>, 
    'wsgi.multithread': 0, 
    'SCRIPT_NAME': '', 
    'wsgi.url_scheme': 'http', 
    'wsgi.input': <StringIO.StringIO instance at 0xf8c9e0>, 
    'REQUEST_METHOD': 'POST', 
    'HTTP_HOST': '127.0.0.1', 
    'PATH_INFO': '/', 
    'CONTENT_TYPE': 'multipart/form-data; boundary=8a836306-c65e-11e9-aa5e-0050569b350e', 
    'SERVER_PROTOCOL': 'HTTP/1.0'
    }
    """

    boundary = '--' + boundary
    body = ''

    # fields = [('field1', 'value1'), ('field2', 'value2'), ('field2', 'value3')]
    for name, value in fields:
        body += boundary + '\n'
        body += 'Content-Disposition: form-data; name="%s"\n\n' % name
        body += value + '\n'

    # files = [('file1', 'filename1.txt', 'content1'), ('file2', 'filename2.py', u'ä\nö\rü')]
    for name, filename, content in files:
        mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        body += boundary + '\n'
        body += 'Content-Disposition: file; name="%s"; filename="%s"\n' % \
             (name, filename)
        body += 'Content-Type: %s\n\n' % mimetype
        body += content + '\n'
    body += boundary + '--\n'
    if hasattr(body, 'encode'):
        body = body.encode('utf8')

    print 'body: {}'.format(body)
    """
    --3de250f6-c65f-11e9-8b6b-0050569b350e
    Content-Disposition: form-data; name="field1"
    
    value1
    --3de250f6-c65f-11e9-8b6b-0050569b350e
    Content-Disposition: form-data; name="field2"
    
    value2
    --3de250f6-c65f-11e9-8b6b-0050569b350e
    Content-Disposition: form-data; name="field2"
    
    value3
    --3de250f6-c65f-11e9-8b6b-0050569b350e
    Content-Disposition: file; name="file1"; filename="filename1.txt"
    Content-Type: text/plain
    
    content1
    --3de250f6-c65f-11e9-8b6b-0050569b350e
    Content-Disposition: file; name="file2"; filename="filename2.py"
    Content-Type: text/x-python
    
    ä
    ü
    --3de250f6-c65f-11e9-8b6b-0050569b350e--

    """
    env['CONTENT_LENGTH'] = str(len(body))
    env['wsgi.input'].write(body)
    env['wsgi.input'].seek(0)
    return env



if __name__ == '__main__':
    fields = [('field1', 'value1'), ('field2', 'value2'), ('field2', 'value3')]
    files = [('file1', 'filename1.txt', 'content1'), ('file2', 'filename2.py', u'ä\nö\rü')]
    e = multipart_environ(fields=fields, files=files)
    print e
    """
    {
    'CONTENT_LENGTH': '602', 
    'wsgi.multiprocess': 0, 
    'wsgi.version': (1, 0), 
    'SERVER_PORT': '80', 
    'SERVER_NAME': '127.0.0.1', 
    'wsgi.run_once': 0, 
    'wsgi.errors': <StringIO.StringIO instance at 0x1fe7a28>, 
    'wsgi.multithread': 0, 
    'SCRIPT_NAME': '', 
    'wsgi.url_scheme': 'http', 
    'wsgi.input': <StringIO.StringIO instance at 0x1fe79e0>, 
    'REQUEST_METHOD': 'POST', 
    'HTTP_HOST': '127.0.0.1', 
    'PATH_INFO': '/', 
    'CONTENT_TYPE': 'multipart/form-data; boundary=3de250f6-c65f-11e9-8b6b-0050569b350e', 
    'SERVER_PROTOCOL': 'HTTP/1.0'
    }
    """