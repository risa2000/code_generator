import unittest
import io
from textwrap import dedent

from code_gen.cpp import CppSourceFile, CppArray, CppClass
from test.comparing_tools import normalize_lines

__doc__ = """Unit tests for C++ code generator
"""


class TestCppArrayStringIo(unittest.TestCase):
    """
    Test C++ array generation by writing to StringIO
    """

    def test_simple_case(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        arr = CppArray(name="my_array", type="int", array_size=5)
        arr.add_array_items(["1", "2", "0"])
        arr.render_to_string(cpp)
        expected_output = "int my_array[5] = {1, 2, 0};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_with_newline_align(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        arr = CppArray(name="my_array", type="int", array_size=5, newline_align=True)
        arr.add_array_items(["1", "2", "0"])
        arr.render_to_string(cpp)
        generated_output = writer.getvalue().strip()
        expected_output = dedent(
            """int my_array[5] = {
                1,
                2,
                0
            };"""
        )
        expected_output_normalized = normalize_lines(expected_output)
        generated_output_normalized = normalize_lines(generated_output)
        self.assertEqual(expected_output_normalized, generated_output_normalized)

    def test_declaration(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        cls = CppClass(name="Cls")
        arr = CppArray(
            name="my_class_member_array",
            type="int",
            array_size=None,
        )
        cls.add_array(arr)
        arr.render_to_string_declaration(cpp)
        expected_output = "int my_class_member_array[];"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_implementation(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        cls = CppClass(name="Cls")
        arr = CppArray(
            name="m_my_static_array",
            type="int",
            array_size=None,
            is_static=True,
        )
        cls.add_array(arr)
        arr.add_array_items(["1", "2", "0"])
        arr.render_to_string_implementation(cpp)
        expected_output = "static int Cls::m_my_static_array[] = {1, 2, 0};"
        self.assertEqual(expected_output, writer.getvalue().strip())

    def test_missing_type(self):
        arr = CppArray(name="my_array", array_size=5)
        self.assertRaises(RuntimeError, arr.render_to_string, None)

    def test_missing_name(self):
        arr = CppArray(type="int", array_size=5)
        self.assertRaises(RuntimeError, arr.render_to_string, None)

    def test_class_member_missing_name(self):
        arr = CppArray(type="int")
        self.assertRaises(RuntimeError, arr.render_to_string_declaration, None)

    def test_class_member_static_without_name(self):
        arr = CppArray(type="int", is_static=True)
        self.assertRaises(RuntimeError, arr.render_to_string_implementation, None)


if __name__ == "__main__":
    unittest.main()
