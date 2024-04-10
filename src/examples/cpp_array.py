from code_gen.cpp import CppSourceFile, CppArray

__doc__ = """Example of generating C++ array

Expected output:
int my_array[5] = {1, 2, 0};

"""

cpp = CppSourceFile("array.cpp")

arr = CppArray(name="my_array", type="int", array_size=5)
arr.add_array_items(["1", "2", "0"])
arr.render_to_string(cpp)

arr2 = CppArray(name="my_array_2", type="int", array_size=5, newline_align=True)
arr2.add_array_items(["1", "2", "0"])
arr2.render_to_string(cpp)
