import pytest
from .model import gpt3, gpt4, claude
from generative.prompt import format_semantic_checker
from generative.utils import format_binary_output


@pytest.mark.skip(reason="Unstable")
@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_is_semantically_correct(model):
    code = """
    def add(a, b):
        return sum([a, b])
    """
    input = {"a": 1, "b": 2}
    prompt = format_semantic_checker(code, input, context="")
    output = model(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_incorrect_factorial(model):
    code = """
    def factorial(n):
        if n == 0:
            return 1
        else:
            return n - factorial(n-1)
    """
    input = "5"
    prompt = format_semantic_checker(code, input, context="")
    output = model(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_incorrect_valueerror(model):
    code = """
    try:
        x = 5 / 0
    except ValueError:
        x = 0
    """
    prompt = format_semantic_checker(code, input, context="")
    output = model(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_incorrect_zerodivisionerror(model):
    code = """
    try:
        x = 5 / 0
    except ZeroDivisionError:
        x = 0
    print(x)
    """

    prompt = format_semantic_checker(code, input, context="")
    output = model(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
@pytest.mark.parametrize("model", [gpt4, gpt3, claude])
def test_incorrect_io_with(model):
    code = """
    with open('somefile.txt', 'r') as f:
        f.write('some text')
    """

    prompt = format_semantic_checker(code, input, context="")
    output = model(prompt)
    output = format_binary_output(output)

    assert output == False
