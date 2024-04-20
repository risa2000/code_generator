import unittest
import io

from code_gen.cpp import CppSourceFile, CppVariable, CppClass

__doc__ = """Unit tests for C++ code generator
"""


class TestCppVariableStringIo(unittest.TestCase):
    """
    Test C++ variable generation by writing to StringIO
    """

    def test_simple_case(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        variables = CppVariable(
            name="var1",
            type="char*",
            is_static=False,
            is_const=True,
            value="0",
        )
        variables.render_to_string(cpp)
        self.assertEqual("const char* var1 = 0;\n", writer.getvalue())

    def test_is_constexpr_const_raises(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        var = CppVariable(
            name="COUNT",
            type="int",
            is_const=True,
            is_constexpr=True,
            value="0",
        )
        self.assertRaises(ValueError, var.render_to_string, cpp)

    def test_is_constexpr_no_implementation_raises(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        var = CppVariable(name="COUNT", type="int", is_constexpr=True)
        self.assertRaises(ValueError, var.render_to_string, cpp)

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        variable = CppVariable(
            name="COUNT",
            type="int",
            is_constexpr=True,
            value="0",
        )
        variable.render_to_string(cpp)
        self.assertIn("constexpr int COUNT = 0;", writer.getvalue())

    def test_is_constexpr_render_to_string_declaration(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        cls = CppClass(name="Cls")
        variable = CppVariable(name="COUNT", type="int", is_constexpr=True, value="0")
        cls.add_variable(variable)
        variable.render_to_string_declaration(cpp)
        self.assertIn("constexpr int COUNT = 0;", writer.getvalue())

    def test_is_extern_static_raises(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        var = CppVariable(name="var1", type="char*", is_static=True, is_extern=True)
        self.assertRaises(ValueError, var.render_to_string, cpp)

    def test_is_extern_render_to_string(self):
        writer = io.StringIO()
        cpp = CppSourceFile(None, writer=writer)
        v = CppVariable(name="var1", type="char*", is_extern=True)
        v.render_to_string(cpp)
        self.assertIn("extern char* var1;", writer.getvalue())


if __name__ == "__main__":
    unittest.main()
