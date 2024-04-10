import unittest
import io
from textwrap import dedent

from code_gen.cpp import CppSourceFile, CppFunction

__doc__ = """
Unit tests for C++ code generator
"""


def handle_to_factorial(cpp):
    cpp("return n < 1 ? 1 : (n * factorial(n - 1));")


class TestCppFunctionStringIo(unittest.TestCase):
    """
    Test C++ function generation by writing to StringIO
    """

    def test_simple_case(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        func = CppFunction(
            name="factorial", ret_type="int", implementation=handle_to_factorial
        )
        func.add_argument("int n")
        func.render_to_string(cpp)
        self.assertIn(
            dedent(
                """\
            int factorial(int n) {
                return n < 1 ? 1 : (n * factorial(n - 1));
            }"""
            ),
            writer.getvalue(),
        )

    def test_is_constexpr_no_implementation_raises(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int", is_constexpr=True)
        self.assertRaises(ValueError, func.render_to_string, cpp)

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        func = CppFunction(
            name="factorial",
            ret_type="int",
            implementation=handle_to_factorial,
            is_constexpr=True,
        )
        func.add_argument("int n")
        func.render_to_string(cpp)
        self.assertIn(
            dedent(
                """\
            constexpr int factorial(int n) {
                return n < 1 ? 1 : (n * factorial(n - 1));
            }"""
            ),
            writer.getvalue(),
        )

    def test_is_constexpr_render_to_string_declaration(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        func = CppFunction(
            name="factorial",
            ret_type="int",
            implementation=handle_to_factorial,
            is_constexpr=True,
        )
        func.add_argument("int n")
        func.render_to_string_declaration(cpp)
        self.assertIn(
            dedent(
                """\
            constexpr int factorial(int n) {
                return n < 1 ? 1 : (n * factorial(n - 1));
            }"""
            ),
            writer.getvalue(),
        )

    def test_docstring_example(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        factorial_function = CppFunction(
            name="factorial",
            ret_type="int",
            is_constexpr=True,
            implementation=handle_to_factorial,
            documentation="/// Calculates and returns the factorial of p @n.",
        )
        factorial_function.add_argument("int n")
        factorial_function.render_to_string(cpp)
        self.assertIn(
            dedent(
                """\
            /// Calculates and returns the factorial of p @n.
            constexpr int factorial(int n) {
                return n < 1 ? 1 : (n * factorial(n - 1));
            }"""
            ),
            writer.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
