#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
standard commands (标准命令)是 distutils 内建命令，而 Extra commands（附加命令）是像 setuptools 这样的第三方包创建的
python setup.py install -n --record install.log
python setup.py develop
"""

from distutils.core import setup
import setuptools

import evolution_0009

setup(name='evolution_0009',
      version='%d.%d.%d' % evolution_0009.__version__,
      description='Bottle Web Framework',
      long_description=open('../../README.md').read(),
      author='Marcel Hellkamp',
      author_email='marc@gsites.de',
      url='http://github.com/defnull/bottle',
      py_modules=['evolution_0009'],
      license='MIT',
      classifiers=['Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries :: Application Frameworks']
     )



