#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import sys


def tob(s, enc='utf8'):
    print 'isinstance(s, unicode): {}'.format(isinstance(s, unicode))
    if isinstance(s, unicode):
        return s.encode(enc)  # 编码
    else:
        return bytes(s)
    # return s.encode(enc) if isinstance(s, unicode) else bytes(s)


def touni(s, enc='utf8', err='strict'):
    print 'isinstance(s, bytes): {}'.format(isinstance(s, bytes))
    if isinstance(s, bytes):
        return s.decode(enc, err)
    else:
        return unicode(s)
    # return s.decode(enc, err) if isinstance(s, bytes) else unicode(s)


py = sys.version_info
py3k = py >= (3, 0, 0)
if py3k:
    tonat = touni
else:
    tonat = tob


if __name__ == '__main__':
    print tob('a=a&a=1&b=b&c=c&cn=%e7%93%b6')
    print tob(u'a=a&a=1&b=b&c=c&cn=%e7%93%b6')
    print tob('瓶')
    print tob('foobar')
    print tob('a=a&a=1&b=b&c=&d')
    print tob('b=b&c=p')
    print tob('ä\nö\rü')

    print '=========' * 10

    print touni(tob('a=a&a=1&b=b&c=c&cn=%e7%93%b6'))
    print touni(tob(u'a=a&a=1&b=b&c=c&cn=%e7%93%b6'))
    print touni('瓶')
    print touni('foobar')

    print base64.b64encode(tob('user:pwd'))
    print touni(base64.b64encode(tob('user:pwd')))

    """
    isinstance(s, unicode): False
    a=a&a=1&b=b&c=c&cn=%e7%93%b6
    isinstance(s, unicode): True
    a=a&a=1&b=b&c=c&cn=%e7%93%b6
    isinstance(s, unicode): False
    瓶
    isinstance(s, unicode): False
    foobar
    isinstance(s, unicode): False
    a=a&a=1&b=b&c=&d
    isinstance(s, unicode): False
    b=b&c=p
    isinstance(s, unicode): False
    ä
    ü
    ==========================================================================================
    isinstance(s, unicode): False
    isinstance(s, bytes): True
    a=a&a=1&b=b&c=c&cn=%e7%93%b6
    isinstance(s, unicode): True
    isinstance(s, bytes): True
    a=a&a=1&b=b&c=c&cn=%e7%93%b6
    isinstance(s, bytes): True
    瓶
    isinstance(s, bytes): True
    foobar
    
    isinstance(s, unicode): False
    dXNlcjpwd2Q=
    isinstance(s, unicode): False
    isinstance(s, bytes): True
    dXNlcjpwd2Q=
    """