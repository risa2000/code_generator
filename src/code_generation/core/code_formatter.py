from enum import Enum, auto

__doc__ = """Formatters for different styles of code generation
"""


class CodeFormat(Enum):
    DEFAULT = auto()
    ANSI_CPP = auto()


class CodeLayout:
    """
    Class defining code layout rules, such as indentation, line ending, etc.
    """
    default_endline = "\n"
    default_indent = " " * 4
    default_postfix = ""

    def __init__(self, indent=None, endline=None, postfix=None):
        """
        :param indent: sequence of symbols used for indentation (4 spaces, tab, etc.)
        :param endline: symbol used for line ending
        :param postfix: optional line-terminating symbol
        """
        self.indent = self.default_indent if indent is None else indent
        self.endline = self.default_endline if endline is None else endline
        self.postfix = self.default_postfix if postfix is None else postfix


class CodeFormatter:
    """
    Base class for code close of different styles
    """
    pass


class ANSICodeFormatter(CodeFormatter):
    """
    Class represents C++ {} close and its formatting style.
    It supports ANSI C style with braces on the new lines, like that:
    // C++ code
    {
        // C++ code
    };
    finishing postfix is optional (e.g. necessary for classes, unnecessary for namespaces)
    """

    def __init__(self, owner, text, code_layout=None):
        """
        @param: owner - SourceFile where text is written to
        @param: text - text opening C++ close
        """
        super().__init__()
        self.owner = owner
        if self.owner.last is not None:
            with self.owner.last:
                pass
        self.owner.line("".join(text))
        self.owner.last = self

    def line(self, text, indent_level=0, endline=None):
        """
        Write a new line with line ending
        """
        return (
            f"{self.indent * indent_level}"
            f"{text}"
            f"{self.endline if endline is None else endline}"
        )

    def __enter__(self):
        """
        Open code block
        """
        self.owner.line("{")
        self.owner.current_indent += 1
        self.owner.last = None

    def __exit__(self, *_):
        """
        Close code block
        """
        if self.owner.last is not None:
            with self.owner.last:
                pass
        self.owner.current_indent -= 1
        self.owner.line("}" + self.postfix)


class CodeFormatterFactory:
    """
    Factory class for code formatters
    """

    @staticmethod
    def create(code_format, owner, text, *args, **kwargs):
        """
        Create a new code formatter
        :param owner: source file where formatter is created
        :param text: code to format
        :param code_format: code formatter type
        :param args: formatter arguments
        :param kwargs: formatter keyword arguments
        :return: new code formatter
        """
        if code_format == CodeFormat.ANSI_CPP:
            return ANSICodeFormatter(owner=owner, text=text, *args, **kwargs)
        elif code_format == CodeFormat.DEFAULT:
            # TODO: leave default formatter for respective source file
            return CodeFormatter(*args, **kwargs)
        else:
            raise ValueError(f"Unknown code format: {code_format}")
