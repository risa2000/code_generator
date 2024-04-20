__doc__ = """The module encapsulates C++ code generation logics for main C++ language primitives:
classes, methods and functions, variables, enums.
Every C++ element could render its current state to a string that could be evaluated as
a legal C++ construction.

Some elements could be rendered to a pair of representations (i.e. declaration and definition)

Example:
# Python code
cpp_class = CppClass(name = 'MyClass', is_struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    is_static = True,
    is_const = True,
    value = 255))

// Generated C++ declaration
struct MyClass
{
    static const size_t m_var;
}

// Generated C++ definition
const size_t MyClass::m_var = 255;

You can use CppSourceFile for composing more complicated C++ code,
which is not supported by CppLanguageElement

It supports:

- functional calls:
cpp('int a = 10;')

- 'with' semantic:
with cpp.block('class MyClass', ';')
    class_definition(cpp)

- append code to the last string without EOL:
cpp.append(', p = NULL);')

- empty lines:
cpp.newline(2)

For more detailed information see SourceFile and CppSourceFile documentation.
"""


###########################################################################
# Declaration/Implementation helpers
class CppDeclaration:
    """
    declaration/Implementation pair is used to split one element code generation to
    declaration and implementation parts
    E.g. method declaration
    struct Obj
    {
        int GetItem() const;
    }

    ... and method implementation
    int Obj::GetItem() const {...}

    That could be necessary to use unified render_to_string() interface, that is impossible for
    C++ primitives having two string representations (i.e. declaration and definition)
    """

    def __init__(self, cpp_element):
        self.cpp_element = cpp_element

    def render_to_string(self, cpp):
        self.cpp_element.render_to_string_declaration(cpp)


class CppImplementation:
    """
    See declaration description
    """

    def __init__(self, cpp_element):
        self.cpp_element = cpp_element

    def render_to_string(self, cpp):
        self.cpp_element.render_to_string_implementation(cpp)


class CppLanguageElement:
    """
    The base class for all C++ language elements.
    Contains dynamic storage for element properties
    (e.g. is_static for the variable is_virtual for the class method etc.)
    """

    PROPERTIES = {
        "name",
        "ref_to_parent",
    }

    def __init__(self):
        """
        @param: properties - Basic C++ element properties (name, ref_to_parent)
        class is a parent for method or a member variable
        """
        self.name = None
        self.ref_to_parent = None

    def is_class_member(self):
        """Return True if element is part of another (class/struct/scope) element."""
        return self.ref_to_parent is not None

    def normalize_properties(self, properties):
        """Produce properties with normalized names, i.e. substitute "const" with "is_const"."""
        result = {}
        for name, val in properties.items():
            if name in self.PROPERTIES:
                result[name] = val
            if f"is_{name}" in self.PROPERTIES:
                result[f"is_{name}"] = val
        return result

    def init_properties(self, input_properties_dict, default_property_value=None):
        """
        Set default values for all properties not listed in PROPERTIES
        Set values for all properties that are listed in input_properties_dict
        @param: input_properties_dict - values for the initialized properties (e.g. is_const=True)
        @param: default_property_value - value for properties that are not initialized
        (None by default, because of same as False semantic)
        """
        # Set all properties not listed in PROPERTIES to default_property_value
        defaults = {
            name: default_property_value
            for name in self.PROPERTIES
            if not hasattr(self, name)
        }
        defaults.update(self.normalize_properties(input_properties_dict))
        for name, val in defaults.items():
            setattr(self, name, val)

    def render_to_string(self, cpp):
        """
        @param: cpp - handle that supports code generation interface (see source_file.py)
        Typically it is passed to all child elements so that render their content
        """
        raise NotImplementedError("CppLanguageElement is an abstract class")

    def render_to_string_declaration(self, cpp):
        """
        @param: cpp - handle that supports code generation interface (see source_file.py)
        Typically it is passed to all child elements so that render their content
        """
        raise NotImplementedError("CppLanguageElement is an abstract class")

    def render_to_string_implementation(self, cpp):
        """
        @param: cpp - handle that supports code generation interface (see source_file.py)
        Typically it is passed to all child elements so that render their content
        """
        raise NotImplementedError("CppLanguageElement is an abstract class")

    def parent_qualifier(self):
        """
        Generate string for class name qualifiers
        Should be used for methods implementation and static class members definition.
        Ex.
        void MyClass::MyMethod()
        int MyClass::m_staticVar = 0;

        Supports for nested classes, e.g.
        void MyClass::NestedClass::
        """
        full_parent_qualifier = ""
        parent = self.ref_to_parent
        # walk through all existing parents
        while parent:
            if parent.name is not None:
                full_parent_qualifier = f"{parent.name}::{full_parent_qualifier}"
            parent = parent.ref_to_parent
        return full_parent_qualifier

    def fully_qualified_name(self):
        """
        Generate string for fully qualified name of the element
        Ex.
        MyClass::NestedClass::Method()
        """
        return f"{self.parent_qualifier()}{self.name}"

    def scoped_name(self, local_scope):
        return self.name if local_scope else self.fully_qualified_name()

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
