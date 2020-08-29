# -*- coding: utf-8 -*-

from bottle import route, run, request, response, send_file, abort, validate

from bottle import DEBUG, OPTIMIZER, ROUTES_SIMPLE, ROUTES_REGEXP, ERROR_HANDLER

# print(DEBUG)  # False
# print(OPTIMIZER)  # False
# print(ROUTES_SIMPLE)  # {}
# print(ROUTES_REGEXP)  # {}
# print(ERROR_HANDLER)  # {400: <function error_http at 0x217e230>, 404: <function error_http at 0x217e230>, 500: <function error500 at 0x217e0c8>, 401: <function error_http at 0x217e230>}
# print(request)  # <bottle.Request object at 0x211b328>
# print(response)  # <bottle.Response object at 0x211b870>


# Lets start with "Hello World!"
# Point your Browser to 'http://localhost:8080/' and greet the world :D
@route('/')
def hello_world():
    return 'Hello World!'
"""
$ curl http://localhost:8080/
Hello World!
"""

# Receiving GET parameter (/hello?name=Tim) is as easy as using a dict.
@route('/hello')
def hello_get():
    name = request.GET['name']
    return 'Hello %s!' % name
"""
$ curl http://localhost:8080/hello?name=Tim
Hello Tim!
"""

# This example handles POST requests to '/hello_post'
@route('/hello_post', method='POST')
def hello_post():
    name = request.POST['name']
    return 'Hello %s!' % name
"""
$ curl -X POST -F "name=user" http://localhost:8080/hello_post
Hello user!
"""

# Cookies :D
@route('/counter')
def counter():
    old = request.COOKIES.get('counter',0)
    new = int(old) + 1
    response.COOKIES['counter'] = new
    return "You viewed this page %d times!" % new
"""
$ curl http://localhost:8080/counter
You viewed this page 1 times!
$ curl http://localhost:8080/counter
You viewed this page 1 times!
$ curl http://localhost:8080/counter
You viewed this page 1 times!


# 存储网站 Cookie
$ curl --cookie-jar testcookie.txt http://localhost:8080/counter
You viewed this page 1 times!
$ ll
总用量 8
-rw-r--r-- 1 root root  171 8月  29 14:36 testcookie.txt
drwxr-xr-x 3 root root 4096 7月  31 11:17 work

# 发送网站 Cookie
$ curl --cookie testcookie.txt http://localhost:8080/counter
You viewed this page 2 times!
"""

# URL-parameter are a useful tool and generate nice looking URLs
# This handles requests such as '/hello/Tim' or '/hello/Jane'
@route('/hello/:name')
def hello_url(name):
    return 'hhhHello %s!' % name
"""
$ curl http://localhost:8080/hello/Tim
hhhHello Tim!
$ curl http://localhost:8080/hello/tom
hhhHello tom!
"""

# By default, an URL parameter matches everything up to the next slash.
# You can change that behaviour by adding a regular expression between two '#'
# in this example, :num will only match one or more digits.
# Requests to '/number/Tim' won't work (and result in a 404)
@route('/number/:num#[0-9]+#')
def hello_number(num):
    return "Your number is %d" % int(num)
"""
$ curl http://localhost:8080/number/6
Your number is 6
$ curl http://localhost:8080/number/tom
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 404: Not Found</title></head><body><h1>Error 404: Not Found</h1><p>Sorry, the requested URL /number/tom caused an error.</p>Not found</body></html>
"""

# How to send a static file to the Browser? Just name it.
# Bottle does the content-type guessing and save path checking for you.
@route('/static/:filename#.*#')
def static_file(filename):
    send_file(filename, root='/root/work/code/lanzw_bottle/evolution/evolution_02/')
