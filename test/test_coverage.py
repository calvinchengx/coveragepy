"""Tests for Coverage."""
# http://nedbatchelder.com/code/coverage

import os, sys

import coverage
from coverage.misc import CoverageException

sys.path.insert(0, os.path.split(__file__)[0]) # Force relative import for Py3k
from coveragetest import CoverageTest


class TestCoverageTest(CoverageTest):
    """Make sure our complex self.check_coverage method works."""

    def test_successful_coverage(self):
        # The simplest run possible.
        self.check_coverage("""\
            a = 1
            b = 2
            """,
            [1,2]
            )
        # You can provide a list of possible statement matches.
        self.check_coverage("""\
            a = 1
            b = 2
            """,
            ([100], [1,2], [1723,47]),
            )
        # You can specify missing lines.
        self.check_coverage("""\
            a = 1
            if a == 2:
                a = 3
            """,
            [1,2,3],
            missing="3",
            )
        # You can specify a list of possible missing lines.
        self.check_coverage("""\
            a = 1
            if a == 2:
                a = 3
            """,
            [1,2,3],
            missing=("47-49", "3", "100,102")
            )

    def test_failed_coverage(self):
        # If the lines are wrong, the message shows right and wrong.
        self.assertRaisesRegexp(AssertionError,
            r"\[1, 2] != \[1]",
            self.check_coverage, """\
                a = 1
                b = 2
                """,
                [1]
            )
        # If the list of lines possibilities is wrong, the msg shows right.
        self.assertRaisesRegexp(AssertionError,
            r"None of the lines choices matched \[1, 2]",
            self.check_coverage, """\
                a = 1
                b = 2
                """,
                ([1], [2])
            )
        # If the missing lines are wrong, the message shows right and wrong.
        self.assertRaisesRegexp(AssertionError,
            r"'3' != '37'",
            self.check_coverage, """\
                a = 1
                if a == 2:
                    a = 3
                """,
                [1,2,3],
                missing="37",
            )
        # If the missing lines possibilities are wrong, the msg shows right.
        self.assertRaisesRegexp(AssertionError,
            r"None of the missing choices matched '3'",
            self.check_coverage, """\
                a = 1
                if a == 2:
                    a = 3
                """,
                [1,2,3],
                missing=("37", "4-10"),
            )


class BasicCoverageTest(CoverageTest):
    """The simplest tests, for quick smoke testing of fundamental changes."""

    def test_simple(self):
        self.check_coverage("""\
            a = 1
            b = 2

            c = 4
            # Nothing here
            d = 6
            """,
            [1,2,4,6], report="4 0 100%")

    def test_indentation_wackiness(self):
        # Partial final lines are OK.
        self.check_coverage("""\
            import sys
            if not sys.path:
                a = 1
                """,
            [1,2,3], "3")

    def test_multiline_initializer(self):
        self.check_coverage("""\
            d = {
                'foo': 1+2,
                'bar': (lambda x: x+1)(1),
                'baz': str(1),
            }

            e = { 'foo': 1, 'bar': 2 }
            """,
            [1,7], "")

    def test_list_comprehension(self):
        self.check_coverage("""\
            l = [
                2*i for i in range(10)
                if i > 5
                ]
            assert l == [12, 14, 16, 18]
            """,
            [1,5], "")


