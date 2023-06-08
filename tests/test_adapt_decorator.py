# Demo code for dynamic metaprogramming decorator
import pytest
import unittest.mock as mock
from unittest.mock import Mock, MagicMock
from generative.functions import adapt
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
