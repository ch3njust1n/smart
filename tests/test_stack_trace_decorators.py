# Demo code for dynamic metaprogramming decorator
import pytest
import unittest.mock as mock
from unittest.mock import Mock
from generative.decorators import stack_trace
from .model import gpt4

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
    with mock.patch(
        "openai.ChatCompletion.create", return_value=mock_gpt4_stack_trace_function
    ):

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
    with mock.patch(
        "openai.ChatCompletion.create", return_value=mock_gpt4_stack_trace_class
    ):

        @stack_trace(model=model)
        class DecoratedClass:
            def func(self):
                raise ValueError("Induced exception")

        try:
            instance = DecoratedClass()
            instance.func()
        except Exception as e:
            assert isinstance(e, Exception)
