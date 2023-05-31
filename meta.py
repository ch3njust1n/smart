import os
import re
import inspect
import textwrap
import traceback
from typing import Callable, Any, Optional, Type

from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals

from utils import remove_prepended, extract_func_name
from prompt import format_generative_function, format_stack_trace

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code (string, optional): A string of Python code that returns a result.
    llm  (Callable, optional): LLM to generate code.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""


def adapt(code: str = "", llm: Optional[Callable[[str], str]] = None) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal code
        func_source: Optional[str] = None
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)

            if llm:
                prompt = format_generative_function(func_source)
                code = llm(prompt)

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
                code = remove_prepended(code)
                code = textwrap.dedent(code)
                byte_code = compile_restricted(code, mode="exec")
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
The `catch` decorator captures exceptions from the decorated function. An optional Language Learning 
Model (LLM) function can be passed to generate replacement code in the event of an exception. 

If the LLM function is absent or its code also raises an exception, the original exception gets re-raised, 
allowing for upstream error handling or user notification.

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
                    prompt = format_generative_function(func_source)
                    code = llm(func_source)

                    if code.strip() != "":
                        global_vars = {
                            "func_source": func_source,
                        }

                        # TODO: sanitize given function using traditional methods and LLM
                        code = remove_prepended(code)
                        code = textwrap.dedent(code)
                        byte_code = compile_restricted(code, mode="exec")
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


"""
A decorator that intercepts exceptions from a decorated function, feeding the stack trace to an 
optional Language Learning Model (LLM). The LLM, if present, crafts a new exception message from 
the stack trace, enhancing error reporting or debugging. In the absence of an LLM or if the LLM fails, 
the original exception is propagated.

Args:
    llm (Callable[[str], str], optional): A function that takes a stack trace as a string 
        and returns a string to be used as the message for a new exception.

Returns:
    Callable: A new function that wraps the original one, adding exception handling 
        capabilities as described above.
"""


def stack_trace(llm: Optional[Callable[[str], str]] = None) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Capture the stack trace
                stack_trace = traceback.format_exc()

                # If an LLM function is provided, pass the stack trace to it
                if llm:
                    prompt = format_stack_trace(stack_trace)
                    summary = textwrap.dedent(llm(prompt))
                    new_exception_message = f"{stack_trace}\n{summary}"
                    print(new_exception_message)

                    # Raise a new exception with the modified message
                    raise Exception(new_exception_message) from None
                else:
                    # If no LLM function is provided, just re-raise the original exception
                    raise e from None

        return wrapper

    return decorator

class GenerativeMetaClass(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

    @staticmethod
    def generate(cls: Type['GenerativeMetaClass'], code: str):
        local_dict = {}
        exec(code, {}, local_dict)
        func_name = extract_func_name(code)
        setattr(cls, func_name, local_dict[func_name])