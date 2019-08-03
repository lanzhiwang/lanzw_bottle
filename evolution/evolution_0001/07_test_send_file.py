#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mimetypes
import os
from evolution_0001 import HTTPError, BreakTheBottle, response  # route, run, request, response, send_file, abort


def abort(code=500, text='Unknown Error: Appliction stopped.'):
    """ Aborts execution and causes a HTTP error. """
    raise HTTPError(code, text)


def send_file(filename, root, guessmime=True, mimetype='text/plain'):
    """ Aborts execution and sends a static files as response. """
    print 'root: {} filename: {}'.format(root, filename)
    root = os.path.abspath(root) + '/'
    filename = os.path.normpath(filename).strip('/')
    filename = os.path.join(root, filename)
    print 'root: {} filename: {}'.format(root, filename)
    """
    root: ./static/ filename: ling.png
    root: /root/work/lanzw_frame/evolution/evolution_0001/static/ 
    filename: /root/work/lanzw_frame/evolution/evolution_0001/static/ling.png
    """

    if not filename.startswith(root):
        abort(401, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        abort(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        abort(401, "You do not have permission to access this file.")

    if guessmime:
        print mimetypes.guess_type(filename)  # ('image/png', None)
        guess = mimetypes.guess_type(filename)[0]
        if guess:
            response.content_type = guess
        elif mimetype:
            response.content_type = mimetype
    elif mimetype:
        response.content_type = mimetype

    # TODO: Add Last-Modified header (Wed, 15 Nov 1995 04:58:08 GMT)
    raise BreakTheBottle(open(filename, 'r'))


if __name__ == '__main__':
    send_file('ling.png', root='./static/')
