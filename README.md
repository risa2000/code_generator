# Pythonic C/C++ Code Generator

Using a simple abstract Python interface allows generating source code for
basic C/C++ constructs:
* variables
* enums
* arrays
* functions
* classes (structs)

**Note about the source:** This repository is a fork of a more featured project
https://github.com/yuchdev/code_generator, which targets also *HTML* and *Java*
generation. I am neither using nor knowing each one enough to keep their
development on par with C/C++ code base, so I deliberately dropped both here.

## Installation

**Note about the installation:** Running `pip install code_generation` will install the original package from the source mentioned above. For installing this version you may need to run `pip` while referencing the local source tree.
```shell
pip install [options] [-e] <local project path> ...
```

## C/C++

C/C++ generator tries to follow the classic declaration vs definition dichotomy
in C/C++ and allows explicit targeting of one or the other.

### Creating variables

#### Python code
```python
from code_generation.cpp import CppSourceFile, CppVariable

cpp = CppSourceFile('example.cpp')
cpp('int i = 0;')

x_variable = CppVariable(name='x', type='int const&', static=True, constexpr=True, value='42')
x_variable.render_to_string(cpp)

name_variable = CppVariable(name='name', type='char*', extern=True)
name_variable.render_to_string(cpp)

cpp.close())
```

#### Generated C++ code
```c++
int i = 0;
static constexpr int const& x = 42;
extern char* name;
```

### Creating functions

#### Python code
```python
from code_generation.cpp import CppSourceFile, CppFunction

def handle_to_factorial(cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')

cpp = CppSourceFile('example.cpp')

factorial_function = CppFunction(name='factorial',
    ret_type='int',
    is_constexpr=True,
    implementation=handle_to_factorial,
    documentation='/// Calculates and returns the factorial of \p n.')

factorial_function.add_argument('int n')
factorial_function.render_to_string(cpp)

cpp.close())
```

#### Generated C++ code
```c++
/// Calculates and returns the factorial of \p n.
constexpr int factorial(int n) {
    return n < 1 ? 1 : (n * factorial(n - 1));
}

```

### Creating classes and structures

#### Python code
```python
from code_generation.cpp import CppSourceFile

cpp = CppSourceFile('example.cpp')

with cpp.block('class A', postfix=';') as block:
    block.label('public')
    block('int m_classMember1;')
    block('double m_classMember2;')

cpp.close()
```

#### Generated C++ code
```c++
class A
{
public:
    int m_classMember1;
    double m_classMember2;
};
```

### Rendering `CppClass` objects to C++ declaration and implementation

#### Python code

```python
from code_generation.cpp import CppSourceFile, CppClass, CppVariable

cpp = CppSourceFile('example.cpp')
header = CppSourceFile('example.h')

cpp_class = CppClass(name = 'MyClass', struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    static = True,
    const = True,
    value = 255))

cpp_class.render_to_string_declaration(header)
cpp_class.render_to_string_implementation(cpp)

cpp.close()
header.close())
```
 
#### Generated C++ declaration

```c++
struct MyClass
{
    static const size_t m_var;
};
```
 
#### Generated C++ implementation
```c++
static const size_t MyClass::m_var = 255;
```

### Implementation Notes

#### CppSourcešFile

Module `code_generation.cpp` provides the tools for C/C++ code generating and
formatting functionality.
 
The Python code typically starts with `CppSourceFile` instance (`cpp`), which
is passed around as a target for different language objects, by calling
`render_to_string(cpp)` Python method.

`CppSourceFile` instance `cpp` can be also used for composing an arbitrary C++
code using following semantics:

- functional call:
```python
cpp('int a = 10;')
```
 
- context manager `with` semantic:
```python
with cpp.block('class MyClass', ';') as block
    class_definition(block)
```
 
- empty lines:
```python
cpp.newline(2)
```

#### ANSICodeFormatter

Class `ANSICodeFormatter` together with `CodeLayout` is responsible for code
formatting and can be reimplemented to customize the formatting style.
 
## Maintenance

### Executing unit tests
The following command will execute the unit tests.

```bash
python ./run_tests.py
```

### Acknowledgements

This is a fork of the broader project
https://github.com/yuchdev/code_generator, which has been reduced to only
support C/C++ (for simplicity and the fact that I do not use and know both HTML
and Java enough to maintain their respective implementation).
