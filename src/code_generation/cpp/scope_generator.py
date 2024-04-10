from textwrap import dedent

from .language_element import CppLanguageElement, CppDeclaration, CppImplementation


class CppClassScope(CppLanguageElement):
    """
    An abstract scope which can accommodated different language elements and can be used to define different sections of class or struct.
    """

    PROPERTIES = CppLanguageElement.PROPERTIES | {
        "documentation",
        "scope",
    }

    def __init__(self, **properties):
        super().__init__()
        self.documentation = None
        self.scope = None
        self.init_properties(properties)

        # aggregated classes
        self.internal_class_elements = []

        # class members
        self.variable_members = []

        # array class members
        self.array_members = []

        # class methods
        self.methods = []

        # class scoped enums
        self.scoped_enums = []

        # internal scopes
        self.internal_scopes = []

    # add class members
    def add_enum(self, enum):
        """
        @param: enum CppEnum instance
        """
        enum.ref_to_parent = self
        self.scoped_enums.append(enum)

    def add_variable(self, cpp_variable):
        """
        @param: cpp_variable CppVariable instance
        """
        cpp_variable.ref_to_parent = self
        cpp_variable.is_class_member = True
        self.variable_members.append(cpp_variable)

    def add_array(self, cpp_variable):
        """
        @param: cpp_variable CppVariable instance
        """
        cpp_variable.ref_to_parent = self
        cpp_variable.is_class_member = True
        self.array_members.append(cpp_variable)

    def add_internal_class(self, cpp_class):
        """
        Add nested class
        @param: cpp_class CppClass instance
        """
        cpp_class.ref_to_parent = self
        self.internal_class_elements.append(cpp_class)

    def add_method(self, method):
        """
        @param: method CppFunction instance
        """
        method.ref_to_parent = self
        method.is_method = True
        self.methods.append(method)

    def add_internal_scope(self, cpp_scope):
        """
        Add nested scope
        @param: cpp_scope CppScope instance
        """
        cpp_scope.ref_to_parent = self
        self.internal_scopes.append(cpp_scope)

    # render declaration
    def anything_to_declare_local(self):
        """
        Checks if there is any local element (without nested scopes) which should be declared.
        """
        return any(
            [
                self.internal_class_elements,
                self.scoped_enums,
                self.variable_members,
                self.array_members,
                self.methods,
            ]
        )

    def anything_to_declare(self):
        """
        Checks if there is any element which should be declared.
        """
        return self.internal_scopes or self.anything_to_declare_local()

    def render_internal_classes_declaration(self, cpp):
        """
        Generates section of nested classes
        Could be placed both in 'private:' or 'public:' sections
        Method is protected as it is used by CppClass only
        """
        for class_item in self.internal_class_elements:
            class_item.declaration().render_to_string(cpp)

    def render_enum_declaration(self, cpp):
        """
        Render to string all contained enums
        Method is protected as it is used by CppClass only
        """
        for enum_item in self.scoped_enums:
            enum_item.render_to_string(cpp)

    def render_variables_declaration(self, cpp):
        """
        Render to string all contained variable class members
        Method is protected as it is used by CppClass only
        """
        for var_item in self.variable_members:
            var_item.declaration().render_to_string(cpp)

    def render_array_declaration(self, cpp):
        """
        Render to string all contained array class members
        Method is protected as it is used by CppClass only
        """
        for arr_item in self.array_members:
            arr_item.declaration().render_to_string(cpp)

    def render_methods_declaration(self, cpp):
        """
        Generates all class methods declaration
        Should be placed in 'public:' section
        Method is protected as it is used by CppClass only
        """
        for func_item in self.methods:
            func_item.render_to_string_declaration(cpp)

    def render_internal_scopes_declarations(self, cpp):
        """
        Generates sections of nested scopes (with labels if given)
        """
        for scope_item in self.internal_scopes:
            scope_item.declaration().render_to_string(cpp)

    def render_to_string_declaration(self, cpp):
        """
        Render to string scope declaration.
        """
        if not self.anything_to_declare():
            return

        if self.scope is not None:
            cpp.label(self.scope)

        if self.documentation:
            cpp(dedent(self.documentation))

        self.render_enum_declaration(cpp)
        self.render_internal_classes_declaration(cpp)
        self.render_methods_declaration(cpp)
        self.render_variables_declaration(cpp)
        self.render_array_declaration(cpp)
        self.render_internal_scopes_declarations(cpp)

    # render implementation
    def render_static_members_implementation(self, cpp):
        """
        Generates definition for all static class variables
        Method is public, as it could be used for nested classes
        int MyClass::my_static_array[] = {}
        """
        # generate definition for static variables
        static_vars = [
            variable for variable in self.variable_members if variable.is_static
        ]

        for var_item in static_vars:
            var_item.definition().render_to_string(cpp)

        if self.array_members:
            cpp.newline()

        for arr_item in self.array_members:
            arr_item.definition().render_to_string(cpp)
        cpp.newline()

    def render_methods_implementation(self, cpp):
        # generate methods implementation section
        for func_item in self.methods:
            if not func_item.is_pure_virtual:
                func_item.render_to_string_implementation(cpp)
                cpp.newline()

    def render_internal_classes_implementation(self, cpp):
        # do the same for nested classes
        for class_item in self.internal_class_elements:
            class_item.render_to_string_implementation(cpp)
            cpp.newline()

    def render_internal_scopes_implementation(self, cpp):
        # do the same for nested classes
        for scope_item in self.internal_scopes:
            scope_item.render_to_string_implementation(cpp)
            cpp.newline()

    def render_to_string_implementation(self, cpp):
        """
        Render to string class definition.
        Typically handle to *.cpp file should be passed as 'cpp' param
        """
        self.render_static_members_implementation(cpp)
        self.render_methods_implementation(cpp)
        self.render_internal_classes_implementation(cpp)
        self.render_internal_scopes_implementation(cpp)

    def render_to_string(self, cpp):
        """
        Render to string both declaration and definition.
        A rare case enough, because the only code generator handle is used.
        Typically class declaration is rendered to *.h file, and definition to *.cpp
        """
        self.render_to_string_declaration(cpp)
        self.render_to_string_implementation(cpp)

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
