# -*- coding: utf-8 -*-
import imp
import sys

class _ImportRedirect(object):
    def __init__(self, name, impmask):
        ''' Create a virtual package that redirects imports (see PEP 302). '''
        print name  # evolution_0020.ext
        print impmask  # bottle_%s
        self.name = name
        self.impmask = impmask
        # 与其它任何 Python 的东西一样，模块也是对象。只要导入了，总可以用全局 dictionary sys.modules 来得到一个模块的引用
        self.module = sys.modules.setdefault(name, imp.new_module(name))
        self.module.__dict__.update({'__file__': '<virtual>', '__path__': [],
                                    '__all__': [], '__loader__': self})
        sys.meta_path.append(self)

    def find_module(self, fullname, path=None):
        if '.' not in fullname: return
        packname, modname = fullname.rsplit('.', 1)
        if packname != self.name: return
        return self

    def load_module(self, fullname):
        if fullname in sys.modules: return sys.modules[fullname]
        packname, modname = fullname.rsplit('.', 1)
        realname = self.impmask % modname
        __import__(realname)
        module = sys.modules[fullname] = sys.modules[realname]
        setattr(self.module, modname, module)
        module.__loader__ = self
        return module

print __name__
ext = _ImportRedirect(__name__+'.ext', 'bottle_%s').module
