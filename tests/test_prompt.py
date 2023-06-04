from model import gpt3, gpt4, claude
from prompt import format_semantic_checker
from utils import format_binary_output


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
