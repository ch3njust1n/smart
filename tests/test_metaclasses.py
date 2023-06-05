import sys
import pytest
import unittest.mock as mock
from unittest.mock import Mock
from io import StringIO

from .metaclasses.demo import Car, Doggo
from .model import gpt4
from generative.metaclasses import GenerativeMetaClass
from generative.prompt import format_generative_function


def test_traditional_metaclass():
    honk_code = """
def honk(self, times=1):
    for i in range(times):
        print(f'{i} - Beep beep!')
"""
    GenerativeMetaClass.generate(Car, honk_code)
    my_car = Car()
    backup = sys.stdout  # Backup original standard output
    sys.stdout = StringIO()  # Redirect standard output
    my_car.honk(3)
    output = sys.stdout.getvalue()  # Get redirected output
    sys.stdout.close()
    sys.stdout = backup  # Restore original standard output
    assert output == "0 - Beep beep!\n1 - Beep beep!\n2 - Beep beep!\n"


@pytest.fixture
def mock_gpt4_metaclass():
    response = Mock()
    response.choices = [Mock()]
    response.choices[
        0
    ].message.content = """
    def do_trick(self):
        return "*sit*"
    """
    return response


def test_generative_metaclass_with_gpt(mock_gpt4_metaclass):
    with mock.patch("openai.ChatCompletion.create", return_value=mock_gpt4_metaclass):
        prompt = "Write a function with the header `def do_trick(self)` that returns a string '*sit*'"
        prompt = format_generative_function(prompt)
        new_trick = gpt4(prompt)
        GenerativeMetaClass.generate(Doggo, new_trick)
        a_good_boy = Doggo("Chewy")
        assert a_good_boy.do_trick() == "*sit*"
        a_good_boy.set_treat("roast beef")
        assert a_good_boy.stomach == "roast beef"
