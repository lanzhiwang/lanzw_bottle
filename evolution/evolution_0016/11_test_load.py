# -*- coding: utf-8 -*-
import sys

def _load(target, **vars):
    """ Fetch something from a module. The exact behaviour depends on the the
        target string:

        If the target is a valid python import path (e.g. `package.module`),
        the rightmost part is returned as a module object.
        If the target contains a colon (e.g. `package.module:var`) the module
        variable specified after the colon is returned.
        If the part after the colon contains any non-alphanumeric characters
        (e.g. `package.module:func(var)`) the result of the expression
        is returned. The expression has access to keyword arguments supplied
        to this function.

        Example::
        >>> _load('bottle')
        <module 'bottle' from 'bottle.py'>
        >>> _load('bottle:Bottle')
        <class 'bottle.Bottle'>
        >>> _load('bottle:cookie_encode(v, secret)', v='foo', secret='bar')
        '!F+hN4dQxaDJ4QxxaZ+Z3jw==?gAJVA2Zvb3EBLg=='

    """
    module, target = target.split(":", 1) if ':' in target else (target, None)
    print module  # bottle  bottle  bottle
    print target  # None    Botstle cookie_encode(v, secret)

    # print sys.modules
    if module not in sys.modules:
        __import__(module)
    if not target:
        return sys.modules[module]
    if target.isalnum():
        return getattr(sys.modules[module], target)
    package_name = module.split('.')[0]
    vars[package_name] = sys.modules[package_name]
    return eval('%s.%s' % (module, target), vars)

# _load('bottle')
# _load('bottle:Botstle')
_load('bottle:cookie_encode(v, secret)', v='foo', secret='bar')


"""
sys.modules
{
'copy_reg': <module 'copy_reg' from '/usr/lib64/python2.7/copy_reg.pyc'>,
'sre_compile': <module 'sre_compile' from '/usr/lib64/python2.7/sre_compile.pyc'>,
'_sre': <module '_sre' (built-in)>, 
'encodings': <module 'encodings' from '/usr/lib64/python2.7/encodings/__init__.pyc'>, 
'site': <module 'site' from '/usr/lib64/python2.7/site.pyc'>, 
'__builtin__': <module '__builtin__' (built-in)>, 
'sysconfig': <module 'sysconfig' from '/usr/lib64/python2.7/sysconfig.pyc'>, 
'__main__': <module '__main__' from '11_test_load.py'>, 
'encodings.encodings': None, 
'abc': <module 'abc' from '/usr/lib64/python2.7/abc.pyc'>, 
'posixpath': <module 'posixpath' from '/usr/lib64/python2.7/posixpath.pyc'>, 
'_weakrefset': <module '_weakrefset' from '/usr/lib64/python2.7/_weakrefset.pyc'>, 
'errno': <module 'errno' (built-in)>, 
'encodings.codecs': None, 
'sre_constants': <module 'sre_constants' from '/usr/lib64/python2.7/sre_constants.pyc'>, 
're': <module 're' from '/usr/lib64/python2.7/re.pyc'>, 
'_abcoll': <module '_abcoll' from '/usr/lib64/python2.7/_abcoll.pyc'>, 
'types': <module 'types' from '/usr/lib64/python2.7/types.pyc'>, 
'_codecs': <module '_codecs' (built-in)>, 
'encodings.__builtin__': None, 
'_warnings': <module '_warnings' (built-in)>, 
'genericpath': <module 'genericpath' from '/usr/lib64/python2.7/genericpath.pyc'>, 
'stat': <module 'stat' from '/usr/lib64/python2.7/stat.pyc'>, 
'zipimport': <module 'zipimport' (built-in)>, 
'_sysconfigdata': <module '_sysconfigdata' from '/usr/lib64/python2.7/_sysconfigdata.pyc'>, 
'warnings': <module 'warnings' from '/usr/lib64/python2.7/warnings.pyc'>, 
'UserDict': <module 'UserDict' from '/usr/lib64/python2.7/UserDict.pyc'>, 
'encodings.utf_8': <module 'encodings.utf_8' from '/usr/lib64/python2.7/encodings/utf_8.pyc'>, 
'sys': <module 'sys' (built-in)>, 
'codecs': <module 'codecs' from '/usr/lib64/python2.7/codecs.pyc'>, 
'os.path': <module 'posixpath' from '/usr/lib64/python2.7/posixpath.pyc'>, 
'signal': <module 'signal' (built-in)>, 
'traceback': <module 'traceback' from '/usr/lib64/python2.7/traceback.pyc'>, 
'linecache': <module 'linecache' from '/usr/lib64/python2.7/linecache.pyc'>, 
'posix': <module 'posix' (built-in)>, 
'encodings.aliases': <module 'encodings.aliases' from '/usr/lib64/python2.7/encodings/aliases.pyc'>, 
'exceptions': <module 'exceptions' (built-in)>, 
'sre_parse': <module 'sre_parse' from '/usr/lib64/python2.7/sre_parse.pyc'>, 
'os': <module 'os' from '/usr/lib64/python2.7/os.pyc'>, 
'_weakref': <module '_weakref' (built-in)>s
}
"""