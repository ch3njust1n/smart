import textwrap
from typing import Any, List, Tuple
from . import rules

"""
Prompt for generating entire functions

Args:
    code    (string): Source code fo function to be appended to prompt.
    context (list):   List of tuples of available functions.

Returns:
    Prompt for generating a function.
"""


def format_generative_function(code: str, context: List[Tuple[str, str]] = []) -> str:
    return textwrap.dedent(
        f"""
    The given source code is potentially broken.
    Please rewrite the function using the available functions.

    {rules.CODE_GENERATION_RULES}

    For example, only do this:
    ```
    ### BEGIN FUNCTION ###
    def func():
    \t# function body
    ### END FUNCTION ###
    ```
    and do not do this:
    ```
    ### BEGIN FUNCTION ###
    def func():
    \t# function body
    ### END FUNCTION ###
    return func()
    ```

    You can only use avaiable functions to generate code.
    The functions are given in a list of tuples.
    The first element is the function name.
    The second element is the function source.
    Available functions: {context}

    Source code:
    {code}
    """
    )


"""
Prompt for generating entire functions

Args:
    code    (string): Source code fo function to be appended to prompt.
    kwargs  (Any): Parameters of function to be generated.
    context (list, optional): List of tuples of available functions.

Returns:
    Prompt for generating a function.
"""


def format_generative_function_from_input(
    text: str, kwargs: Any, context: List[Tuple[str, str]] = []
) -> str:
    kwargs = str(kwargs)
    return textwrap.dedent(
        f"""
    {rules.CODE_GENERATION_RULES}

    For example, only do this:
    ```
    ### BEGIN FUNCTION ###
    def func():
    \t# function body
    ### END FUNCTION ###
    ```
    and do not do this:
    ```
    ### BEGIN FUNCTION ###
    def func():
    \t# function body
    ### END FUNCTION ###
    return func()
    ```

    You can only use avaiable functions to generate code.
    The functions are given in a list of tuples.
    The first element is the function name.
    The second element is the function source.
    Available functions: {context}

    Generate a function name: {text} that takes the following parameters: {kwargs}
    """
    )


"""
Prompt for summarizing as human-readable stack traces

Args:
    text (string): Stack trace to be appended to prompt.

Returns:
    Prompt for summarizing a stack trace.
"""


def format_stack_trace(text: str) -> str:
    return textwrap.dedent(
        f"""
    Explain the following stack trace.
    Make suggestions for how to fix the error.
    Given the name of the function where the exception occurred.
    <function name> is the function name of where the error occurred.
    <function name> is not the function called wrapper.
    <function name> is not a file name e.g. ending with .py.
    Format the stack trace as follows:
    ```
    Human-readable summary:
    (<function name>) <explanation of concretely what went wrong>

    Suggestions for how to fix the error:
    <numbered list with steps to fix the error>
    \n
    ```

    Stack trace:
    {text}
    """
    )


"""
Prompt for checking semantic correctness of code.

Args:
    code  (string): Stack trace to be appended to prompt.
    input (Any, optional): Input to the function.
    context (string, optional): Context of the codebase.

Returns:
    Prompt for semantically checking generated code.
"""


def format_semantic_checker(code: str, input: Any = "", context: str = "") -> str:
    return textwrap.dedent(
        f"""
    You are a python interpreter that can execute pseudocode.
    Execute the following pseudocode and return the output only!
    Do not explain the code.
    Do not explain the output.
    Consider if the function name matches the functionality.
    Run the code in your mind and determine if it semantically makes sense.
    Just execute the pseudo code and return the output.

    def is_semantically_correct(code: str, input: Any='', context: str='') -> bool:
        purpose_of_code = summarize_purpose_of_code_and_find_bugs(code, context)
        if input == '':
            return True (code, purpose_of_code) is semantically correct else False
        elif context == '':
            return True (code, input) is semantically correct else False
        elif input == '' and context == '':
            return True (code) is semantically correct else False
        else:
            return True (code, input, purpose_of_code) is semantically correct else False

    is_semantically_correct('{code}', '{str(input)}', '{context}') # return True or False
    """
    )
