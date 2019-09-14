#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys


def load(target, **namespace):
    """ Import a module or fetch an object from a module.

        * ``package.module`` returns `module` as a module object.
        * ``pack.mod:name`` returns the module variable `name` from `pack.mod`.
        * ``pack.mod:func()`` calls `pack.mod.func()` and returns the result.

        The last form accepts not only function calls, but any type of
        expression. Keyword arguments passed to this function are available as
        local variables. Example: ``import_string('re:compile(x)', x='[a-z]')``
    """
    if ':' in target:
        module, target = target.split(":", 1)
    else:
        module, target = (target, None)
    # module, target = target.split(":", 1) if ':' in target else (target, None)
    print 'module: {}'.format(module)
    print 'target: {}'.format(target)
    """
    module: package.module
    target: None
    
    module: pack.mod
    target: name
    
    module: pack.mod
    target: func()
    """

    if module not in sys.modules:
        __import__(module)

    if not target:
        return sys.modules[module]

    if target.isalnum():
        return getattr(sys.modules[module], target)

    package_name = module.split('.')[0]
    print 'package_name: {}'.format(package_name)
    """
    package_name: pack
    
    package_name: pack
    """

    namespace[package_name] = sys.modules[package_name]
    return eval('%s.%s' % (module, target), namespace)


# allback = load(callback)
# server = load(server)

load('pack.mod:func()')
"""
module: package.module
target: None
"""