class SimpleStatementTest(CoverageTest):
    """Testing simple single-line statements."""

    def test_expression(self):
        # Bare expressions as statements are tricky: some implementations
        # optimize some of them away.  All implementations seem to count
        # the implicit return at the end as executable.
        self.check_coverage("""\
            12
            23
            """,
            ([1,2],[2]), "")
        self.check_coverage("""\
            12
            23
            a = 3
            """,
            ([1,2,3],[3]), "")
        self.check_coverage("""\
            1 + 2
            1 + \\
                2
            """,
            ([1,2], [2]), "")
        self.check_coverage("""\
            1 + 2
            1 + \\
                2
            a = 4
            """,
            ([1,2,4], [4]), "")

    def test_assert(self):
        self.check_coverage("""\
            assert (1 + 2)
            assert (1 +
                2)
            assert (1 + 2), 'the universe is broken'
            assert (1 +
                2), \\
                'something is amiss'
            """,
            [1,2,4,5], "")

    def test_assignment(self):
        # Simple variable assignment
        self.check_coverage("""\
            a = (1 + 2)
            b = (1 +
                2)
            c = \\
                1
            """,
            [1,2,4], "")

    def test_assign_tuple(self):
        self.check_coverage("""\
            a = 1
            a,b,c = 7,8,9
            assert a == 7 and b == 8 and c == 9
            """,
            [1,2,3], "")

    def test_attribute_assignment(self):
        # Attribute assignment
        self.check_coverage("""\
            class obj: pass
            o = obj()
            o.foo = (1 + 2)
            o.foo = (1 +
                2)
            o.foo = \\
                1
            """,
            [1,2,3,4,6], "")

    def test_list_of_attribute_assignment(self):
        self.check_coverage("""\
            class obj: pass
            o = obj()
            o.a, o.b = (1 + 2), 3
            o.a, o.b = (1 +
                2), (3 +
                4)
            o.a, o.b = \\
                1, \\
                2
            """,
            [1,2,3,4,7], "")

    def test_augmented_assignment(self):
        self.check_coverage("""\
            a = 1
            a += 1
            a += (1 +
                2)
            a += \\
                1
            """,
            [1,2,3,5], "")

    def test_triple_string_stuff(self):
        self.check_coverage("""\
            a = '''
                a multiline
                string.
                '''
            b = '''
                long expression
                ''' + '''
                on many
                lines.
                '''
            c = len('''
                long expression
                ''' +
                '''
                on many
                lines.
                ''')
            """,
            [1,5,11], "")

    def test_pass(self):
        # pass is tricky: if it's the only statement in a block, then it is
        # "executed". But if it is not the only statement, then it is not.
        self.check_coverage("""\
            if 1==1:
                pass
            """,
            [1,2], "")
        self.check_coverage("""\
            def foo():
                pass
            foo()
            """,
            [1,2,3], "")
        self.check_coverage("""\
            def foo():
                "doc"
                pass
            foo()
            """,
            ([1,3,4], [1,4]), "")
        self.check_coverage("""\
            class Foo:
                def foo(self):
                    pass
            Foo().foo()
            """,
            [1,2,3,4], "")
        self.check_coverage("""\
            class Foo:
                def foo(self):
                    "Huh?"
                    pass
            Foo().foo()
            """,
            ([1,2,4,5], [1,2,5]), "")

    def test_del(self):
        self.check_coverage("""\
            d = { 'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1 }
            del d['a']
            del d[
                'b'
                ]
            del d['c'], \\
                d['d'], \\
                d['e']
            assert(len(d.keys()) == 0)
            """,
            [1,2,3,6,9], "")

    if sys.version_info < (3, 0):   # Print statement is gone in Py3k.
        def test_print(self):
            self.check_coverage("""\
                print "hello, world!"
                print ("hey: %d" %
                    17)
                print "goodbye"
                print "hello, world!",
                print ("hey: %d" %
                    17),
                print "goodbye",
                """,
                [1,2,4,5,6,8], "")

    def test_raise(self):
        self.check_coverage("""\
            try:
                raise Exception(
                    "hello %d" %
                    17)
            except:
                pass
            """,
            [1,2,5,6], "")

    def test_return(self):
        self.check_coverage("""\
            def fn():
                a = 1
                return a

            x = fn()
            assert(x == 1)
            """,
            [1,2,3,5,6], "")
        self.check_coverage("""\
            def fn():
                a = 1
                return (
                    a +
                    1)

            x = fn()
            assert(x == 2)
            """,
            [1,2,3,7,8], "")
        self.check_coverage("""\
            def fn():
                a = 1
                return (a,
                    a + 1,
                    a + 2)

            x,y,z = fn()
            assert x == 1 and y == 2 and z == 3
            """,
            [1,2,3,7,8], "")

    def test_yield(self):
        self.check_coverage("""\
            from __future__ import generators
            def gen():
                yield 1
                yield (2+
                    3+
                    4)
                yield 1, \\
                    2
            a,b,c = gen()
            assert a == 1 and b == 9 and c == (1,2)
            """,
            [1,2,3,4,7,9,10], "")

    def test_break(self):
        self.check_coverage("""\
            for x in range(10):
                a = 2 + x
                break
                a = 4
            assert a == 2
            """,
            [1,2,3,4,5], "4")

    def test_continue(self):
        self.check_coverage("""\
            for x in range(10):
                a = 2 + x
                continue
                a = 4
            assert a == 11
            """,
            [1,2,3,4,5], "4")

    if 0:
        # Peephole optimization of jumps to jumps can mean that some statements
        # never hit the line tracer.  The behavior is different in different
        # versions of Python, so don't run this test:
        def test_strange_unexecuted_continue(self):
            self.check_coverage("""\
                a = b = c = 0
                for n in range(100):
                    if n % 2:
                        if n % 4:
                            a += 1
                        continue    # <-- This line may not be hit.
                    else:
                        b += 1
                    c += 1
                assert a == 50 and b == 50 and c == 50

                a = b = c = 0
                for n in range(100):
                    if n % 2:
                        if n % 3:
                            a += 1
                        continue    # <-- This line is always hit.
                    else:
                        b += 1
                    c += 1
                assert a == 33 and b == 50 and c == 50
                """,
                [1,2,3,4,5,6,8,9,10, 12,13,14,15,16,17,19,20,21], "")

    def test_import(self):
        self.check_coverage("""\
            import string
            from sys import path
            a = 1
            """,
            [1,2,3], "")
        self.check_coverage("""\
            import string
            if 1 == 2:
                from sys import path
            a = 1
            """,
            [1,2,3,4], "3")
        self.check_coverage("""\
            import string, \\
                os, \\
                re
            from sys import path, \\
                stdout
            a = 1
            """,
            [1,4,6], "")
        self.check_coverage("""\
            import sys, sys as s
            assert s.path == sys.path
            """,
            [1,2], "")
        self.check_coverage("""\
            import sys, \\
                sys as s
            assert s.path == sys.path
            """,
            [1,3], "")
        self.check_coverage("""\
            from sys import path, \\
                path as p
            assert p == path
            """,
            [1,3], "")
        self.check_coverage("""\
            from sys import \\
                *
            assert len(path) > 0
            """,
            [1,3], "")

    def test_global(self):
        self.check_coverage("""\
            g = h = i = 1
            def fn():
                global g
                global h, \\
                    i
                g = h = i = 2
            fn()
            assert g == 2 and h == 2 and i == 2
            """,
            [1,2,6,7,8], "")
        self.check_coverage("""\
            g = h = i = 1
            def fn():
                global g; g = 2
            fn()
            assert g == 2 and h == 1 and i == 1
            """,
            [1,2,3,4,5], "")

    if sys.version_info < (3, 0):
        # In Python 2.x, exec is a statement.
        def test_exec(self):
            self.check_coverage("""\
                a = b = c = 1
                exec "a = 2"
                exec ("b = " +
                    "c = " +
                    "2")
                assert a == 2 and b == 2 and c == 2
                """,
                [1,2,3,6], "")
            self.check_coverage("""\
                vars = {'a': 1, 'b': 1, 'c': 1}
                exec "a = 2" in vars
                exec ("b = " +
                    "c = " +
                    "2") in vars
                assert vars['a'] == 2 and vars['b'] == 2 and vars['c'] == 2
                """,
                [1,2,3,6], "")
            self.check_coverage("""\
                globs = {}
                locs = {'a': 1, 'b': 1, 'c': 1}
                exec "a = 2" in globs, locs
                exec ("b = " +
                    "c = " +
                    "2") in globs, locs
                assert locs['a'] == 2 and locs['b'] == 2 and locs['c'] == 2
                """,
                [1,2,3,4,7], "")
    else:
        # In Python 3.x, exec is a function.
        def test_exec(self):
            self.check_coverage("""\
                a = b = c = 1
                exec("a = 2")
                exec("b = " +
                    "c = " +
                    "2")
                assert a == 2 and b == 2 and c == 2
                """,
                [1,2,3,6], "")
            self.check_coverage("""\
                vars = {'a': 1, 'b': 1, 'c': 1}
                exec("a = 2", vars)
                exec("b = " +
                    "c = " +
                    "2", vars)
                assert vars['a'] == 2 and vars['b'] == 2 and vars['c'] == 2
                """,
                [1,2,3,6], "")
            self.check_coverage("""\
                globs = {}
                locs = {'a': 1, 'b': 1, 'c': 1}
                exec("a = 2", globs, locs)
                exec("b = " +
                    "c = " +
                    "2", globs, locs)
                assert locs['a'] == 2 and locs['b'] == 2 and locs['c'] == 2
                """,
                [1,2,3,4,7], "")

    def test_extra_doc_string(self):
        self.check_coverage("""\
            a = 1
            "An extra docstring, should be a comment."
            b = 3
            assert (a,b) == (1,3)
            """,
            [1,3,4], "")
        self.check_coverage("""\
            a = 1
            "An extra docstring, should be a comment."
            b = 3
            123 # A number for some reason: ignored
            1+1 # An expression: executed.
            c = 6
            assert (a,b,c) == (1,3,6)
            """,
            ([1,3,6,7], [1,3,5,6,7], [1,3,4,5,6,7]), "")


