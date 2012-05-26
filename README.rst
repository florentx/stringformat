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
