#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Exceptions and Events

class BottleException(Exception):
    """ A base class for exceptions used by bottle."""
    pass


class HTTPError(BottleException):
    """ A way to break the execution and instantly jump to an error handler. """

    """
    HTTPError(401, "Access denied.")
    HTTPError(404, "File does not exist.")
    HTTPError(401, "You do not have permission to access this file.")
    """
    def __init__(self, status, text):
        self.output = text
        self.http_status = int(status)

    def __str__(self):
        return self.output


class BreakTheBottle(BottleException):
    """ Not an exception, but a straight jump out of the controller code.

    Causes the WSGIHandler to instantly call start_response() and return the
    content of output """

    """
    BreakTheBottle(open(filename, 'r'))
    """
    def __init__(self, output):
        self.output = output
