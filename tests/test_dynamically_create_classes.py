import time
import pytest
import textwrap
import unittest.mock as mock
from unittest.mock import Mock

from .model import GPT4


def test_generated_class():
    def my_func(self):
        return self.x * 2

    MyClass = type("MyClass", (object,), {"x": 10, "my_func": my_func})
    instance = MyClass()
    assert instance.x == 10
    assert instance.my_func() == 20


def test_generated_stringified_class():
    properties = textwrap.dedent(
        """
    {
        'x': 10,
        'my_func':
            '''def my_func(self):
                return self.x * 2
            '''
    }
    """
    )
    properties = eval(properties)
    global_vars = {}
    func_source = properties["my_func"]
    exec(func_source, global_vars)
    properties["my_func"] = global_vars["my_func"]

    MyClass = type("MyClass", (object,), properties)
    instance = MyClass()

    assert instance.x == 10
    assert instance.my_func() == 20


@pytest.fixture
def mock_gpt4_create_class():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
    {
        'x': 10,
        'my_func':
            '''def my_func(self):
                return self.x * 2
            '''
    }
    """
    return response


def test_generated_stringified_class_with_gpt(mock_gpt4_create_class):
    with mock.patch(
        "openai.ChatCompletion.create", return_value=mock_gpt4_create_class
    ):
        prompt = """
        You are a stochastic parrot that only repeats back JSON.
        Repeat the following JSON back to me:
        ```
        {
            'x': 10,
            'my_func':
                '''def my_func(self):
                    return self.x * 2
                '''
        }
        ```

        Do not explain.
        Do not add any additional information.
        Just repeat the JSON back to me exactly.
        """
        properties = textwrap.dedent(GPT4.generate(prompt))
        properties = eval(properties)
        global_vars = {}
        func_source = properties["my_func"]
        exec(func_source, global_vars)
        properties["my_func"] = global_vars["my_func"]

        MyClass = type("MyClass", (object,), properties)
        instance = MyClass()

        assert instance.x == 10
        assert instance.my_func() == 20
