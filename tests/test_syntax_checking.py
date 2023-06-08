from generative.utils import is_valid_syntax

def test_is_code_statement():
    assert is_valid_syntax('print("Hello, world!")')


def is_not_code_statement():
    assert not is_valid_syntax('print("Hello, world!"')


def test_is_code_class():
    code = """
    class Mobile(object):
            def __init__(self):
                pass

            def phone(self):
                pass

            def wifi(self):
                pass
    """
    assert is_valid_syntax(code)


def test_is_code_class():
    code = """
    class Mobile(object
            def __init__(self):
                pass

            def phone(self):
                pass

            def wifi(self):
                pass
    """
    assert not is_valid_syntax(code)