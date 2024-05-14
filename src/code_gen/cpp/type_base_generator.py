from textwrap import dedent

from .language_element import CppLanguageElement


# noinspection PyUnresolvedReferences
class CppBaseType(CppLanguageElement):
    """
    The Python class that provides the base type used in other elements:
        array, variable, template type
    """

    PROPERTIES = CppLanguageElement.PROPERTIES | {
        "type",
        "is_static",
        "is_extern",
        "is_const",
        "is_constexpr",
        "is_ref",
        "is_integral",
        "documentation",
    }

    def __init__(self, **properties):
        super().__init__()
        self.type = None
        self.is_static = False
        self.is_extern = False
        self.is_const = False
        self.is_constexpr = False
        self.is_ref = False
        self.is_integral = False
        self.documentation = None
        self.init_properties(properties)

    @staticmethod
    def normalize(ctype, **properties):
        """Return new instance of CppBaseType if ctype is str."""
        if isinstance(ctype, str):
            return CppBaseType(type=ctype, **properties)
        return ctype

    def scoped_name(self, local_scope):
        self._sanity_check()
        s_name = CppLanguageElement.resolved_name(self.type, local_scope)
        declarators = [
            f"{self._static()}",
            f"{self._extern()}",
            f"{self._const()}",
            f"{self._constexpr()}",
            f"{s_name}{self._ref()}",
        ]
        return " ".join(d for d in declarators if d)

    def _sanity_check(self):
        """
        @raise: ValueError, if some properties are not valid
        """
        if self.is_const and self.is_constexpr:
            raise ValueError(
                "Type object can be either 'const' or 'constexpr', not both"
            )
        if self.is_static and self.is_extern:
            raise ValueError("Type object can be either 'extern' or 'static', not both")

    def _static(self):
        """
        @return: 'static' prefix, can't be used with 'extern'
        """
        return "static" if self.is_static else ""

    def _extern(self):
        """
        @return: 'extern' prefix, can't be used with 'static'
        """
        return "extern" if self.is_extern else ""

    def _const(self):
        """
        @return: 'const' prefix, can't be used with 'constexpr'
        """
        return "const" if self.is_const else ""

    def _constexpr(self):
        """
        @return: 'constexpr' prefix, can't be used with 'const'
        """
        return "constexpr" if self.is_constexpr else ""

    def _ref(self):
        return "&" if self.is_ref else ""


class CppTemplateType(CppBaseType):
    """Implements an abstraction of a C++ templated type."""

    PROPERTIES = CppBaseType.PROPERTIES | {
        "template_args",
    }

    def __init__(self, **properties):
        super().__init__()
        self.template_args = []
        self.init_properties(properties)

    def scoped_name(self, local_scope):
        self._sanity_check()
        s_name = super().resolved_name(self.type, local_scope)
        t_args_names = []
        for t_arg in self.template_args:
            t_args_names.append(CppLanguageElement.resolved_name(t_arg, local_scope))
        return f'{s_name}<{", ".join(t_args_names)}>'
