import pytest
from .model import gpt3, gpt4, claude
from generative.prompt import format_semantic_checker
from generative.utils import format_binary_output


@pytest.mark.skip(reason="Unstable")
def test_is_semantically_correct_with_gpt4():
    code = """
    def add(a, b):
        return sum([a, b])
    """
    input = {"a": 1, "b": 2}
    prompt = format_semantic_checker(code, input, context="")
    output = gpt4(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
def test_is_semantically_correct_with_gpt3():
    code = """
    def add(a, b):
        return sum([a, b])
    """
    input = {"a": 1, "b": 2}
    prompt = format_semantic_checker(code, input, context="")
    output = gpt3(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
def test_is_semantically_correct_with_claude():
    code = """
    def add(a, b):
        return sum([a, b])
    """
    input = {"a": 1, "b": 2}
    prompt = format_semantic_checker(code, input, context="")
    output = claude(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
def test_incorrect_factorial_with_gpt4():
    code = """
    def factorial(n):
        if n == 0:
            return 1
        else:
            return n - factorial(n-1)
    """
    input = "5"
    prompt = format_semantic_checker(code, input, context="")
    output = gpt4(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_factorial_with_gpt3():
    code = """
    def factorial(n):
        if n == 0:
            return 1
        else:
            return n - factorial(n-1)
    """
    input = "5"
    prompt = format_semantic_checker(code, input, context="")
    output = gpt3(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_factorial_with_claude():
    code = """
    def factorial(n):
        if n == 0:
            return 1
        else:
            return n - factorial(n-1)
    """
    input = "5"
    prompt = format_semantic_checker(code, input, context="")
    output = claude(prompt)
    print(f"output: {output}")
    output = format_binary_output(output)
    print(f"formatted: {output}")

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_valueerror_with_gpt4():
    code = """
    try:
        x = 5 / 0
    except ValueError:
        x = 0
    """
    prompt = format_semantic_checker(code, input, context="")
    output = gpt4(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_valueerror_with_gpt3():
    code = """
    try:
        x = 5 / 0
    except ValueError:
        x = 0
    """
    prompt = format_semantic_checker(code, input, context="")
    output = gpt3(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_valueerror_with_claude():
    code = """
    try:
        x = 5 / 0
    except ValueError:
        x = 0
    """
    prompt = format_semantic_checker(code, input, context="")
    output = claude(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_zerodivisionerror_with_gpt4():
    code = """
    try:
        x = 5 / 0
    except ZeroDivisionError:
        x = 0
    print(x)
    """

    prompt = format_semantic_checker(code, input, context="")
    output = gpt4(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
def test_incorrect_zerodivisionerror_with_gpt3():
    code = """
    try:
        x = 5 / 0
    except ZeroDivisionError:
        x = 0
    print(x)
    """

    prompt = format_semantic_checker(code, input, context="")
    output = gpt3(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
def test_incorrect_zerodivisionerror_with_claude():
    code = """
    try:
        x = 5 / 0
    except ZeroDivisionError:
        x = 0
    print(x)
    """

    prompt = format_semantic_checker(code, input, context="")
    output = claude(prompt)
    output = format_binary_output(output)

    assert output


@pytest.mark.skip(reason="Unstable")
def test_incorrect_io_with_gpt4():
    code = """
    with open('somefile.txt', 'r') as f:
        f.write('some text')
    """

    prompt = format_semantic_checker(code, input, context="")
    output = gpt4(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_io_with_gpt3():
    code = """
    with open('somefile.txt', 'r') as f:
        f.write('some text')
    """

    prompt = format_semantic_checker(code, input, context="")
    output = gpt3(prompt)
    output = format_binary_output(output)

    assert output == False


@pytest.mark.skip(reason="Unstable")
def test_incorrect_io_with_claude():
    code = """
    with open('somefile.txt', 'r') as f:
        f.write('some text')
    """

    prompt = format_semantic_checker(code, input, context="")
    output = claude(prompt)
    output = format_binary_output(output)

    assert output == False
