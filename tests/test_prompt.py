import pytest
import unittest.mock as mock
from unittest.mock import MagicMock
from .model import Claude
from generative.prompt import format_semantic_checker
from generative.utils import format_binary_output


@pytest.fixture
def mock_anthropic_check_true():
    response = MagicMock()
    response.__getitem__.return_value = "True"
    return response


@pytest.fixture
def mock_anthropic_check_false():
    response = MagicMock()
    response.__getitem__.return_value = "False"
    return response


def test_is_semantically_correct(mock_anthropic_check_true):
    claude = Claude()
    mock_anthropic = MagicMock()
    mock_anthropic.completions.create.return_value = mock_anthropic_check_true

    with mock.patch("anthropic.Anthropic", return_value=mock_anthropic):
        with mock.patch.object(claude, "generate", return_value="True"):
            code = """
            def add(a, b):
                return sum([a, b])
            """

            input = {"a": 1, "b": 2}
            prompt = format_semantic_checker(code, input, context="")
            output = claude.generate(prompt)
            output = format_binary_output(output)

            assert output


def test_incorrect_factorial(mock_anthropic_check_false):
    claude = Claude()
    mock_anthropic = MagicMock()
    mock_anthropic.completions.create.return_value = mock_anthropic_check_false
    with mock.patch("anthropic.Anthropic", return_value=mock_anthropic):
        with mock.patch.object(claude, "generate", return_value="False"):
            code = """
            def factorial(n):
                if n == 0:
                    return 1
                else:
                    return n - factorial(n-1)
            """
            input = "5"
            prompt = format_semantic_checker(code, input, context="")
            output = claude.generate(prompt)
            output = format_binary_output(output)

            assert output == False


def test_incorrect_valueerror(mock_anthropic_check_false):
    claude = Claude()
    mock_anthropic = MagicMock()
    mock_anthropic.completions.create.return_value = mock_anthropic_check_false
    with mock.patch("anthropic.Anthropic", return_value=mock_anthropic):
        with mock.patch.object(claude, "generate", return_value="False"):
            code = """
            try:
                x = 5 / 0
            except ValueError:
                x = 0
            """

            claude = Claude()
            prompt = format_semantic_checker(code, input, context="")
            output = claude.generate(prompt)
            output = format_binary_output(output)

            assert output == False


def test_incorrect_zerodivisionerror(mock_anthropic_check_true):
    claude = Claude()
    mock_anthropic = MagicMock()
    mock_anthropic.completions.create.return_value = mock_anthropic_check_true
    with mock.patch("anthropic.Anthropic", return_value=mock_anthropic):
        with mock.patch.object(claude, "generate", return_value="False"):
            code = """
            try:
                x = 5 / 0
            except ZeroDivisionError:
                x = 0
            """

            claude = Claude()
            prompt = format_semantic_checker(code, input, context="")
            output = claude.generate(prompt)
            output = format_binary_output(output)

            assert output


def test_incorrect_io_with(mock_anthropic_check_false):
    claude = Claude()
    mock_anthropic = MagicMock()
    mock_anthropic.completions.create.return_value = mock_anthropic_check_false
    with mock.patch("anthropic.Anthropic", return_value=mock_anthropic):
        with mock.patch.object(claude, "generate", return_value="False"):
            code = """
            with open('somefile.txt', 'r') as f:
                f.write('some text')
            """

            claude = Claude()
            prompt = format_semantic_checker(code, input, context="")
            output = claude.generate(prompt)
            output = format_binary_output(output)

            assert output == False
