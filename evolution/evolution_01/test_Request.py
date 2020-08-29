# -*- coding: utf-8 -*-

import os
import sys
import unittest
import wsgiref
import wsgiref.util
import wsgiref.validate

import mimetypes
import uuid

py = sys.version_info
# print(py)  # sys.version_info(major=2, minor=7, micro=5, releaselevel='final', serial=0)
py3k = py.major > 2

if py3k:
    unicode = str
else:  # 2.x
    unicode = unicode




def multipart_environ(fields, files):
    boundary = str(uuid.uuid1())
    env = {'REQUEST_METHOD':'POST',
           'CONTENT_TYPE':  'multipart/form-data; boundary='+boundary}
    # print(env)
    """
    {
        'REQUEST_METHOD': 'POST',
        'CONTENT_TYPE': 'multipart/form-data; boundary=a5e7b316-e928-11ea-8be3-00163e157c3e'
    }
    """
    wsgiref.util.setup_testing_defaults(env)
    # print(env)
    """
    {
        'wsgi.multiprocess': 0,
        'wsgi.version': (1, 0),
        'SERVER_PORT': '80',
        'SERVER_NAME': '127.0.0.1',
        'wsgi.run_once': 0,
        'wsgi.errors': <StringIO.StringIO instance at 0x21a63b0>,
        'wsgi.multithread': 0,
        'SCRIPT_NAME': '',
        'wsgi.url_scheme': 'http',
        'wsgi.input': <StringIO.StringIO instance at 0x21a6f38>,
        'REQUEST_METHOD': 'POST',
        'HTTP_HOST': '127.0.0.1',
        'PATH_INFO': '/',
        'CONTENT_TYPE': 'multipart/form-data; boundary=a5e7b316-e928-11ea-8be3-00163e157c3e',
        'SERVER_PROTOCOL': 'HTTP/1.0'
    }
    """
    boundary = '--' + boundary
    body = ''
    for name, value in fields:
        # print(name, value)
        body += boundary + '\n'
        body += 'Content-Disposition: form-data; name="%s"\n\n' % name
        body += value + '\n'
    # print(body)
    """
    ('field1', 'value1')
    ('field2', 'value2')
    ('field2', '\xe4\xb8\x87\xe9\x9a\xbe')
    --33adf552-e929-11ea-8ffa-00163e157c3e
    Content-Disposition: form-data; name="field1"

    value1
    --33adf552-e929-11ea-8ffa-00163e157c3e
    Content-Disposition: form-data; name="field2"

    value2
    --33adf552-e929-11ea-8ffa-00163e157c3e
    Content-Disposition: form-data; name="field2"

    万难

    """

    for name, filename, content in files:
        # print(name, filename, content)
        # print(mimetypes.guess_type(filename))
        mimetype = str(mimetypes.guess_type(filename)[0]) or 'application/octet-stream'
        body += boundary + '\n'
        body += 'Content-Disposition: file; name="%s"; filename="%s"\n' % \
             (name, filename)
        body += 'Content-Type: %s\n\n' % mimetype
        body += content + '\n'
    # print(body)
    """
    ('file1', 'filename1.txt', 'content1')
    ('text/plain', None)
    ('\xe4\xb8\x87\xe9\x9a\xbe', '\xe4\xb8\x87\xe9\x9a\xbefoo.py', '\xc3\xa4\n\xc3\xb6\r\xc3\xbc')
    ('text/x-python', None)
    --a0e895c8-e929-11ea-9684-00163e157c3e
    Content-Disposition: form-data; name="field1"

    value1
    --a0e895c8-e929-11ea-9684-00163e157c3e
    Content-Disposition: form-data; name="field2"

    value2
    --a0e895c8-e929-11ea-9684-00163e157c3e
    Content-Disposition: form-data; name="field2"

    万难
    --a0e895c8-e929-11ea-9684-00163e157c3e
    Content-Disposition: file; name="file1"; filename="filename1.txt"
    Content-Type: text/plain

    content1
    --a0e895c8-e929-11ea-9684-00163e157c3e
    Content-Disposition: file; name="万难"; filename="万难foo.py"
    Content-Type: text/x-python

    ä
    ü

    """
    body += boundary + '--\n'
    # print(body)
    """
    --2349fd7c-e92a-11ea-bfe8-00163e157c3e
    Content-Disposition: form-data; name="field1"

    value1
    --2349fd7c-e92a-11ea-bfe8-00163e157c3e
    Content-Disposition: form-data; name="field2"

    value2
    --2349fd7c-e92a-11ea-bfe8-00163e157c3e
    Content-Disposition: form-data; name="field2"

    万难
    --2349fd7c-e92a-11ea-bfe8-00163e157c3e
    Content-Disposition: file; name="file1"; filename="filename1.txt"
    Content-Type: text/plain

    content1
    --2349fd7c-e92a-11ea-bfe8-00163e157c3e
    Content-Disposition: file; name="万难"; filename="万难foo.py"
    Content-Type: text/x-python

    ä
    ü
    --2349fd7c-e92a-11ea-bfe8-00163e157c3e--

    """
    if isinstance(body, unicode):
        body = body.encode('utf8')
    env['CONTENT_LENGTH'] = str(len(body))
    env['wsgi.input'].write(body)
    env['wsgi.input'].seek(0)
    return env

fields = [('field1','value1'), ('field2','value2'), ('field2','万难')]
files = [('file1','filename1.txt','content1'), ('万难','万难foo.py', 'ä\nö\rü')]
e = multipart_environ(fields=fields, files=files)


