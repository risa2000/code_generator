from code_generation.cpp.language_element import (
    CppLanguageElement,
    CppDeclaration,
    CppImplementation,
)


# noinspection PyUnresolvedReferences
class CppArray(CppLanguageElement):
    """
    The Python class that generates string representation for C++ array (automatic or class member)
    For example:

    int arr[] = {1,2,2};
    double doubles[5] = {1.0,2.0};

    class MyClass
    {
        int m_arr1[10];
        static double m_arr2[];
        ...
    }
    Available properties:

    type - string, variable type
    (is_)static - boolean, 'static' prefix
    (is_)const - boolean, 'const' prefix
    (is_)class_member - boolean, for appropriate definition/declaration rendering
    array_size - integer, size of array if required
    newline_align - in the array definition rendering place every item on the new string

    NOTE: versions 2.0+ of CodeGenerator support boolean properties without "is_" suffix,
    but old versions preserved for backward compatibility

    NOTE: methods responsible for rendering of any element to string start from 'render_*'
    (e.g. render_value, render_to_string)
    Methods simply returning string representation of the element start from '_'
    """

    PROPERTIES = CppLanguageElement.PROPERTIES | {
        "type",
        "is_static",
        "is_const",
        "is_class_member",
        "array_size",
        "newline_align",
        "items",
    }

    def __init__(self, **properties):
        super().__init__()
        self.type = None
        self.is_static = False
        self.is_const = False
        self.is_class_member = False
        self.array_size = 0
        self.newline_align = False
        # array elements
        self.items = []
        self.init_properties(properties)

    def declaration(self):
        """
        @return: CppDeclaration wrapper, that could be used
        for declaration rendering using render_to_string(cpp) interface
        """
        return CppDeclaration(self)

    def definition(self):
        """
        @return: CppImplementation wrapper, that could be used
        for definition rendering using render_to_string(cpp) interface
        """
        return CppImplementation(self)

    def add_array_item(self, item):
        """
        If variable is an array it could contain a number of items
        @param: item - string
        """
        self.items.append(item)

    def add_array_items(self, items):
        """
        If variable is an array it could contain a number of items
        @param: items - list of strings
        """
        self.items.extend(items)

    def decl_to_string(self):
        lhr = [
            f"{self._modifiers()}",
            f"{self.type}",
            f"{self.name}[{self._size()}]",
        ]
        return " ".join(h for h in lhr if h)

    def full_decl_to_string(self):
        lhr = [
            f"{self._modifiers()}",
            f"{self.type}",
            f"{self.fully_qualified_name()}[{self._size()}]",
        ]
        return " ".join(h for h in lhr if h)

    def render_to_string(self, cpp):
        """
        Generates definition for the C++ array.
        Output depends on the array type

        Generates something like
        int my_array[5] = {1, 2, 0};
        const char* my_array[] = {"Hello", "World"};

        That method is used for generating automatic (non-class members) arrays
        For class members use render_to_string_declaration/render_to_string_implementation methods
        """
        self._sanity_check()
        if self.is_class_member and not (self.is_static and self.is_const):
            raise RuntimeError(
                "For class member variables use definition() and declaration() methods"
            )

        # newline-formatting of array elements makes sense only if array is not empty
        if self.newline_align and self.items:
            with cpp.block(
                f"{self.decl_to_string()} =", endline=False, postfix=";"
            ) as block:
                # render array items
                self._render_value(block)
        else:
            cpp(f"{self.decl_to_string()} = {{{self._content()}}};")

    def render_to_string_declaration(self, cpp):
        """
        Generates declaration for the C++ array.
        Non-static arrays-class members do not supported

        Example:
        static int my_class_member_array[];
        """
        self._sanity_check()
        if not self.is_class_member:
            raise RuntimeError(
                "For automatic variable use its render_to_string() method"
            )
        cpp(f"{self.decl_to_string()};")

    def render_to_string_implementation(self, cpp):
        """
        Generates definition for the C++ array.
        Output depends on the array type

        Example:
        int MyClass::m_my_static_array[] =
        {
            ...
        };

        Non-static arrays-class members do not supported
        """
        self._sanity_check()
        if not self.is_class_member:
            raise RuntimeError(
                "For automatic variable use its render_to_string() method"
            )

        # generate definition for the static class member arrays only
        # other types are not supported
        if not self.is_static:
            raise RuntimeError("Only static arrays as class members are supported")

        # newline-formatting of array elements makes sense only if array is not empty
        if self.newline_align and self.items:
            with cpp.block(
                f"{self.full_decl_to_string()} =", endline=False, postfix=";"
            ) as block:
                # render array items
                self._render_value(block)
        else:
            cpp(f"{self.full_decl_to_string()} = {{{self._content()}}};")

    def _sanity_check(self):
        """
        Check if all required properties are set
        """
        if not self.type:
            raise RuntimeError("Array type is not set")
        if not self.name:
            raise RuntimeError("Array name is not set")
        if self.is_class_member and not self.name:
            raise RuntimeError("Class member array name is not set")

    def _static(self):
        """
        @return: 'static' prefix if required
        """
        return "static" if self.is_static else ""

    def _const(self):
        """
        @return: 'const' prefix if required
        """
        return "const" if self.is_const else ""

    def _modifiers(self):
        modifiers = [
            self._static(),
            self._const(),
        ]
        return " ".join(m for m in modifiers if m)

    def _size(self):
        """
        @return: array size
        """
        return self.array_size if self.array_size else ""

    def _content(self):
        """
        @return: array items if any
        """
        return ", ".join(self.items) if self.items else "nullptr"

    def _render_value(self, cpp):
        """
        Render to string array items
        """
        if not self.items:
            raise RuntimeError("Empty arrays do not supported")
        for item in self.items[:-1]:
            cpp(f"{item},")
        cpp(f"{self.items[-1]}")
