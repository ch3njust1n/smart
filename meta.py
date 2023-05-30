import os
import re
import inspect
import textwrap
from dotenv import load_dotenv
from typing import Callable, Any, Optional

import openai
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals
from prompt import format_generative_function


def setup_openai():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if openai.api_key is None:
        raise ValueError(
            "The OPENAI_API_KEY environment variable is not set. Please provide your OpenAI API key."
        )

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code    (string, optional): A string of Python code that returns a result.
    use_llm (boolean, optional): True to use a LLM to generate code, False otherwise.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""

def adapt(code: str = "", use_llm: bool = False) -> Callable:
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

            if use_llm:
                llm_code = openai.Completion.create(
                    model=os.getenv("MODEL"),
                    prompt=format_generative_function(func_source),
                    temperature=float(os.getenv("TEMPERATURE", 0.7)),
                    max_tokens=int(os.getenv("MAX_TOKENS", 3600)),
                )
                code = llm_code.choices[0].text

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

                func_name = extract_func_name(code)

                # TODO: santize given function using traditional methods and LLM
                code = textwrap.dedent(code)
                byte_code = compile_restricted(code, '<inline>', 'exec')
                exec(byte_code, global_vars)

                # TODO: sanitize generated code i.e. generative_func
                generative_func = global_vars[func_name]

                # TODO: sanitize result
                result = generative_func(*args, **kwargs)

                return result

        return wrapper

    return decorator
