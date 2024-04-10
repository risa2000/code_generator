__doc__ = """Run following tests:
        python test.cpp.test_cpp_array_writer
        python test.cpp.test_cpp_enum_writer
        python test.cpp.test_cpp_scope_writer
        python test.cpp.test_cpp_class_writer
        python test.cpp.test_cpp_function_writer
        python test.cpp.test_cpp_variable_writer
        python test.cpp.test_cpp_file
"""

import subprocess
import sys


def run_tests(tests):
    for test_file in tests:
        print(f"Running test {test_file}")
        subprocess.run([sys.executable, '-m', f'{test_file}'])


def run_linters():
    linters = ["pylint", "mypy", "flake8"]
    for linter in linters:
        print(f"Running {linter}")
        subprocess.run([linter, "src"])


def run_black():
    print("Running black")
    subprocess.run(["black", "src", "test"])


if __name__ == "__main__":
    command_line_args = sys.argv[1:]
    test_files = [
        "test.cpp.test_cpp_array_writer",
        "test.cpp.test_cpp_enum_writer",
        "test.cpp.test_cpp_scope_writer",
        "test.cpp.test_cpp_class_writer",
        "test.cpp.test_cpp_function_writer",
        "test.cpp.test_cpp_variable_writer",
        "test.cpp.test_cpp_file",
    ]

    if 'black' in command_line_args:
        run_black()

    if 'lint' in command_line_args:
        run_linters()

    run_tests(test_files)
