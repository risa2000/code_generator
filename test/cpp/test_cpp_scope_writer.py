import unittest
import io
from textwrap import dedent

from code_generation.cpp import (
    CppSourceFile,
    CppVariable,
    CppClassScope,
    CppClass,
)
from test.comparing_tools import normalize_code, debug_dump, is_debug

__doc__ = """Unit tests for C++ code generator"""


class TestCppScopeStringIo(unittest.TestCase):
    """
    Test C++ class generation by writing to StringIO
    """

    def test_simple_case(self):
        writer = io.StringIO()
        cpp_file = CppSourceFile(None, writer=writer)

        # Create a CppClass instance
        cpp_scope = CppClassScope(scope="private")

        # Add a CppVariable to the class
        cpp_scope.add_variable(
            CppVariable(
                name="m_var", type="size_t", static=True, const=True, value="255"
            )
        )

        # Define a function body for the CppMethod
        def body(cpp):
            cpp("return m_var;")

        # Add a CppMethod to the class
        cpp_scope.add_method(
            CppClass.CppMethod(
                name="GetVar", ret_type="size_t", static=True, implementation=body
            )
        )

        # Render the class to string
        with cpp_file.block(postfix="", braces=False) as block:
            cpp_scope.render_to_string(block)

        # Define the expected output
        expected_output = dedent(
            """\
            private:
                static size_t GetVar();
                static const size_t m_var;

                static const size_t m_var = 255;

                size_t GetVar()
                {
                    return m_var;
                }"""
        )

        # Assert the output matches the expected output
        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "cpp")
        self.assertEqual(expected_output_normalized, actual_output_normalized)

    def test_with_nested_scopes(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)

        # Create a CppClass instance
        cpp_class = CppClass(name="MyClass")

        # Create a nested scope
        nested_scope = CppClassScope(scope="private")

        # Create a CppClass instance
        nested_class = CppClass(name="NestedClass")
        nested_scope.add_internal_class(nested_class)

        # Add nested scope to the class
        cpp_class.add_internal_scope(nested_scope)

        # Render the main class to string
        cpp_class.render_to_string(cpp)

        # Define the expected output
        expected_output = dedent(
            """\
            class MyClass
            {
            private:
                class NestedClass
                {
                };
            };"""
        )

        actual_output = writer.getvalue().strip()
        expected_output_normalized = normalize_code(expected_output)
        actual_output_normalized = normalize_code(actual_output)
        if is_debug():
            debug_dump(expected_output_normalized, actual_output_normalized, "cpp")
        self.assertEqual(expected_output_normalized, actual_output_normalized)


if __name__ == "__main__":
    unittest.main()
