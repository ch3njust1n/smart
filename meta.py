from typing import Callable, Any

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code: A string of Python code that returns a result.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""
def adapt(code: str) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if code == "":
                # If no code is provided, run the decorated function as normal
                return func(*args, **kwargs)
            else:
                local_vars = {
                    "args": args,
                    "kwargs": kwargs,
                }
                exec(f"result = {code}", local_vars)
                return local_vars.get("result")

        return wrapper

    return decorator
