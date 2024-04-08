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

    def __init__(self, writer, text = None, indent = None, endline = True, postfix = None, code_layout=None):
        """
        @param: owner - SourceFile where text is written to
        @param: text - text opening C++ close
        """
        super().__init__()
        self.writer = writer
        self.code_layout = code_layout or CodeLayout()
        self.indent_level = 0 if indent is None else indent
        if isinstance(text, (list, tuple)):
            self.text = ''.join(text)
        else:
            self.text = text
        self.endline = endline
        self.postfix = postfix is None and self.code_layout.postfix or postfix

    def __call__(self, text, indent=None, endline=True):
        self.line(text, indent=indent, endline=endline)

    def __enter__(self):
        """Open code block."""
        if self.endline:
            self.line(self.text, endline=self.endline)
            self.line("{")
        else:
            text = self.text and f'{self.text} ' or ''
            self.line(f'{text}{{')
        self.indent_level += 1
        return self

    def __exit__(self, *_):
        """Close code block."""
        self.indent_level -= 1
        self.line("}" + self.postfix)

    def line(self, text, indent=None, endline=True):
        """Write one line into writer."""
        if indent is None:
            indent =  self.indent_level
        self.writer.write(
            f"{self.code_layout.indent * indent}"
            f"{text}"
            f"{self.code_layout.endline if endline else ''}"
        )

    def block(self, text, endline=True, postfix=None):
        return ANSICodeFormatter(writer=self.writer, text=text, indent=self.indent_level, endline=endline, postfix=postfix, code_layout=self.code_layout)

    def label(self, text):
        """Write C/C++ code label."""
        self.line(f"{text}:", self.indent_level - 1)

    def newline(self, n=1):
        """
        Insert one or several empty lines
        """
        for _ in range(n):
            self.line(text='', indent=0)


class CodeFormatterFactory:
    """
    Factory class for code formatters
    """

    @staticmethod
    def get_code_formatter(code_format, code_layout=None) -> CodeFormatter:
        """
        Create a new code formatter
        :param code_format: code formatter type
        """
        code_layout = code_layout is not None and code_layout or CodeLayout()
        if code_format == CodeFormat.ANSI_CPP:
            return type('Formatter', (ANSICodeFormatter,), {'code_layout': code_layout})
        elif code_format == CodeFormat.DEFAULT:
            # TODO: leave default formatter for respective source file
            return type('Formatter', (CodeFormatter,), {'code_layout': CodeLayout})
        else:
            raise ValueError(f"Unknown code format: {code_format}")
