Bottle Web Framework
====================

.. image:: http://bottlepy.org/bottle-logo.png
  :alt: Bottle Logo
  :align: right

Bottle is a fast and simple micro-framework for small web applications. It
offers request dispatching (URL routing) with URL parameter support, templates,
a built-in HTTP Server and adapters for many third party WSGI/HTTP-server and
template engines - all in a single file and with no dependencies other than the
Python Standard Library.

Homepage and documentation: http://bottlepy.org/
License: MIT (see LICENSE.txt)

Installation and Dependencies
-----------------------------

Install bottle with ``pip install bottle`` or just `download bottle.py <http://pypi.python.org/pypi/bottle>`_ and place it in your project directory. There are no (hard) dependencies other than the Python Standard Library.


Example
-------

::

    from bottle import route, run

    @route('/hello/:name')
    def hello(name):
        return '<h1>Hello %s!</h1>' % name.title()

    run(host='localhost', port=8080)

https://github.com/bottlepy/bottle/commits/master?before=357a0cb39cb8337f8467f5396e4b7caaa7e4f25c+490&path%5B%5D=bottle.py

https://github.com/bottlepy/bottle/commit/ba8ad1a95c103a530f9abfa871816fe9aff0a34c#diff-ad8cb2f640fd3a70db3fc97f3044a4e6
