import re
import inspect
import textwrap
import traceback
from typing import Callable, Any, Optional, Dict

from RestrictedPython import compile_restricted

from .metaclasses import AbstractDatabase, DatabaseException

from .utils import (
    clean_function,
    remove_prepended,
    extract_func_name,
    format_binary_output,
    is_valid_syntax,
)

from .prompt import (
    format_generative_function,
    format_stack_trace,
    format_semantic_checker,
)

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code  (string, optional): A string of Python code that returns a result.
    model (Callable, optional): LLM to generate code.
    critic (Callable, optional): LLM to review generated code from `model`.
    database (AbstractDatabase, optional): An instance of a class that implements the
                                           AbstractDatabase interface.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""


def adapt(
    code: str = "",
    model: Optional[Callable[[str], str]] = None,
    critic: Optional[Callable[[str], str]] = None,
    database: Optional[AbstractDatabase] = None,
) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal code
        func_source: str = ""
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)
        except (TypeError, OSError):
            code = ""

        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            nonlocal code
            has_cached_code = False
            func_name = extract_func_name(func_source)

            if database:
                query = str(
                    {
                        "function_name": func_name,
                        "args": args,
                        "kwargs": kwargs,
                    }
                )
                has_cached_code = database.contains(query)

                if has_cached_code:
                    code = database.get(query)

            if not has_cached_code and model and func_source:
                is_semantically_correct = False

                # Here, we can access `self` and get all functions of its class
                class_functions = inspect.getmembers(
                    self.__class__, predicate=inspect.isfunction
                )

                # Format the generative function here, inside the wrapper,
                # where you have access to `self`
                prompt = format_generative_function(func_source, class_functions)
                code = clean_function(model(prompt))

                if critic:
                    prompt = format_semantic_checker(code, input="", context="")
                    output = critic(prompt)
                    is_semantically_correct = format_binary_output(output)

                if not is_semantically_correct:
                    return func(self, *args, **kwargs)

            if code.strip() == "":
                return func(self, *args, **kwargs)
            else:
                # TODO: sanitize given function using traditional methods and LLM
                # It's recommended to use RestrictedPython.safe_globals to whitelist
                # the global namespace
                # global_vars = {} allows all global variables to be accessed.
                # However, using RestrictedPython.safe_globals prevents many common functions
                # from being implemented by the LLM.
                global_vars: Dict[str, Any] = {}
                code = remove_prepended(code)
                code = textwrap.dedent(code)

                if not is_valid_syntax(code):
                    raise SyntaxError("Invalid syntax")

                byte_code = compile_restricted(code, mode="exec")
                exec(byte_code, global_vars)

                # TODO: sanitize generated code i.e. generative_func
                func_name = extract_func_name(code)
                generative_func = global_vars[func_name]

                if database:
                    try:
                        capability = {
                            "function_name": func_name,
                            "args": args,
                            "kwargs": kwargs,
                            "generated_code": code,
                        }
                        database.set(capability)
                    except Exception as e:
                        raise DatabaseException(
                            "An error occurred while adding to the database"
                        ) from e

                # TODO: sanitize result
                result = generative_func(self, *args, **kwargs)

                return result

        # Add a special attribute to the wrapper to indicate it has access to a generative model
        wrapper._is_generative = model is not None  # type: ignore[attr-defined]

        return wrapper

    return decorator


"""
The `catch` decorator captures exceptions from the decorated function. An optional Language
Learning Model (LLM) function can be passed to generate replacement code in the event of an
exception.

If the LLM function is absent or its code also raises an exception, the original exception gets
re-raised, allowing for upstream error handling or user notification.

Args:
    model (Callable[[str], str], optional): A function that takes a string of Python code as input
    and returns a string of Python code as output. Typically, this would be a Language Learning
    Model that can generate alternative implementations of the input function.

Returns:
    A function that wraps the original function, catching any exceptions that it raises, and
    optionally replacing its behavior with LLM-generated code in the event of an exception.
"""


def catch(model: Optional[Callable[[str], str]] = None) -> Callable:
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
            except Exception:
                # If there was an exception, and an LLM is provided, use it
                if model and func_source:
                    prompt = format_generative_function(func_source)
                    code = clean_function(model(prompt))

                    if code.strip() != "":
                        global_vars: Dict[str, Any] = {
                            "func_source": func_source,
                        }

                        # TODO: sanitize given function using traditional methods and LLM
                        code = remove_prepended(code)
                        code = textwrap.dedent(code)

                        if not is_valid_syntax(code):
                            raise SyntaxError("Invalid syntax")

                        byte_code = compile_restricted(code, mode="exec")
                        exec(byte_code, global_vars)

                        # TODO: sanitize generated code i.e. generative_func
                        func_name = extract_func_name(code)
                        generative_func: Callable = global_vars[func_name]

                        # TODO: sanitize result
                        result = generative_func(*args, **kwargs)

                        return result

            # If there was an exception, and no LLM is provided, or if the LLM fails, re-raise the
            # original exception
            raise

        # Add a special attribute to the wrapper to indicate it has access to a generative model
        wrapper._is_generative = model is not None  # type: ignore[attr-defined]

        return wrapper

    return decorator


"""
A decorator that intercepts exceptions from a decorated function, feeding the stack trace to an
optional Language Learning Model (LLM). The LLM, if present, crafts a new exception message from
the stack trace, enhancing error reporting or debugging. In the absence of an LLM or if the LLM
fails, the original exception is propagated.

Args:
    model (Callable[[str], str], optional): A function that takes a stack trace as a string
        and returns a string to be used as the message for a new exception.

Returns:
    Callable: A new function that wraps the original one, adding exception handling
        capabilities as described above.
"""


def stack_trace(model: Optional[Callable[[str], str]] = None) -> Callable:
    def decorator(obj: Any) -> Any:
        if inspect.isclass(obj):

            class Wrapper(obj):
                pass

            for attr_name, attr_value in obj.__dict__.items():
                if callable(attr_value):
                    setattr(Wrapper, attr_name, decorator(attr_value))

            return Wrapper

        elif inspect.isfunction(obj):

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return obj(*args, **kwargs)
                except Exception as e:
                    # Capture the stack trace
                    stack_trace = traceback.format_exc()

                    # If an LLM function is provided, pass the stack trace to it
                    if model:
                        prompt = format_stack_trace(stack_trace)
                        summary = textwrap.dedent(model(prompt))
                        new_exception_message = f"{stack_trace}\n{summary}"

                        # Raise a new exception with the modified message
                        raise Exception(new_exception_message) from None
                    else:
                        # If no LLM function is provided, just re-raise the original exception
                        raise e from None

            # Add a special attribute to the wrapper to indicate it has access to a generative model
            wrapper._is_generative = model is not None  # type: ignore[attr-defined]

            return wrapper
        else:
            raise TypeError("Unsupported object type for decoration")

    return decorator
