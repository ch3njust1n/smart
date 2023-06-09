# Demo code for dynamic metaprogramming decorator
import pytest
import unittest.mock as mock
from unittest.mock import Mock
from generative.functions import catch
from .model import GPT4


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


@pytest.mark.parametrize("model", [GPT4])
def test_catch_with_gpt(model, mock_gpt4_catch):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_gpt4_catch):
        # Define a function that raises an exception
        @catch(model=model)
        def func(a, b):
            raise Exception("Original function exception")

        # Since the original function raises an exception, we expect the LLM
        # to provide an implementation that returns the sum of a and b
        assert func(3, 4) == 7
