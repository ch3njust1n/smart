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


"""
The `catch` decorator captures exceptions from the decorated function. An optional Language Learning Model (LLM) 
function can be passed to generate replacement code in the event of an exception. 

If the LLM function is absent or its code also raises an exception, the original exception gets re-raised, allowing 
for upstream error handling or user notification.

Args:
    llm (Callable[[str], str], optional): A function that takes a string of Python code as input and returns a 
    string of Python code as output. Typically, this would be a Language Learning Model that can generate 
    alternative implementations of the input function.

Returns:
    A function that wraps the original function, catching any exceptions that it raises, and optionally replacing 
    its behavior with LLM-generated code in the event of an exception.
"""


def catch(llm: Optional[Callable[[str], str]] = None) -> Callable:
    def extract_func_name(code: str) -> str:
        match = re.search(r"def\s+(\w+)", code)
        if match:
            return match.group(1)
        else:
            raise ValueError("No function definition found in provided code.")

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func_source: Optional[str] = None
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)
        except (TypeError, OSError):
            pass

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Execute the original function first
                return func(*args, **kwargs)
            except Exception as e:
                print(f"An exception occurred in the original function: {e}")
                # If there was an exception, and an LLM is provided, use it
                if llm and func_source:
                    code = llm(func_source)

                    if code.strip() != "":
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

            # If there was an exception, and no LLM is provided, or if the LLM fails, re-raise the original exception
            raise

        return wrapper

    return decorator
