from typing import Callable, Any

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code: A string of Python code that returns a result.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""


import inspect
from typing import Callable, Any, Optional

def adapt(code: str) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func_source: Optional[str] = None
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)
            print("\nsource\n"+func_source)
        except (TypeError, OSError):
            # Handle the error if the source code could not be retrieved
            print("Could not retrieve the source code of the function.")
        
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if code == "":
                # If no code is provided, run the decorated function as normal
                return func(*args, **kwargs)
            else:
                local_vars = {
                    "args": args,
                    "kwargs": kwargs,
                    "func_source": func_source,  # make the source code available to the new code
                }
                exec(f"result = {code}", local_vars)
                return local_vars.get("result")

        return wrapper

    return decorator

