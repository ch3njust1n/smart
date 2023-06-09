from generative.utils import (
    to_func_name,
    remove_self_param,
)


def test_to_func_name():
    assert to_func_name("Hello World") == "hello_world"
    assert to_func_name("    space    ") == "space"
    assert to_func_name("123abc") == "_123abc"
    assert to_func_name("MixedCase123") == "mixedcase123"
    assert to_func_name("non-alphanumeric!@#") == "non_alphanumeric"


def test_remove_self_param():
    # Test function with 'self' parameter
    func_str = "def my_func(self, arg1, arg2):\n    pass\n"
    expected_str = "def my_func(arg1, arg2):\n    pass\n"
    assert remove_self_param(func_str) == expected_str

    # Test function without 'self' parameter
    func_str = "def my_func(arg1, arg2):\n    pass\n"
    assert remove_self_param(func_str) == func_str

    # Test function with 'self' as part of another parameter name
    func_str = "def my_func(selfish, arg1, arg2):\n    pass\n"
    assert remove_self_param(func_str) == func_str
