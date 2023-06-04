import textwrap
from typing import Type

from .utils import remove_prepended, extract_func_name


class GenerativeMetaClass(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.is_generative = False

    @staticmethod
    def generate(cls: Type["GenerativeMetaClass"], code: str):
        cls.is_generative = True
        local_vars = {}

        code = remove_prepended(code)
        code = textwrap.dedent(code)
        func_name = extract_func_name(code)
        byte_code = compile(code, filename=func_name, mode="exec")
        exec(byte_code, {}, local_vars)
        setattr(cls, func_name, local_vars[func_name])
