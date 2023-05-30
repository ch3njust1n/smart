import os
import re
import inspect
import textwrap
from typing import Callable, Any, Optional

from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code (string, optional): A string of Python code that returns a result.
    llm  (Callable, optional): LLM to generate code.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""


def adapt(code: str = "", llm: Optional[Callable[[str], str]] = None) -> Callable:
    def extract_func_name(code: str) -> str:
        match = re.search(r"def\s+(\w+)", code)
        if match:
            return match.group(1)
        else:
            raise ValueError("No function definition found in provided code.")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal code
        func_source: Optional[str] = None
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)

            if llm:
                code = llm(func_source)

        except (TypeError, OSError):
            code = ""

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal code
            if code.strip() == "":
                return func(*args, **kwargs)
            else:
                global_vars = {
                    "func_source": func_source,
                }

                # TODO: sanitize given function using traditional methods and LLM
                code = textwrap.dedent(code)
                byte_code = compile_restricted(code, "<inline>", "exec")
                exec(byte_code, global_vars)

                # TODO: sanitize generated code i.e. generative_func
                func_name = extract_func_name(code)
                generative_func = global_vars[func_name]

                # TODO: sanitize result
                result = generative_func(*args, **kwargs)

                return result

        return wrapper

    return decorator
