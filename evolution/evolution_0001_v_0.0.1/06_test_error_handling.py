#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = False
ERROR_HANDLER = {}  # ERROR_HANDLER[code] = handler

def set_error_handler(code, handler):
    """ Sets a new error handler. """
    code = int(code)
    ERROR_HANDLER[code] = handler


def error(code=500):
    """ Decorator for error handler. Same as set_error_handler(code, handler)."""

    def wrapper(handler):
        set_error_handler(code, handler)
        return handler

    return wrapper

@error(500)
def error500(exception):
    """If an exception is thrown, deal with it and present an error page."""
    if DEBUG:
        return str(exception)
    else:
        return """<b>Error:</b> Internal server error."""


@error(404)
def error404(exception):
    """If an exception is thrown, deal with it and present an error page."""
    yield '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">'
    yield '<html><head><title>Error 404: Not found</title>'
    yield '</head><body><h1>Error 404: Not found</h1>'
    yield '<p>The requested URL %s was not found on this server.</p>' % request.path
    yield '</body></html>'

# errorhandler = ERROR_HANDLER.get(response.status, None)
# output = errorhandler(exception)
