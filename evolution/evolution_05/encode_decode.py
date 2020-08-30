# -*- coding: utf-8 -*-

import sys


if sys.version_info >= (3,0,0): # pragma: no cover
    # def touni(x, enc='utf8'): # Convert anything to unicode (py3)
    #     print('py3: %s' % isinstance(x, bytes))
    #     return str(x, encoding=enc) if isinstance(x, bytes) else str(x)
    unicode = str
else:
    # def touni(x, enc='utf8'): # Convert anything to unicode (py2)
    #     print('py2: %s ' % isinstance(x, unicode))
    #     return x if isinstance(x, unicode) else unicode(str(x), encoding=enc)
    unicode = unicode

# def tob(data, enc='utf8'): # Convert strings to bytes (py2 and py3)
#     return data.encode(enc) if isinstance(data, unicode) else data


def touni(s, enc='utf8', err='strict'):
    print('isinstance(s, bytes): %s' % isinstance(s, bytes))
    if isinstance(s, bytes):
        return s.decode(enc, err)
    return unicode("" if s is None else s)
"""
unicode = unicode
py2
foobar b'foobar' -> bytes  字节码 -解码-> unicode
u'foobar' -> uncode        unicode 强制类型转换成 unicode

unicode = str
py3
b'foobar' -> bytes          字节码 -解码-> unicode
foobar u'foobar' -> uncode  str 强制类型转换成 unicode
"""


for anything in [
    'foobar', u'foobar', b'foobar', '瓶', '万难', 'äöü', 'ümläüts$', '', 'öäüß', '*',
    '{% if var is even %}gerade{% else %}ungerade{% endif %}',
    'start middle end', 'υηι¢σ∂є', 'Unicode äöüß message.' 'a=a&a=1&b=b&c=c&cn=%e7%93%b6',
    'b=b&c=p', 'ä\nö\rü', 'urf8-öäü'
    ]:
    # print(anything)
    # print(touni(anything))
    # print('====================')
    pass

"""
$ python encode_decode.py
foobar
isinstance(s, bytes): True
foobar
====================
u'foobar'
isinstance(s, bytes): False
foobar
====================
b'foobar'
isinstance(s, bytes): True
foobar
====================
瓶
isinstance(s, bytes): True
瓶
====================
万难
isinstance(s, bytes): True
万难
====================
äöü
isinstance(s, bytes): True
äöü
====================
ümläüts$
isinstance(s, bytes): True
ümläüts$
====================

isinstance(s, bytes): True

====================
öäüß
isinstance(s, bytes): True
öäüß
====================
*
isinstance(s, bytes): True
*
====================
{% if var is even %}gerade{% else %}ungerade{% endif %}
isinstance(s, bytes): True
{% if var is even %}gerade{% else %}ungerade{% endif %}
====================
start middle end
isinstance(s, bytes): True
start middle end
====================
υηι¢σ∂є
isinstance(s, bytes): True
υηι¢σ∂є
====================
Unicode äöüß message.a=a&a=1&b=b&c=c&cn=%e7%93%b6
isinstance(s, bytes): True
Unicode äöüß message.a=a&a=1&b=b&c=c&cn=%e7%93%b6
====================
b=b&c=p
isinstance(s, bytes): True
b=b&c=p
====================
ä
ü
isinstance(s, bytes): True
ä
ü
====================
urf8-öäü
isinstance(s, bytes): True
urf8-öäü
====================
$

################################################################

$ python3 encode_decode.py
foobar
isinstance(s, bytes): False
foobar
====================
u'foobar'
isinstance(s, bytes): False
foobar
====================
b'foobar'
isinstance(s, bytes): True
foobar
====================
瓶
isinstance(s, bytes): False
瓶
====================
万难
isinstance(s, bytes): False
万难
====================
äöü
isinstance(s, bytes): False
äöü
====================
ümläüts$
isinstance(s, bytes): False
ümläüts$
====================

isinstance(s, bytes): False

====================
öäüß
isinstance(s, bytes): False
öäüß
====================
*
isinstance(s, bytes): False
*
====================
{% if var is even %}gerade{% else %}ungerade{% endif %}
isinstance(s, bytes): False
{% if var is even %}gerade{% else %}ungerade{% endif %}
====================
start middle end
isinstance(s, bytes): False
start middle end
====================
υηι¢σ∂є
isinstance(s, bytes): False
υηι¢σ∂є
====================
Unicode äöüß message.a=a&a=1&b=b&c=c&cn=%e7%93%b6
isinstance(s, bytes): False
Unicode äöüß message.a=a&a=1&b=b&c=c&cn=%e7%93%b6
====================
b=b&c=p
isinstance(s, bytes): False
b=b&c=p
====================
ä
ü
isinstance(s, bytes): False
ä
ü
====================
urf8-öäü
isinstance(s, bytes): False
urf8-öäü
====================
$
"""


