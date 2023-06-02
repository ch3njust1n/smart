import os
import re
import inspect
import textwrap
import traceback
from typing import Callable, Any, Optional, Type

from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals

from utils import remove_prepended, extract_func_name, to_func_name
from prompt import (
    format_generative_function,
    format_stack_trace,
    format_generative_function_from_input,
)

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code  (string, optional): A string of Python code that returns a result.
    model (Callable, optional): LLM to generate code.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""


def adapt(code: str = "", model: Optional[Callable[[str], str]] = None) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal code
        func_source: Optional[str] = None
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)

            if model:
                prompt = format_generative_function(func_source)
                code = model(prompt)

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
    model (Callable[[str], str], optional): A function that takes a string of Python code as input and returns a 
    string of Python code as output. Typically, this would be a Language Learning Model that can generate 
    alternative implementations of the input function.

Returns:
    A function that wraps the original function, catching any exceptions that it raises, and optionally replacing 
    its behavior with LLM-generated code in the event of an exception.
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
            except Exception as e:
                print(f"An exception occurred in the original function: {e}")
                # If there was an exception, and an LLM is provided, use it
                if model and func_source:
                    prompt = format_generative_function(func_source)
                    code = model(prompt)

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
    model (Callable[[str], str], optional): A function that takes a stack trace as a string 
        and returns a string to be used as the message for a new exception.

Returns:
    Callable: A new function that wraps the original one, adding exception handling 
        capabilities as described above.
"""


def stack_trace(model: Optional[Callable[[str], str]] = None) -> Callable:
    def decorator(obj: Any) -> Any:
        if isinstance(obj, Type):

            class Wrapper(obj):
                pass

            for attr_name, attr_value in obj.__dict__.items():
                if callable(attr_value):
                    setattr(Wrapper, attr_name, decorator(attr_value))

            return Wrapper

        elif callable(obj):

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
                        print(new_exception_message)

                        # Raise a new exception with the modified message
                        raise Exception(new_exception_message) from None
                    else:
                        # If no LLM function is provided, just re-raise the original exception
                        raise e from None

            return wrapper
        else:
            raise TypeError("Unsupported object type for decoration")

    return decorator


"""
A decorator that allows for dynamic generation and execution of class attributes.

This decorator takes a function (model) that generates Python code in response to a prompt.
When an attempt is made to access an attribute that doesn't exist on an instance of the decorated class, 
the decorator calls the provided model function to generate Python code. The decorator then compiles 
and executes this code to define a new function. The newly defined function is immediately invoked
and its result is returned as the value of the attribute. 

This new attribute is also added to the instance of the decorated class, so on subsequent attempts 
to access it, the attribute exists and the saved value is returned without the need for regenerating 
and re-executing the function. 

Note: The generated function does not accept any arguments, as it's called immediately upon being defined. 

Args:
    model: A function that takes a string prompt and returns a string of Python code.

Returns:
    A class decorator that can be used to decorate a class, with the added capability of dynamically 
    generating and executing new attributes.
"""

from typing import Optional, Callable, Type, Any

def generate_attribute(model: Optional[Callable[[str], str]]) -> Callable[[Type[Any]], Type[Any]]:
    def decorator(cls: Type[Any]) -> Type[Any]:
        class Wrapper(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def __getattribute__(self, name: str) -> Any:
                try:
                    # Try to get attribute normally
                    return super().__getattribute__(name)
                except AttributeError as e:
                    def method_not_found(*args, **kwargs):
                        # If model is specified and callable, use it to generate the output string
                        if model is not None:
                            func_name = to_func_name(name)
                            prompt = format_generative_function_from_input(func_name, kwargs)
                            func_source = model(prompt)
                            print(f"Model function generated:\n{func_source}")
                            return func_source
                        else:
                            # If no model is specified, return a default string
                            return "Default string"

                    return method_not_found
        return Wrapper
    return decorator



# def generate_attribute(
#     model: Optional[Callable[[str], str]]
# ) -> Callable[[Type[Any]], Type[Any]]:
#     def decorator(cls: Any) -> Any:
#         class Wrapper:
#             def __init__(self, *args, **kwargs):
#                 self.wrapped = cls(*args, **kwargs)

#             def __getattribute__(self, name: str) -> Any:
#                 attr = super(Wrapper, self).__getattribute__(name)

#                 # If this attribute is callable (i.e., it's a method), we need to catch parameters
#                 print(f"Trying to get attribute '{name}': {callable(attr)} {attr}")
#                 if callable(attr):
#                     def newfunc(*args, **kwargs):
#                         print(f'Calling function "{name}" with positional arguments {args} and keyword arguments {kwargs}')

#                         try:
#                             return attr(*args, **kwargs)
#                         except AttributeError as e:
#                             print(f"AttributeError caught for attribute '{name}'")
#                             if model is not None:
#                                 missing_attribute = str(e).split()[-1][1:-1]
#                                 print(f'Attribute "{missing_attribute}" not found. Generating...')
#                                 func_name = to_func_name(missing_attribute)
#                                 print(f'Generating function "{func_name}"...')
#                                 prompt = format_generative_function_from_input(func_name)
#                                 func_source = model(prompt)
#                                 print(f'Generated function source:\n{func_source}')
#                                 global_vars = {}
#                                 byte_code = compile(func_source, "<string>", "exec")
#                                 exec(byte_code, global_vars)

#                                 try:
#                                     generated_func = global_vars[func_name]
#                                     print(f"Generated function '{func_name}':\n{inspect.getsource(generated_func)}")
#                                     # Set the generated function as an attribute of the instance
#                                     setattr(self, func_name, generated_func)
#                                     # Execute and return the result of the generated function
#                                     return generated_func(*args, **kwargs)
#                                 except KeyError:
#                                     raise AttributeError(f"Unable to generate attribute")
#                     return newfunc
#                 else:
#                     # If the attribute is not callable, return it as usual
#                     return attr

#         return Wrapper

#     return decorator


class GenerativeMetaClass(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

    @staticmethod
    def generate(cls: Type["GenerativeMetaClass"], code: str):
        local_dict = {}
        exec(code, {}, local_dict)
        func_name = extract_func_name(code)
        setattr(cls, func_name, local_dict[func_name])
