#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Bottle(object):
    pass


class AppStack(list):
    """ A stack-like list. Calling it returns the head of the stack. """

    def __call__(self):
        """ Return the current default application. """
        return self[-1]

    def push(self, value=None):
        """ Add a new :class:`Bottle` instance to the stack """
        if not isinstance(value, Bottle):
            value = Bottle()
        self.append(value)
        return value

app = default_app = AppStack()
app.push()

"""
##################################

from bottle import route, run

@route('/hello')
def hello():
    return "Hello World!"

run(host='localhost', port=8080, debug=True)

##################################

from bottle import Bottle, run

app = Bottle()

@app.route('/hello')
def hello():
    return "Hello World!"

run(app, host='localhost', port=8080)


##################################

default_app.push()

@route('/')
def hello():
    return 'Hello World'

app = default_app.pop()

##################################

default_app.push()

import some.module

app = default_app.pop()

##################################

##################################

##################################
"""
