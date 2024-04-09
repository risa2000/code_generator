from code_generation.core.code_formatter import CodeFormat, CodeFormatterFactory

__doc__ = """
Simple and straightforward code generator that could be used for generating code
on any programming language and to be a 'building block' for creating more complicated
code generators.

Examples of usage:

1.
# Python code
cpp = SourceFile('example.cpp')
cpp('int i = 0;')

// Generated C++ code
int i = 0;

2.
# Python code
cpp = CppSourceFile('example.cpp')
with cpp.block('class A', ';'):
    cpp.label('public')
    cpp('int m_classMember1;')
    cpp('double m_classMember2;')

// Generated C++ code
class A
{
public:
    int m_classMember1;
    double m_classMember2;
};
"""


class SourceFile:
    """
    The class is a main instrument of code generation

    It can generate plain strings using functional calls
    Ex:
    code = SourceFile(python_src_file)
    code('import os, sys')

    Is supports 'with' semantic for indentation blocks creation
    Ex:
    # Python code
    with code('for i in range(0, 5):'):
        code('lst.append(i*i)')
        code('print(lst)')

    # Generated code:
    for i in range(0, 5):
        lst.append(i*i)
        print(lst)

    It can append code without line ending:
    Ex.
    # Python code
    cpp = SourceFile('ex.cpp')
    cpp('class Derived')
    cpp.append(' : public Base')

    // Generated C++ code
    class Derived : public Base

    And finally, it can insert a number of empty lines
    cpp.newline(3)
    """

    def __init__(self, filename, formatter=None, writer=None):
        """
        Creates a new source file
        @param: filename source file to create (rewrite if exists)
        @param: formatter code formatter to define rules of code indentation and line ending
        @param: writer optional writer to write output to
        """
        self.filename = filename
        if not isinstance(formatter, CodeFormat) and formatter is not None:
            raise TypeError(f"code_format must be an instance of {CodeFormat.__name__}")
        self.formatter = formatter if formatter is not None else CodeFormat.DEFAULT
        self.out = writer if writer is not None else open(filename, "w")
        self.code_formatter = CodeFormatterFactory.get_code_formatter(self.formatter)

    def close(self):
        """
        File created, just close the handle
        """
        self.out.close()
        self.out = None

    def write(self, text, indent=0, endline=True):
        """
        Write a new line with line ending
        """
        self.code_formatter(self.out).line(text, indent, endline)

    def __call__(self, text, indent=0, endline=True):
        """
        Supports 'object()' semantic, i.e.
        cpp('#include <iostream>')
        inserts appropriate line
        """
        self.write(text, indent, endline)

    def block(self, text, endline=True, postfix=None):
        """
        Returns a stub for C++ {} close
        Supports 'with' semantic, i.e.
        with cpp.block(class_name, ';'):
        """
        if postfix is None:
            postfix = self.code_formatter.code_layout.postfix
        return self.code_formatter(
            self.out, text=text, endline=endline, postfix=postfix
        )

    def newline(self, n=1):
        """
        Insert one or several empty lines
        """
        for _ in range(n):
            self.write(text="", indent=0)