"""
$ curl http://localhost:8080/static/README
Bottle Web Framework
====================

`Bottle` is a simple, fast and useful one-file WSGI-framework. It is not a
full-stack framework with a ton of features, but a useful mirco-framework for
small web-applications that stays out of your way.


$ curl http://localhost:8080/static/README -o README
$ ll
总用量 12
-rw-r--r-- 1 root root 3782 8月  29 14:47 README
-rw-r--r-- 1 root root  171 8月  29 14:39 testcookie.txt
drwxr-xr-x 3 root root 4096 7月  31 11:17 work
$ cat README
Bottle Web Framework
====================

`Bottle` is a simple, fast and useful one-file WSGI-framework. It is not a
full-stack framework with a ton of features, but a useful mirco-framework for
small web-applications that stays out of your way.

"""

# You can manually add header and set the content-type of the response.
@route('/json')
def json():
    response.header['Cache-Control'] = 'no-cache, must-revalidate'
    response.content_type = 'application/json'
    return "{counter:%d}" % int(request.COOKIES.get('counter',0))
"""
$ curl http://localhost:8080/json
{counter:0}
$ curl --cookie testcookie.txt http://localhost:8080/json
{counter:1}

$ curl --cookie testcookie.txt -v http://localhost:8080/json
* About to connect() to localhost port 8080 (#0)
*   Trying 127.0.0.1...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /json HTTP/1.1
> User-Agent: curl/7.29.0
> Host: localhost:8080
> Accept: */*
> Cookie: counter=1
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Date: Sat, 29 Aug 2020 06:54:45 GMT
< Server: WSGIServer/0.1 Python/2.7.5
< Content-Type: application/json
< Cache-Control: no-cache, must-revalidate
<
* Closing connection 0
{counter:1}
"""

# Throwing an error using abort()
@route('/private')
def private():
    if request.GET.get('password','') != 'secret':
        abort(401, 'Go away!')
    return "Welcome!"
"""
$ curl http://localhost:8080/private
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 401: Unauthorized</title></head><body><h1>Error 401: Unauthorized</h1><p>Sorry, the requested URL /private caused an error.</p>Go away!</body></html>

$ curl http://localhost:8080/private?password=secret
Welcome!

$ curl http://localhost:8080/private?password=error
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 401: Unauthorized</title></head><body><h1>Error 401: Unauthorized</h1><p>Sorry, the requested URL /private caused an error.</p>Go away!</body></html>
"""

# Validating URL Parameter
@route('/validate/:i/:f/:csv')
@validate(i=int, f=float, csv=lambda x: map(int, x.strip().split(',')))
def validate_test(i, f, csv):
    return "Int: %d, Float:%f, List:%s" % (i, f, repr(csv))
"""
$ curl "http://localhost:8080/validate/10/10.2/csv1,csv2"
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>Error 400: Bad Request</title></head><body><h1>Error 400: Bad Request</h1><p>Sorry, the requested URL /validate/10/10.2/csv1,csv2 caused an error.</p>Wrong parameter format for: csv</body></html>

$ curl "http://localhost:8080/validate/10/10.2/1,2"
Int: 10, Float:10.200000, List:[1, 2]
"""

# print(ROUTES_SIMPLE)
"""
{'POST': {'/hello_post': <function hello_post at 0x1122230>}, 'GET': {'/counter': <function counter at 0x1122320>, '/json': <function json at 0x1122500>, '/private': <function private at 0x1122578>, '/': <function hello_world at 0x11220c8>, '/hello': <function hello_get at 0x11221b8>}}
"""
# print(ROUTES_REGEXP)
"""
{'GET': [[<_sre.SRE_Pattern object at 0x1116200>, <function hello_url at 0x1122398>], [<_sre.SRE_Pattern object at 0x7fb2b3417d30>, <function hello_number at 0x1122410>], [<_sre.SRE_Pattern object at 0x11162e8>, <function static_file at 0x1122488>], [<_sre.SRE_Pattern object at 0xf80220>, <function wrapper at 0x1122758>]]}
"""

run(host='localhost', port=8080)
