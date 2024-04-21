import unittest

from code_gen.cpp import CppBaseType, CppTemplateType, CppClass

__doc__ = """Unit tests for C++ code generator
"""


class TestCppBaseTypeStringIo(unittest.TestCase):
    """
    Test C++ base type generation.
    """

    def test_simple_case(self):
        type = CppBaseType(
            type="char",
            static=False,
            const=True,
        )
        for local_scope in [True, False]:
            s = type.scoped_name(local_scope=local_scope)
            self.assertEqual("const char", s)
        # check the is_ref type flag
        type.is_ref = True
        for local_scope in [True, False]:
            s = type.scoped_name(local_scope=local_scope)
            self.assertEqual("const char&", s)

    def test_is_constexpr_const_raises(self):
        type = CppBaseType(
            type="int",
            const=True,
            constexpr=True,
        )
        for local_scope in [True, False]:
            self.assertRaises(ValueError, type.scoped_name, local_scope)

    def test_is_extern_static_raises(self):
        type = CppBaseType(type="char*", static=True, extern=True)
        for local_scope in [True, False]:
            self.assertRaises(ValueError, type.scoped_name, local_scope)


class TestCppBaseTypeStringIo(unittest.TestCase):
    """
    Test C++ base type generation.
    """

    def test_simple_case(self):
        type1 = CppBaseType(
            type="char",
            static=False,
            const=True,
        )
        templ1 = CppTemplateType(type="std::vector", template_args=[type1])
        for local_scope in [True, False]:
            s = templ1.scoped_name(local_scope)
            self.assertEqual("std::vector<const char>", s)

    def test_multiple_args_case(self):
        type1 = CppBaseType(
            type="char",
            static=False,
            const=True,
        )
        type2 = "bool"
        templ1 = CppTemplateType(type="std::map", template_args=[type1, type2])
        for local_scope in [True, False]:
            s = templ1.scoped_name(local_scope)
            self.assertEqual("std::map<const char, bool>", s)


if __name__ == "__main__":
    unittest.main()
