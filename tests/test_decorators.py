# Demo code for dynamic metaprogramming decorator
import time
import pytest
import unittest.mock as mock
from unittest.mock import Mock, MagicMock
from generative.decorators import adapt, catch, stack_trace
from .model import gpt4, claude


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


@pytest.fixture
def mock_gpt4_selfheal():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
        def fibonacci(n):
            if n == 0:
                return 0
            elif n == 1:
                return 1
            else:
                return fibonacci(n-1) + fibonacci(n-2)
    """
    return response


@pytest.fixture
def mock_anthropic_check_true():
    response = MagicMock()
    response.__getitem__.return_value = "True"
    return response


@pytest.mark.parametrize("model,critic", [(gpt4, claude)])
def test_selfheal_with_gpt4(
    model, critic, mock_gpt4_selfheal, mock_anthropic_check_true
):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_gpt4_selfheal):
        with mock.patch(
            "anthropic.Client.completion", return_value=mock_anthropic_check_true
        ):

            @adapt(model=model, critic=critic)
            def fibonacci(n):
                if n <= 0:
                    return 0
                elif n == 1:
                    return 1
                else:
                    return fibonacci(n - 1) + fibonacci(n - 2) + 1

            assert fibonacci(8) == 21


@pytest.mark.parametrize("model,critic", [(gpt4, claude)])
def test_adapt_with_gpt(model, critic, mock_gpt4_selfheal, mock_anthropic_check_true):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_gpt4_selfheal):
        with mock.patch(
            "anthropic.Client.completion", return_value=mock_anthropic_check_true
        ):

            @adapt(model=model, critic=critic)
            def func(a, b):
                prompt = """
                Write a complete python 3 function, including the header and
                return statement that computes the N-th Fibonacci number.
                """

            assert func(8) == 21


@pytest.fixture
def mock_is_generative():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
        def func():
            pass
    """
    return response


@pytest.mark.parametrize("model,result", [(gpt4, True), (None, False)])
def test_is_generative(model, result, mock_is_generative):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_is_generative):
        @adapt(model=model)
        def func():
            pass

        assert func._is_generative == result


@pytest.fixture
def mock_gpt4_catch():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
        def add(a, b):
            return a + b
    """
    return response


@pytest.mark.parametrize("model", [gpt4])
def test_catch_with_gpt(model, mock_gpt4_catch):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_gpt4_catch):
        # Define a function that raises an exception
        @catch(model=model)
        def func(a, b):
            raise Exception("Original function exception")

        # Since the original function raises an exception, we expect the LLM
        # to provide an implementation that returns the sum of a and b
        assert func(3, 4) == 7


@pytest.fixture
def mock_gpt4_stack_trace_function():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
tests/test_adapt_decorator.py Traceback (most recent call last):
  File "/Users/justin/Documents/dev/personal/ml/dynamic-mp-llm/meta.py", line 167, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/justin/Documents/dev/personal/ml/dynamic-mp-llm/tests/test_adapt_decorator.py", line 100, in funkodunko
    return items[5]
           ~~~~~^^^
IndexError: list index out of range


Human-readable summary:
(funkodunko) Attempted to access an element of a list that does not exist.

Suggestions for how to fix the error:
1. Check the length of the list to make sure there are enough elements to access the desired index.
2. If the list is too short, add elements to the list in order to access the desired index.
3. If the list is empty, consider initializing the list with data.
    """
    return response


@pytest.mark.parametrize("model", [gpt4])
def test_func_stack_trace_with_gpt(model, mock_gpt4_stack_trace_function):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_gpt4_stack_trace_function):

        @stack_trace(model=model)
        def funkodunko():
            items = [1, 2, 3]
            return items[5]

        try:
            funkodunko()
        except Exception as e:
            # The exception message should be the stack trace, as returned by the LLM.
            assert isinstance(e, Exception)


@pytest.fixture
def mock_gpt4_stack_trace_class():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
Traceback (most recent call last):
  File "/Users/justin/Documents/dev/personal/ml/generative/generative/decorators.py", line 217, in wrapper
    return obj(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^
  File "/Users/justin/Documents/dev/personal/ml/generative/tests/test_decorators.py", line 208, in func
    raise ValueError("Induced exception")
ValueError: Induced exception

```
Human-readable summary:
(func) A ValueError was raised with the message "Induced exception"

Suggestions for how to fix the error:
1. Go to the function 'func' in the file 'test_decorators.py' at line 208.
2. Examine the reason for raising the ValueError with the message "Induced exception". If it's a test case, verify if the exception is expected or not.
3. If the exception is not expected, check the logic in the 'func' function and fix the issue that causes the ValueError.
4. If the exception is expected, make sure it is handled properly in the calling function or the test case, possibly using a try-except block.
5. Rerun the code or test to make sure the error is resolved.
    """
    return response


@pytest.mark.parametrize("model", [gpt4])
def test_class_stack_trace_decorator_with_gpt(model, mock_gpt4_stack_trace_class):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_gpt4_stack_trace_class):
        @stack_trace(model=model)
        class DecoratedClass:
            def func(self):
                raise ValueError("Induced exception")

        try:
            instance = DecoratedClass()
            instance.func()
        except Exception as e:
            assert isinstance(e, Exception)
