"""Tests for coverage.templite."""

from coverage.templite import Templite
import unittest

# pylint: disable=W0612,E1101
# Disable W0612 (Unused variable) and
# E1101 (Instance of 'foo' has no 'bar' member)

class AnyOldObject(object):
    """Simple testing object.

    Use keyword arguments in the constructor to set attributes on the object.

    """
    def __init__(self, **attrs):
        for n, v in attrs.items():
            setattr(self, n, v)


class TempliteTest(unittest.TestCase):
    """Tests for Templite."""

    def try_render(self, text, ctx, result):
        """Render `text` through `ctx`, and it had better be `result`."""
        self.assertEqual(Templite(text).render(ctx), result)

    def test_passthrough(self):
        # Strings without variables are passed through unchanged.
        self.assertEqual(Templite("Hello").render(), "Hello")
        self.assertEqual(
            Templite("Hello, 20% fun time!").render(),
            "Hello, 20% fun time!"
            )

    def test_variables(self):
        # Variables use {{var}} syntax.
        self.try_render("Hello, {{name}}!", {'name':'Ned'}, "Hello, Ned!")

    def test_pipes(self):
        # Variables can be filtered with pipes.
        data = {
            'name': 'Ned',
            'upper': lambda x: x.upper(),
            'second': lambda x: x[1],
            }
        self.try_render("Hello, {{name|upper}}!", data, "Hello, NED!")

        # Pipes can be concatenated.
        self.try_render("Hello, {{name|upper|second}}!", data, "Hello, E!")

    def test_reusability(self):
        # A single Templite can be used more than once with different data.
        globs = {
            'upper': lambda x: x.upper(),
            'punct': '!',
            }

        template = Templite("This is {{name|upper}}{{punct}}", globs)
        self.assertEqual(template.render({'name':'Ned'}), "This is NED!")
        self.assertEqual(template.render({'name':'Ben'}), "This is BEN!")

    def test_attribute(self):
        # Variables' attributes can be accessed with dots.
        obj = AnyOldObject(a="Ay")
        self.try_render("{{obj.a}}", locals(), "Ay")

        obj2 = AnyOldObject(obj=obj, b="Bee")
        self.try_render("{{obj2.obj.a}} {{obj2.b}}", locals(), "Ay Bee")

    def test_member_function(self):
        # Variables' member functions can be used, as long as they are nullary.
        class WithMemberFns(AnyOldObject):
            """A class to try out member function access."""
            def ditto(self):
                """Return twice the .txt attribute."""
                return self.txt + self.txt
        obj = WithMemberFns(txt="Once")
        self.try_render("{{obj.ditto}}", locals(), "OnceOnce")

    def test_item_access(self):
        # Variables' items can be used.
        d = {'a':17, 'b':23}
        self.try_render("{{d.a}} < {{d.b}}", locals(), "17 < 23")

    def test_loops(self):
        # Loops work like in Django.
        nums = [1,2,3,4]
        self.try_render(
            "Look: {% for n in nums %}{{n}}, {% endfor %}done.",
            locals(),
            "Look: 1, 2, 3, 4, done."
            )
        # Loop iterables can be filtered.
        def rev(l):
            """Return the reverse of `l`."""
            l = l[:]
            l.reverse()
            return l

        self.try_render(
            "Look: {% for n in nums|rev %}{{n}}, {% endfor %}done.",
            locals(),
            "Look: 4, 3, 2, 1, done."
            )

    def test_empty_loops(self):
        self.try_render(
            "Empty: {% for n in nums %}{{n}}, {% endfor %}done.",
            {'nums':[]},
            "Empty: done."
            )

    def test_multiline_loops(self):
        self.try_render(
            "Look: \n{% for n in nums %}\n{{n}}, \n{% endfor %}done.",
            {'nums':[1,2,3]},
            "Look: \n\n1, \n\n2, \n\n3, \ndone."
            )

    def test_multiple_loops(self):
        self.try_render(
            "{% for n in nums %}{{n}}{% endfor %} and "
                                    "{% for n in nums %}{{n}}{% endfor %}",
            {'nums': [1,2,3]},
            "123 and 123"
            )

    def test_comments(self):
        # Single-line comments work:
        self.try_render(
            "Hello, {# Name goes here: #}{{name}}!",
            {'name':'Ned'}, "Hello, Ned!"
            )
        # and so do multi-line comments:
        self.try_render(
            "Hello, {# Name\ngoes\nhere: #}{{name}}!",
            {'name':'Ned'}, "Hello, Ned!"
            )

    def test_if(self):
        self.try_render(
            "Hi, {% if ned %}NED{% endif %}{% if ben %}BEN{% endif %}!",
            {'ned': 1, 'ben': 0},
            "Hi, NED!"
            )
        self.try_render(
            "Hi, {% if ned %}NED{% endif %}{% if ben %}BEN{% endif %}!",
            {'ned': 0, 'ben': 1},
            "Hi, BEN!"
            )
        self.try_render(
            "Hi, {% if ned %}NED{% if ben %}BEN{% endif %}{% endif %}!",
            {'ned': 0, 'ben': 0},
            "Hi, !"
            )
        self.try_render(
            "Hi, {% if ned %}NED{% if ben %}BEN{% endif %}{% endif %}!",
            {'ned': 1, 'ben': 0},
            "Hi, NED!"
            )
        self.try_render(
            "Hi, {% if ned %}NED{% if ben %}BEN{% endif %}{% endif %}!",
            {'ned': 1, 'ben': 1},
            "Hi, NEDBEN!"
            )

    def test_loop_if(self):
        self.try_render(
            "@{% for n in nums %}{% if n %}Z{% endif %}{{n}}{% endfor %}!",
            {'nums': [0,1,2]},
            "@0Z1Z2!"
            )
        self.try_render(
            "X{%if nums%}@{% for n in nums %}{{n}}{% endfor %}{%endif%}!",
            {'nums': [0,1,2]},
            "X@012!"
            )
        self.try_render(
            "X{%if nums%}@{% for n in nums %}{{n}}{% endfor %}{%endif%}!",
            {'nums': []},
            "X!"
            )

    def test_nested_loops(self):
        self.try_render(
            "@{% for n in nums %}"
                "{% for a in abc %}{{a}}{{n}}{% endfor %}"
            "{% endfor %}!",
            {'nums': [0,1,2], 'abc': ['a', 'b', 'c']},
            "@a0b0c0a1b1c1a2b2c2!"
            )

    def test_exception_during_evaluation(self):
        # TypeError: Couldn't evaluate {{ foo.bar.baz }}:
        # 'NoneType' object is unsubscriptable
        self.assertRaises(TypeError, self.try_render,
            "Hey {{foo.bar.baz}} there", {'foo': None}, "Hey ??? there"
            )

    def test_bogus_tag_syntax(self):
        self.assertRaises(SyntaxError, self.try_render,
            "Huh: {% bogus %}!!{% endbogus %}??", {}, ""
            )
