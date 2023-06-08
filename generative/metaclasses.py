import textwrap
from typing import Type, Dict, Tuple, Any

from .utils import (
    extract_func_name,
    is_valid_syntax,
    remove_prepended,
)


class BaseMetaClass(type):
    is_generative: bool = False


class GenerativeMetaClass(BaseMetaClass):
    def __init__(
        cls: Type[Any],
        name: str,
        bases: Tuple[Type[Any], ...],
        attrs: Dict[str, Any],
    ) -> None:
        cls.is_generative = False  # type: ignore

    @staticmethod
    def generate(cls: Type[Any], code: str) -> None:
        cls.is_generative = True  # type: ignore
        local_vars: Dict[str, Any] = {}

        code = remove_prepended(code)
        code = textwrap.dedent(code)

        if not is_valid_syntax(code):
            raise SyntaxError("Invalid syntax")

        func_name = extract_func_name(code)
        byte_code = compile(code, filename=func_name, mode="exec")
        exec(byte_code, {}, local_vars)
        setattr(cls, func_name, local_vars[func_name])
