import inspect
import textwrap
from typing import Callable, Any, Optional, Type

from .utils import (
    clean_function,
    to_func_name,
    is_incomplete_code,
    is_valid_syntax,
)

from .metaclasses import AbstractDatabase, DatabaseException
from .prompt import format_generative_function_from_input

"""
A decorator that allows for dynamic generation and execution of class attributes.

This decorator takes a function (model) that generates Python code in response to a prompt.
When an attempt is made to access an attribute that doesn't exist on an instance of the decorated
class, the decorator calls the provided model function to generate Python code. The decorator then
compiles and executes this code to define a new function. The newly defined function is immediately
invoked and its result is returned as the value of the attribute.

This new attribute is also added to the instance of the decorated class, so on subsequent attempts
to access it, the attribute exists and the saved value is returned without the need for regenerating
and re-executing the function.

Note: The generated function does not accept any arguments, as it's called immediately upon being
defined.

Args:
    model: A function that takes a string prompt and returns a string of Python code.
    database: An instance of a class that implements the AbstractDatabase interface.

Returns:
    A class decorator that can be used to decorate a class, with the added capability of dynamically
    generating and executing new attributes.

Raises:
    SyntaxError: If the generated code is not valid Python code.
"""


def generate_attribute(
    model: Optional[Callable[[str], str]],
    database: Optional[AbstractDatabase] = None,
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
                        func_name = to_func_name(name)
                        has_cached_code = ""

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
                                return database.get(query)

                        # If model is specified and callable, use it to generate the output string
                        if not has_cached_code and model is not None:
                            # This will return a list of tuples where the first item is the name of
                            # the method and the second item is the method itself. If you only want
                            # the names, you can do:
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

                            prompt = format_generative_function_from_input(
                                func_name, kwargs, context=available_funcs
                            )
                            func_source = clean_function(model(prompt))

                            if not is_valid_syntax(func_source):
                                raise SyntaxError("Invalid syntax")

                            if is_incomplete_code(func_source):
                                raise exception

                            if database:
                                try:
                                    capability = {
                                        "function_name": func_name,
                                        "args": args,
                                        "kwargs": kwargs,
                                        "generated_code": func_source,
                                    }
                                    database.set(capability)
                                except Exception as e:
                                    raise DatabaseException(
                                        "An error occurred while adding to the database"
                                    ) from e

                            return func_source
                        else:
                            raise exception

                    return method_not_found

        return Wrapper

    return decorator
