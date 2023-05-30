# Demo code for dynamic metaprogramming decorator
import pytest
from meta import adapt, setup_openai


@pytest.fixture(autouse=True)
def setup_global_variable():
    setup_openai()


def test_add():
    a = """
    def add(a, b):
        return sum([a, b])
    """

    @adapt(a)
    def add(a, b):
        return a + b

    assert add(3, 4) == 7, "Test failed: Expected 7"


def test_multiply():
    b = ""

    @adapt(b)
    def multiply(a, b):
        return a * b

    assert multiply(3, 4) == 12, "Test failed: Expected 12"


def test_self_healing():
    func = """
     def fibonacci(n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fibonacci(n-1) + fibonacci(n-2)
    """

    @adapt(func)
    def broken_fibonacci(n):
        return n

    assert broken_fibonacci(8) == 21


def test_llm():
    @adapt(use_llm=True)
    def func(a, b):
        prompt="""
        Write a complete python 3 function, including the header and
        return statement that computes the N-th Fibonacci number.
        Do not write a driver program, do not comment, do not explain. 
        Do not write any code outside of the function body.
        Do not call the function or return a reference to it.
        For example, only do this:
        ```
        def func():
        # function body
        ```
        and do not do this:
        ```
        def func():
        # function body
        return func()
        ```
        Only return the function header and body!
        """

    assert func(8) == 21
