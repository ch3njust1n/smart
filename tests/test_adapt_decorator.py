# Demo code for dynamic metaprogramming decorator
import time
import pytest
from meta import adapt, catch
from model import llm


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
    retry_count = 3
    retry_delay = 5

    for _ in range(retry_count):
        try:

            @adapt(llm=llm)
            def func(a, b):
                prompt = """
                Write a complete python 3 function, including the header and
                return statement that computes the N-th Fibonacci number.
                """

            assert func(8) == 21
            break
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)


def test_catch():
    retry_count = 3
    retry_delay = 5

    for _ in range(retry_count):
        try:
            # Define a function that raises an exception
            @catch(llm=llm)
            def func(a, b):
                raise Exception("Original function exception")

            # Since the original function raises an exception, we expect the LLM
            # to provide an implementation that returns the sum of a and b
            assert func(3, 4) == 7
            break
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)


def test_stack_trace():
    retry_count = 3
    retry_delay = 5

    for _ in range(retry_count):
        try:
            @stack_trace(llm=llm)
            def func():
                raise ValueError("Original exception")

            try:
                func()
            except Exception as e:
                # The exception message should be the stack trace, as returned by the LLM.
                assert isinstance(e, ValueError)
                break
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)