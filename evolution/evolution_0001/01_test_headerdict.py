#!/usr/bin/env python
# -*- coding: utf-8 -*-


# from evolution_0001 import HeaderDict


class HeaderDict(dict):
    ''' A dictionary with case insensitive (titled) keys.

    You may add a list of strings to send multible headers with the same name.'''

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.title(), value)

    def __getitem__(self, key):
        return dict.__getitem__(self, key.title())

    def __delitem__(self, key):
        return dict.__delitem__(self, key.title())

    def __contains__(self, key):
        return dict.__contains__(self, key.title())

    def items(self):
        """ Returns a list of (key, value) tuples """
        for key, values in dict.items(self):
            if not isinstance(values, list):
                values = [values]
            for value in values:
                yield (key, str(value))

    def add(self, key, value):
        """ Adds a new header without deleting old ones """
        if isinstance(value, list):
            for v in value:
                self.add(key, v)
        elif key in self:
            if isinstance(self[key], list):
                self[key].append(value)
            else:
                self[key] = [self[key], value]
        else:
            self[key] = [value]


if __name__ == '__main__':
    hd = HeaderDict()
    hd['content-type'] = 'text/html'
    hd['accept'] = 'utf-8'
    hd['cache-control'] = ['max-age', 100]
    print hd
    """
    {
    'Content-Type': 'text/html', 
    'Accept': 'utf-8', 
    'Cache-Control': ['max-age', 100]
    }
    """

    for key, value in hd.items():
        print 'key: {} value: {}'.format(key, value)
        """
        key: Content-Type value: text/html
        key: Accept value: utf-8
        key: Cache-Control value: max-age
        key: Cache-Control value: 100
        """

    hd.add('Content-Length', 1000)
    hd.add('Accept-Language', ['big5', 'gb2312', 'gbk'])
    hd.add('accept', 'big5')
    print hd
    """
    {
    'Accept-Language': ['big5', 'gb2312', 'gbk'], 
    'Content-Length': [1000], 
    'Content-Type': 'text/html', 
    'Accept': ['utf-8', 'big5'], 
    'Cache-Control': ['max-age', 100]
    }
    """
