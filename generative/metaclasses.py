import textwrap
from typing import Type, Dict, Tuple, Any

from .utils import remove_prepended, extract_func_name


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
        func_name = extract_func_name(code)
        byte_code = compile(code, filename=func_name, mode="exec")
        exec(byte_code, {}, local_vars)
        setattr(cls, func_name, local_vars[func_name])
