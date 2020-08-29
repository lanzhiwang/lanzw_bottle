# -*- coding: utf-8 -*-
import sys
import os
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
if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import StringIO
import cgi

def post(env):
    print(env)
    POST = {}
    data = cgi.FieldStorage(fp=env['wsgi.input'], environ=env, keep_blank_values=True)
    print(data)
    print(data.list)
    for item in data.list:
        print(item, item.name, item.filename)
        name = item.name
        if not item.filename:
            item = item.value
        POST.setdefault(name, []).append(item)
    print(POST)
    for key in POST:
        if len(POST[key]) == 1:
            POST[key] = POST[key][0]
    print(POST)
    return POST

sq = 'a=a&b=b&c=c'
e = {}
e['wsgi.input'] = StringIO(sq)
e['wsgi.input'].seek(0)
e['QUERY_STRING'] = sq
print(e)  # {'QUERY_STRING': 'a=a&b=b&c=c', 'wsgi.input': <StringIO.StringIO instance at 0x7f500f1b3830>}

post(e)
"""
{'QUERY_STRING': 'a=a&b=b&c=c', 'wsgi.input': <StringIO.StringIO instance at 0x1e8dd88>}
FieldStorage(None, None, [MiniFieldStorage('a', 'a'), MiniFieldStorage('b', 'b'), MiniFieldStorage('c', 'c')])
[MiniFieldStorage('a', 'a'), MiniFieldStorage('b', 'b'), MiniFieldStorage('c', 'c')]
(MiniFieldStorage('a', 'a'), 'a', None)
(MiniFieldStorage('b', 'b'), 'b', None)
(MiniFieldStorage('c', 'c'), 'c', None)
{'a': ['a'], 'c': ['c'], 'b': ['b']}
{'a': 'a', 'c': 'c', 'b': 'b'}
"""


print()

sq = 'a=a&a=1'
e = {}
e['wsgi.input'] = StringIO(sq)
e['wsgi.input'].seek(0)
e['QUERY_STRING'] = sq
print(e)  # {'QUERY_STRING': 'a=a&a=1', 'wsgi.input': <StringIO.StringIO instance at 0x7fefdf9119e0>}

post(e)
"""
{'QUERY_STRING': 'a=a&a=1', 'wsgi.input': <StringIO.StringIO instance at 0x7fefdf9119e0>}
FieldStorage(None, None, [MiniFieldStorage('a', 'a'), MiniFieldStorage('a', '1')])
[MiniFieldStorage('a', 'a'), MiniFieldStorage('a', '1')]
(MiniFieldStorage('a', 'a'), 'a', None)
(MiniFieldStorage('a', '1'), 'a', None)
{'a': ['a', '1']}
{'a': ['a', '1']}
"""

print()

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
print(e)
"""
{
    'CONTENT_LENGTH': 674,
    'wsgi.input': <StringIO.StringIO instance at 0x7f1ac002bab8>,
    'REQUEST_METHOD': 'POST',
    'CONTENT_TYPE': 'multipart/form-data; boundary=----------------314159265358979323846',
    'SERVER_PROTOCOL': 'HTTP/1.1'
}
"""

post(e)
"""
{'CONTENT_LENGTH': 674, 'wsgi.input': <StringIO.StringIO instance at 0x7f1ac002bab8>, 'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': 'multipart/form-data; boundary=----------------314159265358979323846', 'SERVER_PROTOCOL': 'HTTP/1.1'}
FieldStorage(
    None,
    None,
    [
        FieldStorage('test.txt', 'test.txt', 'This is a test.'),
        FieldStorage('sample.txt', 'sample.txt', 'This is a sample'),
        FieldStorage('sample.txt', 'sample2.txt', 'This is a second sample')
    ]
)

[
    FieldStorage('test.txt', 'test.txt', 'This is a test.'),
    FieldStorage('sample.txt', 'sample.txt', 'This is a sample'),
    FieldStorage('sample.txt', 'sample2.txt', 'This is a second sample')
]

(FieldStorage('test.txt', 'test.txt', 'This is a test.'), 'test.txt', 'test.txt')
(FieldStorage('sample.txt', 'sample.txt', 'This is a sample'), 'sample.txt', 'sample.txt')
(FieldStorage('sample.txt', 'sample2.txt', 'This is a second sample'), 'sample.txt', 'sample2.txt')
{
    'sample.txt': [
        FieldStorage('sample.txt', 'sample.txt', 'This is a sample'),
        FieldStorage('sample.txt', 'sample2.txt', 'This is a second sample')
    ],
    'test.txt': [FieldStorage('test.txt', 'test.txt', 'This is a test.')]
}
{
    'sample.txt': [
        FieldStorage('sample.txt', 'sample.txt', 'This is a sample'),
        FieldStorage('sample.txt', 'sample2.txt', 'This is a second sample')
    ],
    'test.txt': FieldStorage('test.txt', 'test.txt', 'This is a test.')}
"""
self.assertTrue(e['CONTENT_LENGTH'], request.input_length)
self.assertTrue('test.txt' in request.POST)
self.assertTrue('sample.txt' in request.POST)
self.assertEqual('This is a test.', request.POST['test.txt'].file.read())
self.assertEqual('test.txt', request.POST['test.txt'].filename)
self.assertEqual(2, len(request.POST['sample.txt']))
self.assertEqual('This is a sample', request.POST['sample.txt'][0].file.read())
self.assertEqual('This is a second sample', request.POST['sample.txt'][1].file.read())



