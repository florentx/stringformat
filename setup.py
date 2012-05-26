# -*- coding: utf-8 -*-
"""
StringFormat
============

StringFormat is an independent port of the Python 3 advanced string
formatting, compatible with Python >= 2.4.
This implementation is pure Python.

Add the method ``str.format`` only if it is missing (Python < 2.6)::

    import stringformat

    stringformat.init()


Enable auto-numbering fields (``"{} {}"`` instead of ``"{0} {1}"``)
with Python 2.6 also::

    import sys
    import stringformat

    if sys.version_info < (2, 7):
        stringformat.init(True)


The advanced string formatting is officially included in the language
since Python 2.6.

http://docs.python.org/whatsnew/2.6.html#pep-3101-advanced-string-formatting

"""

from setuptools import setup


setup(
    name='StringFormat',
    version='0.5',
    license='BSD',
    url='http://github.com/florentx/stringformat',
    author='Florent Xicluna',
    author_email='florent.xicluna@gmail.com',
    description='Advanced String Formatting for Python >= 2.4',
    long_description=__doc__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Filters',
    ],
    zip_safe=False,
    platforms='any',
    py_modules=['stringformat'],
    test_suite='tests',
)
