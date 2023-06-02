from utils import to_func_name


def test_to_func_name():
    assert to_func_name("Hello World") == "hello_world"
    assert to_func_name("    space    ") == "space"
    assert to_func_name("123abc") == "_123abc"
    assert to_func_name("MixedCase123") == "mixedcase123"
    assert to_func_name("non-alphanumeric!@#") == "non_alphanumeric"
