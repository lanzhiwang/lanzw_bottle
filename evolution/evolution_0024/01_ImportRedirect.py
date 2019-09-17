import imp, sys

class _ImportRedirect(object):
    def __init__(self, name, impmask):
        print 'name: {}'.format(name)  # name: bottle.ext
        print 'impmask: {}'.format(impmask)  # impmask: bottle_%s

        self.name = name  # bottle.ext
        self.impmask = impmask  # bottle_%s
        self.module = sys.modules.setdefault(name, imp.new_module(name))
        self.module.__dict__.update({'__file__': __file__, '__path__': [],
                                    '__all__': [], '__loader__': self})
        sys.meta_path.append(self)

    def find_module(self, fullname, path=None):
        print 'find_module fullname: {}'.format(fullname)  # find_module fullname: bottle.ext.sqlite

        print '. not in fullname: {}'.format('.' not in fullname)  # False
        if '.' not in fullname:
            return

        packname, modname = fullname.rsplit('.', 1)
        print 'find_module packname: {}'.format(packname)  # find_module packname: bottle.ext
        print 'find_module modname: {}'.format(modname)  # find_module modname: sqlite

        if packname != self.name:
            return
        return self

    def load_module(self, fullname):
        print 'load_module fullname: {}'.format(fullname)  # load_module fullname: bottle.ext.sqlite

        print 'fullname in sys.modules: {}'.format(fullname in sys.modules)  # False
        if fullname in sys.modules:
            return sys.modules[fullname]

        packname, modname = fullname.rsplit('.', 1)
        print 'load_module packname: {}'.format(packname)  # load_module packname: bottle.ext
        print 'load_module modname: {}'.format(modname)  # load_module modname: sqlite

        realname = self.impmask % modname
        print 'load_module realname: {}'.format(realname)  # load_module realname: bottle_sqlite

        __import__(realname)

        module = sys.modules[fullname] = sys.modules[realname]
        print 'load_module module: {}'.format(module)  # load_module module: <module 'bottle_sqlite' from '/root/work/lanzw_frame/evolution/evolution_0024/venv/lib/python2.7/site-packages/bottle_sqlite.pyc'>

        setattr(self.module, modname, module)
        module.__loader__ = self
        return module

print _ImportRedirect('bottle.ext', 'bottle_%s')  # <__main__._ImportRedirect object at 0x7f66582fad10>

print _ImportRedirect('bottle.ext', 'bottle_%s').module  # <module 'bottle.ext' from '01_ImportRedirect.py'>


"""
>>>
>>> from bottle.ext import sqlite
name: bottle.ext
impmask: bottle_%s

find_module fullname: bottle.ext.sqlite
. not in fullname: False
find_module packname: bottle.ext
find_module modname: sqlite

load_module fullname: bottle.ext.sqlite
fullname in sys.modules: False
load_module packname: bottle.ext
load_module modname: sqlite
load_module realname: bottle_sqlite

find_module fullname: bottle_sqlite
. not in fullname: True
find_module fullname: sqlite3
. not in fullname: True
find_module fullname: sqlite3.dbapi2
. not in fullname: False
find_module packname: sqlite3
find_module modname: dbapi2
find_module fullname: sqlite3.datetime
. not in fullname: False
find_module packname: sqlite3
find_module modname: datetime
find_module fullname: sqlite3.time
. not in fullname: False
find_module packname: sqlite3
find_module modname: time
find_module fullname: sqlite3._sqlite3
. not in fullname: False
find_module packname: sqlite3
find_module modname: _sqlite3
find_module fullname: _sqlite3
. not in fullname: True
find_module fullname: inspect
. not in fullname: True
find_module fullname: dis
. not in fullname: True
find_module fullname: opcode
. not in fullname: True
find_module fullname: tokenize
. not in fullname: True
find_module fullname: token
. not in fullname: True

load_module module: <module 'bottle_sqlite' from '/root/work/lanzw_frame/evolution/evolution_0024/venv/lib/python2.7/site-packages/bottle_sqlite.pyc'>
>>>
>>>
"""