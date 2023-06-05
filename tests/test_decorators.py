# Demo code for dynamic metaprogramming decorator
import time
import pytest
from generative.decorators import adapt, catch, stack_trace
from .model import gpt3, gpt4, claude


@pytest.mark.parametrize(
    "code",
    [
        "",
        """
    def add(a, b):
        return sum([a, b])
    """,
    ],
)
def test_add(code):
    @adapt(code)
    def add(a, b):
        return a + b

    assert add(3, 4) == 7, "Test failed: Expected 7"


def test_self_healing_no_llm():
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


@pytest.mark.parametrize("model,critic", [(gpt4, claude), (claude, gpt3)])
def test_self_healing_with_llm(model, critic):
    retry_count = 3
    retry_delay = 5

    for _ in range(retry_count):
        try:

            @adapt(model=model, critic=critic)
            def fibonacci(n):
                if n <= 0:
                    return 0
                elif n == 1:
                    return 1
                else:
                    return fibonacci(n - 1) + fibonacci(n - 2) + 1

            assert fibonacci(8) == 21
            break
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)


@pytest.mark.parametrize("model,critic", [(gpt4, claude), (claude, gpt3)])
def test_adapt_with_gpt(model, critic):
    retry_count = 3
    retry_delay = 5

    for _ in range(retry_count):
        try:

            @adapt(model=model, critic=critic)
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


@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_catch_with_gpt(model):
    retry_count = 3
    retry_delay = 5

    for _ in range(retry_count):
        try:
            # Define a function that raises an exception
            @catch(model=model)
            def func(a, b):
                raise Exception("Original function exception")

            # Since the original function raises an exception, we expect the LLM
            # to provide an implementation that returns the sum of a and b
            assert func(3, 4) == 7
            break
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)


@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_func_stack_trace_with_gpt(model):
    retry_count = 5
    retry_delay = 5

    for _ in range(retry_count):
        try:

            @stack_trace(model=model)
            def funkodunko():
                items = [1, 2, 3]
                return items[5]

            try:
                funkodunko()
            except Exception as e:
                # The exception message should be the stack trace, as returned by the LLM.
                assert isinstance(e, Exception)
                break
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)


@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_class_stack_trace_decorator_with_gpt(model):
    @stack_trace(model=model)
    class DecoratedClass:
        def func(self):
            raise ValueError("Induced exception")

    retry_count = 5
    retry_delay = 5

    for _ in range(retry_count):
        try:
            try:
                instance = DecoratedClass()
                instance.func()
            except Exception as e:
                assert isinstance(e, Exception)
                break
        except Exception as e:
            print(f"Test error: {e}. Retrying after delay...")
            time.sleep(retry_delay)


@pytest.mark.parametrize("model,result", [(claude, True), (None, False)])
def test_is_generative(model, result):
    @adapt(model=model)
    def func():
        pass

    assert func._is_generative == result
