import re
import inspect
import textwrap
import traceback
from typing import Callable, Any, Optional, Type

from RestrictedPython import compile_restricted

from .utils import (
    remove_prepended,
    extract_func_name,
    to_func_name,
    is_incomplete_code,
    format_binary_output,
)

from .prompt import (
    format_generative_function,
    format_stack_trace,
    format_generative_function_from_input,
    format_semantic_checker,
)

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code  (string, optional): A string of Python code that returns a result.
    model (Callable, optional): LLM to generate code.
    critic (Callable, optional): LLM to review generated code from `model`.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""


def adapt(
    code: str = "",
    model: Optional[Callable[[str], str]] = None,
    critic: Optional[Callable[[str], str]] = None,
) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal code
        func_source: Optional[str] = None
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)
        except (TypeError, OSError):
            code = ""

        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            nonlocal code

            # Here, we can access `self` and get all functions of its class
            class_functions = inspect.getmembers(
                self.__class__, predicate=inspect.isfunction
            )

            is_semantically_correct = False

            if model:
                # Format the generative function here, inside the wrapper, where you have access to `self`
                prompt = format_generative_function(func_source, class_functions)
                code = model(prompt)

                if critic:
                    prompt = format_semantic_checker(code, input="", context="")
                    output = critic(prompt)
                    is_semantically_correct = format_binary_output(output)

            if code.strip() == "" or (critic and not is_semantically_correct):
                return func(self, *args, **kwargs)
            else:
                # TODO: sanitize given function using traditional methods and LLM
                # It's recommended to use RestrictedPython.safe_globals to whitelist the global namespace
                # global_vars = {} allows all global variables to be accessed.
                # However, using RestrictedPython.safe_globals prevents many common functions from being implemented by the LLM.
                global_vars = {}
                code = remove_prepended(code)
                code = textwrap.dedent(code)
                byte_code = compile_restricted(code, mode="exec")
                exec(byte_code, global_vars)

                # TODO: sanitize generated code i.e. generative_func
                func_name = extract_func_name(code)
                generative_func = global_vars[func_name]

                # TODO: sanitize result
                result = generative_func(self, *args, **kwargs)

                return result

        # Add a special attribute to the wrapper to indicate it has access to a generative model
        wrapper._is_generative = model != None

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

        # Add a special attribute to the wrapper to indicate it has access to a generative model
        wrapper._is_generative = model != None

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

            # Add a special attribute to the wrapper to indicate it has access to a generative model
            wrapper._is_generative = model != None

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


def generate_attribute(
    model: Optional[Callable[[str], str]]
) -> Callable[[Type[Any]], Type[Any]]:
    def decorator(cls: Type[Any]) -> Type[Any]:
        class Wrapper(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if model:
                    self._is_generative = True

            def __getattribute__(self, name: str) -> Any:
                try:
                    # Try to get attribute normally
                    return super().__getattribute__(name)
                except AttributeError as e:
                    exception = e

                    def method_not_found(*args, **kwargs):
                        # If model is specified and callable, use it to generate the output string
                        if model is not None:
                            # This will return a list of tuples where the first item is the name of the method
                            # and the second item is the method itself. If you only want the names, you can do:
                            all_methods = inspect.getmembers(
                                cls, predicate=inspect.isfunction
                            )
                            available_funcs = [
                                (
                                    method[0],
                                    textwrap.dedent(inspect.getsource(method[1])),
                                )
                                for method in all_methods
                            ]

                            func_name = to_func_name(name)
                            prompt = format_generative_function_from_input(
                                func_name, kwargs, context=available_funcs
                            )
                            func_source = model(prompt)
                            print(f"Model function generated:\n{func_source}")

                            if is_incomplete_code(func_source):
                                raise exception

                            return func_source
                        else:
                            raise e

                    return method_not_found

        return Wrapper

    return decorator