print()

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
print(e)
"""
{
    'CONTENT_LENGTH': '603',
    'wsgi.multiprocess': 0,
    'wsgi.version': (1, 0),
    'SERVER_PORT': '80',
    'SERVER_NAME': '127.0.0.1',
    'wsgi.run_once': 0,
    'wsgi.errors': <StringIO.StringIO instance at 0xf9b4d0>,
    'wsgi.multithread': 0,
    'SCRIPT_NAME': '',
    'wsgi.url_scheme': 'http',
    'wsgi.input': <StringIO.StringIO instance at 0xf9bb48>,
    'REQUEST_METHOD': 'POST',
    'HTTP_HOST': '127.0.0.1',
    'PATH_INFO': '/',
    'CONTENT_TYPE': 'multipart/form-data; boundary=c7562332-ea01-11ea-b1c4-00163e157c3e',
    'SERVER_PROTOCOL': 'HTTP/1.0'
}
"""

post(e)
"""
{'CONTENT_LENGTH': '603', 'wsgi.multiprocess': 0, 'wsgi.version': (1, 0), 'SERVER_PORT': '80', 'SERVER_NAME': '127.0.0.1', 'wsgi.run_once': 0, 'wsgi.errors': <StringIO.StringIO instance at 0x11f04d0>, 'wsgi.multithread': 0, 'SCRIPT_NAME': '', 'wsgi.url_scheme': 'http', 'wsgi.input': <StringIO.StringIO instance at 0x11f0b48>, 'REQUEST_METHOD': 'POST', 'HTTP_HOST': '127.0.0.1', 'PATH_INFO': '/', 'CONTENT_TYPE': 'multipart/form-data; boundary=171722ea-ea02-11ea-99fc-00163e157c3e', 'SERVER_PROTOCOL': 'HTTP/1.0'}
FieldStorage(
    None,
    None,
    [
        FieldStorage('field1', None, 'value1'),
        FieldStorage('field2', None, 'value2'),
        FieldStorage('field2', None, '\xe4\xb8\x87\xe9\x9a\xbe'),
        FieldStorage('file1', 'filename1.txt', 'content1'),
        FieldStorage('\xe4\xb8\x87\xe9\x9a\xbe', '\xe4\xb8\x87\xe9\x9a\xbefoo.py', '\xc3\xa4\n\xc3\xb6\r\xc3\xbc')
    ]
)

[
    FieldStorage('field1', None, 'value1'),
    FieldStorage('field2', None, 'value2'),
    FieldStorage('field2', None, '\xe4\xb8\x87\xe9\x9a\xbe'),
    FieldStorage('file1', 'filename1.txt', 'content1'),
    FieldStorage('\xe4\xb8\x87\xe9\x9a\xbe', '\xe4\xb8\x87\xe9\x9a\xbefoo.py', '\xc3\xa4\n\xc3\xb6\r\xc3\xbc')
]

(FieldStorage('field1', None, 'value1'), 'field1', None)
(FieldStorage('field2', None, 'value2'), 'field2', None)
(FieldStorage('field2', None, '\xe4\xb8\x87\xe9\x9a\xbe'), 'field2', None)
(FieldStorage('file1', 'filename1.txt', 'content1'), 'file1', 'filename1.txt')
(FieldStorage('\xe4\xb8\x87\xe9\x9a\xbe', '\xe4\xb8\x87\xe9\x9a\xbefoo.py', '\xc3\xa4\n\xc3\xb6\r\xc3\xbc'), '\xe4\xb8\x87\xe9\x9a\xbe', '\xe4\xb8\x87\xe9\x9a\xbefoo.py')

{
    'field2': ['value2', '\xe4\xb8\x87\xe9\x9a\xbe'],
    'file1': [FieldStorage('file1', 'filename1.txt', 'content1')],
    'field1': ['value1'],
    '\xe4\xb8\x87\xe9\x9a\xbe': [FieldStorage('\xe4\xb8\x87\xe9\x9a\xbe', '\xe4\xb8\x87\xe9\x9a\xbefoo.py', '\xc3\xa4\n\xc3\xb6\r\xc3\xbc')]
}

{
    'field2': ['value2', '\xe4\xb8\x87\xe9\x9a\xbe'],
    'file1': FieldStorage('file1', 'filename1.txt', 'content1'),
    'field1': 'value1',
    '\xe4\xb8\x87\xe9\x9a\xbe': FieldStorage('\xe4\xb8\x87\xe9\x9a\xbe', '\xe4\xb8\x87\xe9\x9a\xbefoo.py', '\xc3\xa4\n\xc3\xb6\r\xc3\xbc')
}
"""
