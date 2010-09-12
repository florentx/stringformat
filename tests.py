# -*- coding: utf-8 -*-

import unittest

from stringformat import FormattableString as f, _strformat


# object.__format__ does not exist in Python 2.5
has_object_format = hasattr(object, '__format__')


class BaseFormatterTest(unittest.TestCase):
    type2test = None

    def assertEqual(self, first, second, msg=None):
        # strict assertEqual method: verify value and type
        assert_equal = unittest.TestCase.assertEqual
        assert_equal(self, first, second, msg)
        assert_equal(self, type(first), type(second))

    def _prepare(self, *args):
        if len(args) == 1:
            return self.type2test(args[0])
        return tuple(self.type2test(v) for v in args)

    def _check_strformat(self, expected, fmt, value):
        value, expected = self._prepare(value, expected)
        # test both with and without the trailing 's'
        self.assertEqual(_strformat(value, fmt), expected)
        self.assertEqual(_strformat(value, fmt + 's'), expected)
        return expected, fmt, value

    def _check_format(self, expected, fmt, *args, **kwargs):
        fmt, expected = self._prepare(fmt, expected)
        self.assertEqual(f(fmt).format(*args, **kwargs), expected)
        return expected, fmt, args, kwargs

    def _check_raises(self, expected_exception, fmt, *args, **kwargs):
        fmt = self._prepare(fmt)
        try:
            f(fmt).format(*args, **kwargs)
        except expected_exception:
            pass
        else:
            raise self.failureException('%s not raised' %
                                        expected_exception.__name__)
        return expected_exception, fmt, args, kwargs

    assert_raises_25 = _check_raises

    def test_strformat(self):
        test = self._check_strformat

        # def test(expected, fmt, value):
        #     assert _strformat(value, fmt) == expected
        test('', '', '')
        test('abc', '', 'abc')
        test('abc', '.3', 'abc')
        test('ab', '.3', 'ab')
        test('abc', '.3', 'abcdef')
        test('', '.0', 'abcdef')
        test('abc', '3.3', 'abc')
        test('abc', '2.3', 'abc')
        test('ab', '2.2', 'abc')
        test('ab ', '3.2', 'abc')
        test('result', 'x<0', 'result')
        test('result', 'x<5', 'result')
        test('result', 'x<6', 'result')
        test('resultx', 'x<7', 'result')
        test('resultxx', 'x<8', 'result')
        test('result ', ' <7', 'result')
        test('result ', '<7', 'result')
        test(' result', '>7', ' result')
        test('  result', '>8', 'result')
        test(' result ', '^8', 'result')
        test(' result  ', '^9', 'result')
        test('  result  ', '^10', 'result')
        test('a' + ' ' * 9999, '10000', 'a')
        test(' ' * 10000, '10000', '')
        test(' ' * 10000000, '10000000', '')

    def test_format(self):
        test = self._check_format
        assert_raises = self._check_raises

        # Safety check
        self.assertTrue(hasattr(f(''), 'format'))

        # def test(expected, fmt, *args, **kwargs):
        #     assert f(fmt).format(*args, **kwargs) == expected
        test('', '')
        test('a', 'a')
        test('ab', 'ab')
        test('a{', 'a{{')
        test('a}', 'a}}')
        test('{b', '{{b')
        test('}b', '}}b')
        test('a{b', 'a{{b')

        # examples from the PEP:
        test("My name is Fred", "My name is {0}", "Fred")
        test("My name is Fred", "My name is {0[name]}", dict(name="Fred"))
        test("My name is Fred :-{}", "My name is {0} :-{{}}", "Fred")

        import datetime
        d = datetime.date(2007, 8, 18)
        test("The year is 2007", "The year is {0.year}", d)

        # classes we'll use for testing
        class C:

            def __init__(self, x=100):
                self._x = x

            def __format__(self, spec):
                return spec

        class D:

            def __init__(self, x):
                self.x = x

            def __format__(self, spec):
                return str(self.x)

        # class with __str__, but no __format__
        class E:

            def __init__(self, x):
                self.x = x

            def __str__(self):
                return 'E(' + self.x + ')'

        # class with __repr__, but no __format__ or __str__
        class F:

            def __init__(self, x):
                self.x = x

            def __repr__(self):
                return 'F(' + self.x + ')'

        # class with __format__ that forwards to string, for some format_spec's
        class G:

            def __init__(self, x):
                self.x = x

            def __str__(self):
                return "string is " + self.x

            def __format__(self, format_spec):
                if format_spec == 'd':
                    return 'G(' + self.x + ')'
                return object.__format__(self, format_spec)

        # class that returns a bad type from __format__
        class H:

            def __format__(self, format_spec):
                return 1.0

        class I(datetime.date):

            def __format__(self, format_spec):
                return self.strftime(str(format_spec))

        class J(int):

            def __format__(self, format_spec):
                return int.__format__(self * 2, format_spec)

        test('abc', 'abc')
        test('abc', '{0}', 'abc')
        test('abc', '{0:}', 'abc')
        test('Xabc', 'X{0}', 'abc')
        test('abcX', '{0}X', 'abc')
        test('XabcY', 'X{0}Y', 'abc')
        test('abc', '{1}', 1, 'abc')
        test('Xabc', 'X{1}', 1, 'abc')
        test('abcX', '{1}X', 1, 'abc')
        test('XabcY', 'X{1}Y', 1, 'abc')
        test('-15', '{0}', -15)
        test('-15abc', '{0}{1}', -15, 'abc')
        test('-15Xabc', '{0}X{1}', -15, 'abc')
        test('{', '{{')
        test('}', '}}')
        test('{}', '{{}}')
        test('{x}', '{{x}}')
        test('{123}', '{{{0}}}', 123)
        test('{{0}}', '{{{{0}}}}')
        test('}{', '}}{{')
        test('}x{', '}}x{{')

        # weird field names
        test('baz', '{0[foo-bar]}', {'foo-bar': 'baz'})
        test('baz', '{0[foo bar]}', {'foo bar': 'baz'})
        test('3', '{0[ ]}', {' ': 3})

        test('20', '{foo._x}', foo=C(20))
        test('2010', '{1}{0}', D(10), D(20))
        test('abc', '{0._x.x}', C(D('abc')))
        test('abc', '{0[0]}', ['abc', 'def'])
        test('def', '{0[1]}', ['abc', 'def'])
        test('def', '{0[1][0]}', ['abc', ['def']])
        test('def', '{0[1][0].x}', ['abc', [D('def')]])

        # strings
        test('abc', '{0:.3s}', 'abc')
        test('ab', '{0:.3s}', 'ab')
        test('abc', '{0:.3s}', 'abcdef')
        test('', '{0:.0s}', 'abcdef')
        test('abc', '{0:3.3s}', 'abc')
        test('abc', '{0:2.3s}', 'abc')
        test('ab ', '{0:3.2s}', 'abc')
        test('result', '{0:x<0s}', 'result')
        test('result', '{0:x<5s}', 'result')
        test('result', '{0:x<6s}', 'result')
        test('resultx', '{0:x<7s}', 'result')
        test('resultxx', '{0:x<8s}', 'result')
        test('result ', '{0: <7s}', 'result')
        test('result ', '{0:<7s}', 'result')
        test(' result', '{0:>7s}', 'result')
        test('  result', '{0:>8s}', 'result')
        test(' result ', '{0:^8s}', 'result')
        test(' result  ', '{0:^9s}', 'result')
        test('  result  ', '{0:^10s}', 'result')
        test('a' + ' ' * 9999, '{0:10000}', 'a')
        test(' ' * 10000, '{0:10000}', '')
        test(' ' * 10000000, '{0:10000000}', '')

        # format specifiers for user defined type
        test('abc', '{0:abc}', C())

        # !r and !s coercions
        test('Hello', '{0!s}', 'Hello')
        test('Hello', '{0!s}', 'Hello')
        test('Hello          ', '{0!s:15}', 'Hello')
        test('Hello          ', '{0!s:15s}', 'Hello')
        test("'Hello'", '{0!r}', 'Hello')
        test("'Hello'", '{0!r:}', 'Hello')
        test('F(Hello)', '{0!r}', F('Hello'))

        # test fallback to object.__format__
        test('{}', '{0}', {})
        test('[]', '{0}', [])
        test('[1]', '{0}', [1])
        test('E(data)', '{0}', E('data'))

        # XXX pending deprecation
        #  * object.__format__ with a non-empty format string is deprecated
        test(' E(data)  ', '{0:^10}', E('data'))
        test(' E(data)  ', '{0:^10s}', E('data'))
        if has_object_format:
            test(' string is data', '{0:>15s}', G('data'))

        test('G(data)', '{0:d}', G('data'))
        test('string is data', '{0!s}', G('data'))

        test('date: 2007-08-27', '{0:date: %Y-%m-%d}',
             I(year=2007, month=8, day=27))

        if has_object_format:
            # test deriving from a builtin type and overriding __format__
            test('20', '{0}', J(10))

        # string format specifiers
        test('a', '{0:}', 'a')

        # computed format specifiers
        test('hello', '{0:.{1}}', 'hello world', 5)
        test('hello', '{0:.{1}s}', 'hello world', 5)
        test('hello', '{0:.{precision}s}', 'hello world', precision=5)
        test('hello     ', '{0:{width}.{precision}s}',
             'hello world', width=10, precision=5)
        test('hello     ', '{0:{width}.{precision}s}',
             'hello world', width='10', precision='5')

        # test various errors
        #self.assertRaises(ValueError, f('{').format)
        #self.assertRaises(ValueError, f('}').format)
        #self.assertRaises(ValueError, f('a{').format)
        #self.assertRaises(ValueError, f('a}').format)
        #self.assertRaises(ValueError, f('{a').format)
        #self.assertRaises(ValueError, f('}a').format)
        #self.assertRaises(IndexError, f('{0}').format)         # KeyError
        #self.assertRaises(IndexError, f('{1}').format, 'abc')  # KeyError
        assert_raises(KeyError, '{x}')
        #self.assertRaises(ValueError, f("}{").format)
        #self.assertRaises(ValueError, f("abc{0:{}").format)    # KeyError
        #self.assertRaises(ValueError, f("{0").format)
        #self.assertRaises(IndexError, f("{0.}").format)        # ValueError
        assert_raises(ValueError, '{0.}', 0)
        #self.assertRaises(IndexError, f("{0[}").format)        # ValueError
        #XXX assert_raises(ValueError, '{0[}', [])
        assert_raises(KeyError, '{0]}')
        assert_raises(ValueError, '{0.[]}', 0)
        assert_raises(ValueError, '{0..foo}', 0)
        assert_raises(ValueError, '{0[0}', 0)
        assert_raises(ValueError, '{0[0:foo}', 0)
        assert_raises(KeyError, '{c]}')
        #self.assertRaises(ValueError, f("{{ {{{0}}").format, 0)
        #self.assertRaises(ValueError, f("{0}}").format, 0)
        assert_raises(KeyError, '{foo}', bar=3)
        #self.assertRaises(ValueError, f("{0!x}").format, 3)
        #self.assertRaises(ValueError, f("{0!}").format, 0)
        #self.assertRaises(ValueError, f("{0!rs}").format, 0)
        #self.assertRaises(ValueError, f("{!}").format)         # KeyError
        # self.assertRaises(IndexError, f("{:}").format)        # KeyError
        # self.assertRaises(IndexError, f("{:s}").format)       # KeyError
        # self.assertRaises(IndexError, f("{}").format)         # KeyError

        # issue 6089
        #self.assertRaises(ValueError, f("{0[0]x}").format, [None])
        #self.assertRaises(ValueError, f("{0[0](10)}").format, [None])

        # can't have a replacement on the field name portion
        assert_raises(TypeError, '{0[{1}]}', 'abcdefg', 4)

        # exceed maximum recursion depth
        #self.assertRaises(ValueError, f("{0:{1:{2}}}").format, 'abc', 's', '')
        #self.assertRaises(ValueError, f("{0:{1:{2:{3:{4:{5:{6}}}}}}}").format,
                          #0, 1, 2, 3, 4, 5, 6, 7)

        # string format spec errors
        #self.assertRaises(ValueError, f("{0:-s}").format, '')
        #self.assertRaises(ValueError, format, "", "-")
        #self.assertRaises(ValueError, f("{0:=s}").format, '')

    def test_incompatibilities(self):
        # Differences with Python 2.7

        # KeyError instead of IndexError (or ValueError)
        self.assert_raises_25(KeyError, '{0}')
        self.assert_raises_25(KeyError, '{1}', 'abc')
        self.assert_raises_25(KeyError, 'abc{0:{}')     # ValueError
        self.assert_raises_25(KeyError, '{!}')          # ValueError
        self.assert_raises_25(KeyError, '{:}')
        self.assert_raises_25(KeyError, '{:s}')
        self.assert_raises_25(KeyError, '{}')

        # ValueError instead of IndexError
        self.assert_raises_25(ValueError, '{0.}')
        self.assert_raises_25(ValueError, '{0[}')
        self.assert_raises_25(ValueError, '{0.[]}')
        self.assert_raises_25(ValueError, '{0..foo}')
        self.assert_raises_25(ValueError, '{0[0}')
        self.assert_raises_25(ValueError, '{0[0:foo}')

    def test_format_extra(self):
        # Additional tests
        test = self._check_format
        assert_raises = self._check_raises

        import datetime
        d = datetime.date(2007, 8, 18)
        test("Recorded on 2007-08-18", "Recorded on {0:%Y-%m-%d}", d)

        # An Enum-like structure.
        class Enum(dict):
            __getattr__ = dict.__getitem__

            def __getitem__(self, attr):
                raise AssertionError

        test('42', '{ ] [ . [ ]}', **{' ] ': {' . [ ': 42}})
        test('{ 42 }', '{{{ ] [ . [ ]:0< 2n} }}', **{' ] ': {' . [ ': 42}})
        test('42', '{a]b[c[d].e]f.g[h.i]}',
             **{'a]b': {'c[d': Enum({'e]f': Enum(g={'h.i': 42})})}})
        test('42', '{.qsd]er[fe].QsD[ER].e].az.r[t[u][[X][Y][Z.]}',
             Enum({'qsd]er': {'fe': Enum(QsD={'ER': Enum({'e]':
             Enum(az=Enum(r={'t[u': {'[X': {'Y': {'Z.': 42}}}}))})})}}))

    def test_format_numeric(self):
        test = self._check_format
        assert_raises = self._check_raises

        test('   42', '{0:=5}', 42)
        test('___42', '{0:_=5}', 42)
        test('-  42', '{0:=5}', -42)
        test('+  42', '{0:=+5}', 42)
        test('-__42', '{0:_= 5}', -42)
        test('+__42', '{0:_=+5}', 42)
        test('__+42', '{0:_>+5}', 42)
        test('00042', '{0:05}', 42)
        test('-0042', '{0:05}', -42)
        test('00042', '{0:=05}', 42)
        test('-0042', '{0:=05}', -42)
        test('  -42', '{0:#5}', -42)
        test('000-42.', '{0:>07}', '-42.')
        test('-000042', '{0:07}', -42)
        test('+000042', '{0:+07}', 42)
        test('###42', '{0:#=5n}', 42.)
        test('00042.0', '{0:>07}', 42.)
        test('-##42', '{0:#=5n}', -42.)
        test('00-42.0', '{0:>07}', -42.)
        test('+##42.0', '{0:#=+7}', 42.)
        test('00+42.0', '{0:>+07}', 42.)

        # XXX broken
        #test('42.000000%', '{0:%}', .42)        # TypeError
        #test('+42,000', '{0:>+07,}', 42000)     # '0+42000'

        assert_raises(ValueError, '{0:>+07K}', 42.)
        assert_raises(ValueError, '{0:>07s}', .42)
        assert_raises(ValueError, '{0:>+07s}', '42')