def tob(s, enc='utf8'):
    print('isinstance(s, unicode): %s' % isinstance(s, unicode))
    if isinstance(s, unicode):
        return s.encode(enc)
    return b'' if s is None else bytes(s)
"""
unicode = unicode
py2
foobar b'foobar' -> bytes  bytes 强制类型转换成 字节码
u'foobar' -> uncode        unicode -编码-> 字节码

unicode = str
py3
b'foobar' -> bytes          bytes 强制类型转换成 字节码
foobar u'foobar' -> uncode  unicode -编码-> 字节码
"""

for anything in [
    'foobar', u'foobar', b'foobar', '瓶', '万难', 'äöü', 'ümläüts$', '', 'öäüß', '*',
    '{% if var is even %}gerade{% else %}ungerade{% endif %}',
    'start middle end', 'υηι¢σ∂є', 'Unicode äöüß message.' 'a=a&a=1&b=b&c=c&cn=%e7%93%b6',
    'b=b&c=p', 'ä\nö\rü', 'urf8-öäü'
    ]:
    print(anything)
    print(tob(anything))
    print('====================')


"""
$ python encode_decode.py
foobar
isinstance(s, unicode): False
foobar
====================
u'foobar'
isinstance(s, unicode): True
foobar
====================
b'foobar'
isinstance(s, unicode): False
foobar
====================
瓶
isinstance(s, unicode): False
瓶
====================
万难
isinstance(s, unicode): False
万难
====================
äöü
isinstance(s, unicode): False
äöü
====================
ümläüts$
isinstance(s, unicode): False
ümläüts$
====================

isinstance(s, unicode): False

====================
öäüß
isinstance(s, unicode): False
öäüß
====================
*
isinstance(s, unicode): False
*
====================
{% if var is even %}gerade{% else %}ungerade{% endif %}
isinstance(s, unicode): False
{% if var is even %}gerade{% else %}ungerade{% endif %}
====================
start middle end
isinstance(s, unicode): False
start middle end
====================
υηι¢σ∂є
isinstance(s, unicode): False
υηι¢σ∂є
====================
Unicode äöüß message.a=a&a=1&b=b&c=c&cn=%e7%93%b6
isinstance(s, unicode): False
Unicode äöüß message.a=a&a=1&b=b&c=c&cn=%e7%93%b6
====================
b=b&c=p
isinstance(s, unicode): False
b=b&c=p
====================
ä
ü
isinstance(s, unicode): False
ä
ü
====================
urf8-öäü
isinstance(s, unicode): False
urf8-öäü
====================
$

################################################################

$ python3 encode_decode.py
foobar
isinstance(s, unicode): True
b'foobar'
====================
foobar
isinstance(s, unicode): True
b'foobar'
====================
b'foobar'
isinstance(s, unicode): False
b'foobar'
====================
瓶
isinstance(s, unicode): True
b'\xe7\x93\xb6'
====================
万难
isinstance(s, unicode): True
b'\xe4\xb8\x87\xe9\x9a\xbe'
====================
äöü
isinstance(s, unicode): True
b'\xc3\xa4\xc3\xb6\xc3\xbc'
====================
ümläüts$
isinstance(s, unicode): True
b'\xc3\xbcml\xc3\xa4\xc3\xbcts$'
====================

isinstance(s, unicode): True
b''
====================
öäüß
isinstance(s, unicode): True
b'\xc3\xb6\xc3\xa4\xc3\xbc\xc3\x9f'
====================
*
isinstance(s, unicode): True
b'*'
====================
{% if var is even %}gerade{% else %}ungerade{% endif %}
isinstance(s, unicode): True
b'{% if var is even %}gerade{% else %}ungerade{% endif %}'
====================
start middle end
isinstance(s, unicode): True
b'start middle end'
====================
υηι¢σ∂є
isinstance(s, unicode): True
b'\xcf\x85\xce\xb7\xce\xb9\xc2\xa2\xcf\x83\xe2\x88\x82\xd1\x94'
====================
Unicode äöüß message.a=a&a=1&b=b&c=c&cn=%e7%93%b6
isinstance(s, unicode): True
b'Unicode \xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f message.a=a&a=1&b=b&c=c&cn=%e7%93%b6'
====================
b=b&c=p
isinstance(s, unicode): True
b'b=b&c=p'
====================
ä
ü
isinstance(s, unicode): True
b'\xc3\xa4\n\xc3\xb6\r\xc3\xbc'
====================
urf8-öäü
isinstance(s, unicode): True
b'urf8-\xc3\xb6\xc3\xa4\xc3\xbc'
====================
$


"""
