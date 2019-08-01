#!/usr/local/bin/python

from evolution_0001 import HeaderDict

hd = HeaderDict()
hd['Content-Type'] = 'text/html'
hd['qwe'] = 'qwe'
hd['qwe'] = 'asd'
hd['rty'] = ['fgh', 'vbn']
print hd

"""
    {
    'Rty': ['fgh', 'vbn'], 
    'Qwe': 'asd', 
    'Content-Type': 'text/html'
    }
"""

hd.add('addkey1', ['123', '456'])
hd.add('qwe', ['123', '456'])
print hd

"""
    {
    'Rty': ['fgh', 'vbn'], 
    'Qwe': ['asd', '123', '456'], 
    'Addkey1': ['123', '456'], 
    'Content-Type': 'text/html'
    }
"""