# For Python >= 2.6, compare the result with the standard Python formatting
if has_object_format:

    builtin_function_or_method = type(len)

    # Python 2.6 has some limitations (no auto-numbering)
    _empty_field_errors = []
    try:
        '{}'.format(42)
    except ValueError, exc:
        # Python 2.6 raises ValueError: zero length field name in format
        _empty_field_errors.append(repr(exc))

    try:
        '{.real}'.format(42)
    except ValueError, exc:
        # Python 2.6 raises ValueError: empty field name
        _empty_field_errors.append(repr(exc))

    def _test_format(string, *args, **kwargs):
        """Compare with standard implementation.

        Return a pair (tuple) of results (standard_result, actual_result).
        """

        # Monkey patch the _format_field to skip builtin method __format__
        def _format_field(value, parts, conv, spec):
            for k, part, _ in parts:
                if k:
                    if part.isdigit():
                        value = value[int(part)]
                    else:
                        value = value[part]
                else:
                    value = getattr(value, part)
            if conv:
                value = ('%r' if (conv == 'r') else '%s') % (value,)
            format_value = getattr(value, '__format__', None)
            if format_value and (hasattr(value, 'strftime') or
                    not isinstance(format_value, builtin_function_or_method)):
                value = format_value(spec)
            else:
                # Skip the __format__ method for builtin types
                value = _strformat(value, spec)
            return value

        # Monkey patch the _format_field to skip builtin method __format__
        import stringformat as mod
        original_format_field = mod._format_field
        mod._format_field = _format_field
        try:
            s1 = repr(string.format(*args, **kwargs))
        except Exception, exc:
            s1 = repr(exc)
        try:
            s2 = repr(f(string).format(*args, **kwargs))
        except Exception, exc:
            s2 = repr(exc)
        finally:
            mod._format_field = original_format_field
        return s1, s2

    _BaseFormatterTest25 = BaseFormatterTest

    class BaseFormatterTest(_BaseFormatterTest25):

        def _check_strformat(self, expected, fmt, value):
            check_strformat = super(BaseFormatterTest, self)._check_strformat
            check_strformat(expected, fmt, value)

            value, expected = self._prepare(value, expected)
            # test the built-in format() function
            self.assertEqual(format(value, fmt), expected)
            self.assertEqual(format(value, fmt + 's'), expected)

        def _compare_with_standard(self, fmt, *args, **kwargs):
            # Compare with standard formatting
            fmt = self._prepare(fmt)
            std_result, result = _test_format(fmt, *args, **kwargs)
            # Check same result or same error message
            if std_result not in _empty_field_errors:
                self.assertEqual(std_result, result)
            return result

        def _check_format(self, expected, fmt, *args, **kwargs):
            rv = self._compare_with_standard(fmt, *args, **kwargs)
            if expected is None:
                print '\n%r.format(*%r, **%r)' % (fmt, args, kwargs)
                print '***', rv
            else:
                check_format = super(BaseFormatterTest, self)._check_format
                check_format(expected, fmt, *args, **kwargs)

        def _check_raises(self, expected_exception, fmt, *args, **kwargs):
            rv = self._compare_with_standard(fmt, *args, **kwargs)
            if expected_exception is None:
                print '\n%r.format(*%r, **%r)' % (fmt, args, kwargs)
                print '***', rv
            else:
                check_raises = super(BaseFormatterTest, self)._check_raises
                check_raises(expected_exception, fmt, *args, **kwargs)

    del _BaseFormatterTest25


class StringFormatterTest(BaseFormatterTest):
    type2test = str


class UnicodeFormatterTest(BaseFormatterTest):
    type2test = unicode


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StringFormatterTest))
    suite.addTest(unittest.makeSuite(UnicodeFormatterTest))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest='suite')
