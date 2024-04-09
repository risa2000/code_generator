from code_generation.core.code_formatter import CodeFormat
from code_generation.core.source_file import SourceFile

__doc__ = """
"""


class CppSourceFile(SourceFile):
    """
    This class extends SourceFile class with some specific C++ constructions
    """

    default_formatter = CodeFormat.ANSI_CPP

    def __init__(self, filename, formatter=None, writer=None):
        """
        Create C++ source file
        """
        formatter = self.default_formatter if formatter is None else formatter
        SourceFile.__init__(self, filename, formatter=formatter, writer=writer)

    def label(self, text):
        """
        Could be used for access specifiers or ANSI C labels, e.g.
        private:
        a:
        """
        self.write(f"{text}:")
