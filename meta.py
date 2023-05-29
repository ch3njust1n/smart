from typing import Callable, Any

"""
A decorator that replaces the behavior of the decorated function with arbitrary code.

Args:
    code    (string): A string of Python code that returns a result.
    use_llm (boolean): True to use a LLM to generate code, False otherwise.

Returns:
    A function that wraps the original function, replacing its behavior with the provided code.
"""

import os
import inspect
from typing import Callable, Any, Optional

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def adapt(code: str, use_llm: bool = False) -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal code
        func_source: Optional[str] = None
        try:
            # Get the source code of the function
            func_source = inspect.getsource(func)
            if use_llm:
                llm_code = openai.Completion.create(
                    model=os.getenv("MODEL"),
                    prompt=f"source\n{func_source}",
                    temperature=os.getenv("TEMPERATURE"),
                )
                code = llm_code.choices[0].text
            
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
                
                # TODO: santize given function using traditional methods and LLM
                exec(f"result = {code}", local_vars)
                # TODO: sanitize result
                return local_vars.get("result")

        return wrapper

    return decorator