class CompoundStatementTest(CoverageTest):
    """Testing coverage of multi-line compound statements."""

    def test_statement_list(self):
        self.check_coverage("""\
            a = 1;
            b = 2; c = 3
            d = 4; e = 5;

            assert (a,b,c,d,e) == (1,2,3,4,5)
            """,
            [1,2,3,5], "")

    def test_if(self):
        self.check_coverage("""\
            a = 1
            if a == 1:
                x = 3
            assert x == 3
            if (a ==
                1):
                x = 7
            assert x == 7
            """,
            [1,2,3,4,5,7,8], "")
        self.check_coverage("""\
            a = 1
            if a == 1:
                x = 3
            else:
                y = 5
            assert x == 3
            """,
            [1,2,3,5,6], "5")
        self.check_coverage("""\
            a = 1
            if a != 1:
                x = 3
            else:
                y = 5
            assert y == 5
            """,
            [1,2,3,5,6], "3")
        self.check_coverage("""\
            a = 1; b = 2
            if a == 1:
                if b == 2:
                    x = 4
                else:
                    y = 6
            else:
                z = 8
            assert x == 4
            """,
            [1,2,3,4,6,8,9], "6-8")

    def test_elif(self):
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a == 1:
                x = 3
            elif b == 2:
                y = 5
            else:
                z = 7
            assert x == 3
            """,
            [1,2,3,4,5,7,8], "4-7", report="7 3 57% 4-7")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a != 1:
                x = 3
            elif b == 2:
                y = 5
            else:
                z = 7
            assert y == 5
            """,
            [1,2,3,4,5,7,8], "3, 7", report="7 2 71% 3, 7")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a != 1:
                x = 3
            elif b != 2:
                y = 5
            else:
                z = 7
            assert z == 7
            """,
            [1,2,3,4,5,7,8], "3, 5", report="7 2 71% 3, 5")

    def test_elif_no_else(self):
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a == 1:
                x = 3
            elif b == 2:
                y = 5
            assert x == 3
            """,
            [1,2,3,4,5,6], "4-5", report="6 2 67% 4-5")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a != 1:
                x = 3
            elif b == 2:
                y = 5
            assert y == 5
            """,
            [1,2,3,4,5,6], "3", report="6 1 83% 3")

    def test_elif_bizarre(self):
        self.check_coverage("""\
            def f(self):
                if self==1:
                    x = 3
                elif self.m('fred'):
                    x = 5
                elif (g==1) and (b==2):
                    x = 7
                elif self.m('fred')==True:
                    x = 9
                elif ((g==1) and (b==2))==True:
                    x = 11
                else:
                    x = 13
            """,
            [1,2,3,4,5,6,7,8,9,10,11,13], "2-13")

    def test_split_if(self):
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if \\
                a == 1:
                x = 3
            elif \\
                b == 2:
                y = 5
            else:
                z = 7
            assert x == 3
            """,
            [1,2,4,5,7,9,10], "5-9")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if \\
                a != 1:
                x = 3
            elif \\
                b == 2:
                y = 5
            else:
                z = 7
            assert y == 5
            """,
            [1,2,4,5,7,9,10], "4, 9")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if \\
                a != 1:
                x = 3
            elif \\
                b != 2:
                y = 5
            else:
                z = 7
            assert z == 7
            """,
            [1,2,4,5,7,9,10], "4, 7")

    def test_pathological_split_if(self):
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if (
                a == 1
                ):
                x = 3
            elif (
                b == 2
                ):
                y = 5
            else:
                z = 7
            assert x == 3
            """,
            [1,2,5,6,9,11,12], "6-11")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if (
                a != 1
                ):
                x = 3
            elif (
                b == 2
                ):
                y = 5
            else:
                z = 7
            assert y == 5
            """,
            [1,2,5,6,9,11,12], "5, 11")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if (
                a != 1
                ):
                x = 3
            elif (
                b != 2
                ):
                y = 5
            else:
                z = 7
            assert z == 7
            """,
            [1,2,5,6,9,11,12], "5, 9")

    def test_absurd_split_if(self):
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a == 1 \\
                :
                x = 3
            elif b == 2 \\
                :
                y = 5
            else:
                z = 7
            assert x == 3
            """,
            [1,2,4,5,7,9,10], "5-9")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a != 1 \\
                :
                x = 3
            elif b == 2 \\
                :
                y = 5
            else:
                z = 7
            assert y == 5
            """,
            [1,2,4,5,7,9,10], "4, 9")
        self.check_coverage("""\
            a = 1; b = 2; c = 3;
            if a != 1 \\
                :
                x = 3
            elif b != 2 \\
                :
                y = 5
            else:
                z = 7
            assert z == 7
            """,
            [1,2,4,5,7,9,10], "4, 7")

    if sys.version_info >= (2, 4):
        # In 2.4 and up, constant if's were compiled away.
        def test_constant_if(self):
            self.check_coverage("""\
                if 1:
                    a = 2
                assert a == 2
                """,
                [2,3], "")

    def test_while(self):
        self.check_coverage("""\
            a = 3; b = 0
            while a:
                b += 1
                a -= 1
            assert a == 0 and b == 3
            """,
            [1,2,3,4,5], "")
        self.check_coverage("""\
            a = 3; b = 0
            while a:
                b += 1
                break
                b = 99
            assert a == 3 and b == 1
            """,
            [1,2,3,4,5,6], "5")

    def test_while_else(self):
        # Take the else branch.
        self.check_coverage("""\
            a = 3; b = 0
            while a:
                b += 1
                a -= 1
            else:
                b = 99
            assert a == 0 and b == 99
            """,
            [1,2,3,4,6,7], "")
        # Don't take the else branch.
        self.check_coverage("""\
            a = 3; b = 0
            while a:
                b += 1
                a -= 1
                break
                b = 123
            else:
                b = 99
            assert a == 2 and b == 1
            """,
            [1,2,3,4,5,6,8,9], "6-8")

    def test_split_while(self):
        self.check_coverage("""\
            a = 3; b = 0
            while \\
                a:
                b += 1
                a -= 1
            assert a == 0 and b == 3
            """,
            [1,2,4,5,6], "")
        self.check_coverage("""\
            a = 3; b = 0
            while (
                a
                ):
                b += 1
                a -= 1
            assert a == 0 and b == 3
            """,
            [1,2,5,6,7], "")

    def test_for(self):
        self.check_coverage("""\
            a = 0
            for i in [1,2,3,4,5]:
                a += i
            assert a == 15
            """,
            [1,2,3,4], "")
        self.check_coverage("""\
            a = 0
            for i in [1,
                2,3,4,
                5]:
                a += i
            assert a == 15
            """,
            [1,2,5,6], "")
        self.check_coverage("""\
            a = 0
            for i in [1,2,3,4,5]:
                a += i
                break
                a = 99
            assert a == 1
            """,
            [1,2,3,4,5,6], "5")

    def test_for_else(self):
        self.check_coverage("""\
            a = 0
            for i in range(5):
                a += i+1
            else:
                a = 99
            assert a == 99
            """,
            [1,2,3,5,6], "")
        self.check_coverage("""\
            a = 0
            for i in range(5):
                a += i+1
                break
                a = 99
            else:
                a = 123
            assert a == 1
            """,
            [1,2,3,4,5,7,8], "5-7")

    def test_split_for(self):
        self.check_coverage("""\
            a = 0
            for \\
                i in [1,2,3,4,5]:
                a += i
            assert a == 15
            """,
            [1,2,4,5], "")
        self.check_coverage("""\
            a = 0
            for \\
                i in [1,
                2,3,4,
                5]:
                a += i
            assert a == 15
            """,
            [1,2,6,7], "")

    def test_try_except(self):
        self.check_coverage("""\
            a = 0
            try:
                a = 1
            except:
                a = 99
            assert a == 1
            """,
            [1,2,3,4,5,6], "4-5")
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except:
                a = 99
            assert a == 99
            """,
            [1,2,3,4,5,6,7], "")
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except ImportError:
                a = 99
            except:
                a = 123
            assert a == 123
            """,
            [1,2,3,4,5,6,7,8,9], "6")
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise IOError("foo")
            except ImportError:
                a = 99
            except IOError:
                a = 17
            except:
                a = 123
            assert a == 17
            """,
            [1,2,3,4,5,6,7,8,9,10,11], "6, 9-10")
        self.check_coverage("""\
            a = 0
            try:
                a = 1
            except:
                a = 99
            else:
                a = 123
            assert a == 123
            """,
            [1,2,3,4,5,7,8], "4-5")
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except:
                a = 99
            else:
                a = 123
            assert a == 99
            """,
            [1,2,3,4,5,6,8,9], "8")

    def test_try_finally(self):
        self.check_coverage("""\
            a = 0
            try:
                a = 1
            finally:
                a = 99
            assert a == 99
            """,
            [1,2,3,5,6], "")
        self.check_coverage("""\
            a = 0; b = 0
            try:
                a = 1
                try:
                    raise Exception("foo")
                finally:
                    b = 123
            except:
                a = 99
            assert a == 99 and b == 123
            """,
            [1,2,3,4,5,7,8,9,10], "")

    def test_function_def(self):
        self.check_coverage("""\
            a = 99
            def foo():
                ''' docstring
                '''
                return 1

            a = foo()
            assert a == 1
            """,
            [1,2,5,7,8], "")
        self.check_coverage("""\
            def foo(
                a,
                b
                ):
                ''' docstring
                '''
                return a+b

            x = foo(17, 23)
            assert x == 40
            """,
            [1,7,9,10], "")
        self.check_coverage("""\
            def foo(
                a = (lambda x: x*2)(10),
                b = (
                    lambda x:
                        x+1
                    )(1)
                ):
                ''' docstring
                '''
                return a+b

            x = foo()
            assert x == 22
            """,
            [1,10,12,13], "")

    def test_class_def(self):
        self.check_coverage("""\
            # A comment.
            class theClass:
                ''' the docstring.
                    Don't be fooled.
                '''
                def __init__(self):
                    ''' Another docstring. '''
                    self.a = 1

                def foo(self):
                    return self.a

            x = theClass().foo()
            assert x == 1
            """,
            [2,6,8,10,11,13,14], "")


class ExcludeTest(CoverageTest):
    """Tests of the exclusion feature to mark lines as not covered."""

    def test_default(self):
        # A number of forms of pragma comment are accepted.
        self.check_coverage("""\
            a = 1
            b = 2   # pragma: no cover
            c = 3
            d = 4   #pragma NOCOVER
            e = 5
            """,
            [1,3,5]
            )

    def test_simple(self):
        self.check_coverage("""\
            a = 1; b = 2

            if 0:
                a = 4   # -cc
            """,
            [1,3], "", excludes=['-cc'])

    def test_two_excludes(self):
        self.check_coverage("""\
            a = 1; b = 2

            if a == 99:
                a = 4   # -cc
                b = 5
                c = 6   # -xx
            assert a == 1 and b == 2
            """,
            [1,3,5,7], "5", excludes=['-cc', '-xx'])

    def test_excluding_if_suite(self):
        self.check_coverage("""\
            a = 1; b = 2

            if 0:
                a = 4
                b = 5
                c = 6
            assert a == 1 and b == 2
            """,
            [1,7], "", excludes=['if 0:'])

    def test_excluding_if_but_not_else_suite(self):
        self.check_coverage("""\
            a = 1; b = 2

            if 0:
                a = 4
                b = 5
                c = 6
            else:
                a = 8
                b = 9
            assert a == 8 and b == 9
            """,
            [1,8,9,10], "", excludes=['if 0:'])

    def test_excluding_else_suite(self):
        self.check_coverage("""\
            a = 1; b = 2

            if 1==1:
                a = 4
                b = 5
                c = 6
            else:          #pragma: NO COVER
                a = 8
                b = 9
            assert a == 4 and b == 5 and c == 6
            """,
            [1,3,4,5,6,10], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 1; b = 2

            if 1==1:
                a = 4
                b = 5
                c = 6

            # Lots of comments to confuse the else handler.
            # more.

            else:          #pragma: NO COVER

            # Comments here too.

                a = 8
                b = 9
            assert a == 4 and b == 5 and c == 6
            """,
            [1,3,4,5,6,17], "", excludes=['#pragma: NO COVER'])

    def test_excluding_elif_suites(self):
        self.check_coverage("""\
            a = 1; b = 2

            if 1==1:
                a = 4
                b = 5
                c = 6
            elif 1==0:          #pragma: NO COVER
                a = 8
                b = 9
            else:
                a = 11
                b = 12
            assert a == 4 and b == 5 and c == 6
            """,
            [1,3,4,5,6,11,12,13], "11-12", excludes=['#pragma: NO COVER'])

    def test_excluding_oneline_if(self):
        self.check_coverage("""\
            def foo():
                a = 2
                if 0: x = 3     # no cover
                b = 4

            foo()
            """,
            [1,2,4,6], "", excludes=["no cover"])

    def test_excluding_a_colon_not_a_suite(self):
        self.check_coverage("""\
            def foo():
                l = list(range(10))
                a = l[:3]   # no cover
                b = 4

            foo()
            """,
            [1,2,4,6], "", excludes=["no cover"])

    def test_excluding_for_suite(self):
        self.check_coverage("""\
            a = 0
            for i in [1,2,3,4,5]:     #pragma: NO COVER
                a += i
            assert a == 15
            """,
            [1,4], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            for i in [1,
                2,3,4,
                5]:                #pragma: NO COVER
                a += i
            assert a == 15
            """,
            [1,6], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            for i in [1,2,3,4,5
                ]:                        #pragma: NO COVER
                a += i
                break
                a = 99
            assert a == 1
            """,
            [1,7], "", excludes=['#pragma: NO COVER'])

    def test_excluding_for_else(self):
        self.check_coverage("""\
            a = 0
            for i in range(5):
                a += i+1
                break
                a = 99
            else:               #pragma: NO COVER
                a = 123
            assert a == 1
            """,
            [1,2,3,4,5,8], "5", excludes=['#pragma: NO COVER'])

    def test_excluding_while(self):
        self.check_coverage("""\
            a = 3; b = 0
            while a*b:           #pragma: NO COVER
                b += 1
                break
                b = 99
            assert a == 3 and b == 0
            """,
            [1,6], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 3; b = 0
            while (
                a*b
                ):           #pragma: NO COVER
                b += 1
                break
                b = 99
            assert a == 3 and b == 0
            """,
            [1,8], "", excludes=['#pragma: NO COVER'])

    def test_excluding_while_else(self):
        self.check_coverage("""\
            a = 3; b = 0
            while a:
                b += 1
                break
                b = 99
            else:           #pragma: NO COVER
                b = 123
            assert a == 3 and b == 1
            """,
            [1,2,3,4,5,8], "5", excludes=['#pragma: NO COVER'])

    def test_excluding_try_except(self):
        self.check_coverage("""\
            a = 0
            try:
                a = 1
            except:           #pragma: NO COVER
                a = 99
            assert a == 1
            """,
            [1,2,3,6], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except:
                a = 99
            assert a == 99
            """,
            [1,2,3,4,5,6,7], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except ImportError:    #pragma: NO COVER
                a = 99
            except:
                a = 123
            assert a == 123
            """,
            [1,2,3,4,7,8,9], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            try:
                a = 1
            except:       #pragma: NO COVER
                a = 99
            else:
                a = 123
            assert a == 123
            """,
            [1,2,3,7,8], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except:
                a = 99
            else:              #pragma: NO COVER
                a = 123
            assert a == 99
            """,
            [1,2,3,4,5,6,9], "", excludes=['#pragma: NO COVER'])

    def test_excluding_try_except_pass(self):
        self.check_coverage("""\
            a = 0
            try:
                a = 1
            except:           #pragma: NO COVER
                x = 2
            assert a == 1
            """,
            [1,2,3,6], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except ImportError:    #pragma: NO COVER
                x = 2
            except:
                a = 123
            assert a == 123
            """,
            [1,2,3,4,7,8,9], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            try:
                a = 1
            except:       #pragma: NO COVER
                x = 2
            else:
                a = 123
            assert a == 123
            """,
            [1,2,3,7,8], "", excludes=['#pragma: NO COVER'])
        self.check_coverage("""\
            a = 0
            try:
                a = 1
                raise Exception("foo")
            except:
                a = 99
            else:              #pragma: NO COVER
                x = 2
            assert a == 99
            """,
            [1,2,3,4,5,6,9], "", excludes=['#pragma: NO COVER'])

    def test_excluding_if_pass(self):
        # From a comment on the coverage page by Michael McNeil Forbes:
        self.check_coverage("""\
            def f():
                if False:    # pragma: no cover
                    pass     # This line still reported as missing
                if False:    # pragma: no cover
                    x = 1    # Now it is skipped.

            f()
            """,
            [1,7], "", excludes=["no cover"])

    def test_excluding_function(self):
        self.check_coverage("""\
            def fn(foo):      #pragma: NO COVER
                a = 1
                b = 2
                c = 3

            x = 1
            assert x == 1
            """,
            [6,7], "", excludes=['#pragma: NO COVER'])

    def test_excluding_method(self):
        self.check_coverage("""\
            class Fooey:
                def __init__(self):
                    self.a = 1

                def foo(self):     #pragma: NO COVER
                    return self.a

            x = Fooey()
            assert x.a == 1
            """,
            [1,2,3,8,9], "", excludes=['#pragma: NO COVER'])

    def test_excluding_class(self):
        self.check_coverage("""\
            class Fooey:            #pragma: NO COVER
                def __init__(self):
                    self.a = 1

                def foo(self):
                    return self.a

            x = 1
            assert x == 1
            """,
            [8,9], "", excludes=['#pragma: NO COVER'])


if sys.version_info >= (2, 4):
    class Py24Test(CoverageTest):
        """Tests of new syntax in Python 2.4."""

        def test_function_decorators(self):
            self.check_coverage("""\
                def require_int(func):
                    def wrapper(arg):
                        assert isinstance(arg, int)
                        return func(arg)

                    return wrapper

                @require_int
                def p1(arg):
                    return arg*2

                assert p1(10) == 20
                """,
                [1,2,3,4,6,8,10,12], "")

        def test_function_decorators_with_args(self):
            self.check_coverage("""\
                def boost_by(extra):
                    def decorator(func):
                        def wrapper(arg):
                            return extra*func(arg)
                        return wrapper
                    return decorator

                @boost_by(10)
                def boosted(arg):
                    return arg*2

                assert boosted(10) == 200
                """,
                [1,2,3,4,5,6,8,10,12], "")

        def test_double_function_decorators(self):
            self.check_coverage("""\
                def require_int(func):
                    def wrapper(arg):
                        assert isinstance(arg, int)
                        return func(arg)
                    return wrapper

                def boost_by(extra):
                    def decorator(func):
                        def wrapper(arg):
                            return extra*func(arg)
                        return wrapper
                    return decorator

                @require_int
                @boost_by(10)
                def boosted1(arg):
                    return arg*2

                assert boosted1(10) == 200

                @boost_by(10)
                @require_int
                def boosted2(arg):
                    return arg*2

                assert boosted2(10) == 200
                """,
                ([1,2,3,4,5,7,8,9,10,11,12,14,15,17,19,21,22,24,26],
                 [1,2,3,4,5,7,8,9,10,11,12,14,   17,19,21,   24,26]), "")


if sys.version_info >= (2, 5):
    class Py25Test(CoverageTest):
        """Tests of new syntax in Python 2.5."""

        def test_with_statement(self):
            self.check_coverage("""\
                from __future__ import with_statement

                class Managed:
                    def __enter__(self):
                        desc = "enter"

                    def __exit__(self, type, value, tb):
                        desc = "exit"

                m = Managed()
                with m:
                    desc = "block1a"
                    desc = "block1b"

                try:
                    with m:
                        desc = "block2"
                        raise Exception("Boo!")
                except:
                    desc = "caught"
                """,
                [1,3,4,5,7,8,10,11,12,13,15,16,17,18,19,20], "")

        def test_try_except_finally(self):
            self.check_coverage("""\
                a = 0; b = 0
                try:
                    a = 1
                except:
                    a = 99
                finally:
                    b = 2
                assert a == 1 and b == 2
                """,
                [1,2,3,4,5,7,8], "4-5")
            self.check_coverage("""\
                a = 0; b = 0
                try:
                    a = 1
                    raise Exception("foo")
                except:
                    a = 99
                finally:
                    b = 2
                assert a == 99 and b == 2
                """,
                [1,2,3,4,5,6,8,9], "")
            self.check_coverage("""\
                a = 0; b = 0
                try:
                    a = 1
                    raise Exception("foo")
                except ImportError:
                    a = 99
                except:
                    a = 123
                finally:
                    b = 2
                assert a == 123 and b == 2
                """,
                [1,2,3,4,5,6,7,8,10,11], "6")
            self.check_coverage("""\
                a = 0; b = 0
                try:
                    a = 1
                    raise IOError("foo")
                except ImportError:
                    a = 99
                except IOError:
                    a = 17
                except:
                    a = 123
                finally:
                    b = 2
                assert a == 17 and b == 2
                """,
                [1,2,3,4,5,6,7,8,9,10,12,13], "6, 9-10")
            self.check_coverage("""\
                a = 0; b = 0
                try:
                    a = 1
                except:
                    a = 99
                else:
                    a = 123
                finally:
                    b = 2
                assert a == 123 and b == 2
                """,
                [1,2,3,4,5,7,9,10], "4-5")
            self.check_coverage("""\
                a = 0; b = 0
                try:
                    a = 1
                    raise Exception("foo")
                except:
                    a = 99
                else:
                    a = 123
                finally:
                    b = 2
                assert a == 99 and b == 2
                """,
                [1,2,3,4,5,6,8,10,11], "8")


class ModuleTest(CoverageTest):
    """Tests for the module-level behavior of the `coverage` module."""

    def test_not_singleton(self):
        # You *can* create another coverage object.
        coverage.coverage()
        coverage.coverage()


class ReportingTest(CoverageTest):
    """Tests of some reporting behavior."""

    def test_no_data_to_report_on_annotate(self):
        # Reporting with no data produces a nice message and no output dir.
        self.assertRaisesRegexp(
            CoverageException, "No data to report.",
            self.command_line, "annotate -d ann"
            )
        self.assert_doesnt_exist("ann")

    def test_no_data_to_report_on_html(self):
        # Reporting with no data produces a nice message and no output dir.
        self.assertRaisesRegexp(
            CoverageException, "No data to report.",
            self.command_line, "html -d htmlcov"
            )
        self.assert_doesnt_exist("htmlcov")

    def test_no_data_to_report_on_xml(self):
        # Reporting with no data produces a nice message.
        self.assertRaisesRegexp(
            CoverageException, "No data to report.",
            self.command_line, "xml"
            )
        # Currently, this leaves an empty coverage.xml file... :(
