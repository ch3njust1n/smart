import re
import ast
import textwrap
from typing import Optional

"""
This function takes a string that represents a function.
It parses the string to remove any text that occurs above the function header.

Args:
    func_string (str): A string that represents a function.
    end_marker (str): A string that marks the end of the function header.

Returns:
    A string that represents a function, with any text above the function header removed.
"""


def remove_prepended(func_string: str, end_marker="### END FUNCTION ###") -> str:
    func_match = re.search(r"\s*def .+", func_string)
    if func_match:
        func_string = func_string[func_match.start() :]

    end_marker_index = func_string.find(end_marker)
    if end_marker_index != -1:
        func_string = func_string[: end_marker_index + len(end_marker)]

    return func_string


"""
Remove the 'self' parameter from a function header if it exists.

Args:
    func_str: A string representing a Python function.

Returns:
    A string representing the modified Python function.
"""


def remove_self_param(function_code: str) -> Optional[str]:
    parts = re.split(r"(?<=\()\s*self\b,?\s*", function_code)
    return "".join(parts)


"""
This function takes a string that represents a function.
It formats the function to be valid Python class function.

Args:
    function_code (str): A string that represents a function.

Returns:
    A string that represents a function, with any text above the function header removed.
"""


def clean_function(function_code: str) -> Optional[str]:
    function_code = remove_self_param(function_code)
    function_code = remove_prepended(function_code)
    return textwrap.dedent(function_code)


"""
This function takes a string that represents a function.
It parses the string and returns the function name else raises an error.

Args:
    code (str): A string that represents a function.

Returns:
    A string of the function name.
"""


def extract_func_name(code: str) -> str:
    match = re.search(r"def\s+(\w+)", code)
    if match:
        return match.group(1)
    else:
        raise ValueError("No function definition found in provided code.")


"""
    Convert the provided text into a valid Python function name in snake_case.

    This function performs the following operations:
    1. Strips leading and trailing whitespace.
    2. Converts all characters to lowercase.
    3. Replaces non-alphanumeric characters with underscores.
    4. If the result starts with a digit, prefixes it with an underscore.

    Args:
        text (str): The input string to convert into a valid Python function name.

    Returns:
        str: The input string converted into a valid Python function name in snake_case.
"""


def to_func_name(text: str) -> str:
    # remove leading and trailing whitespace
    text = text.strip()
    # convert to lowercase
    text = text.lower()
    # remove non-alphanumeric characters and replace spaces with underscores
    text = re.sub(r"\W+", " ", text).strip().replace(" ", "_")
    # if it starts with a digit, prefix it with an underscore
    if text[0].isdigit():
        text = "_" + text

    return text


"""
    This function checks if the given input string contains the word "pass".
    This is used to check if code generated by a language model is incomplete.

    Args:
        input_string (str): The input string to be checked.

    Returns:
        re.Match: Match object if the word "pass" is found, None otherwise.
"""


def is_incomplete_code(input_string):
    # The word boundaries \b ensure we don't match words that contain "pass" as a substring
    pattern = r"\bpass\b"
    return re.search(pattern, input_string, re.IGNORECASE)


"""
Extracts the word "true" or "false" from the input string, removes all spaces, newlines, tabs,
and punctuation, and formats the extracted word to have the first letter capitalized.

Args:
    input_str (str): The input string to extract the boolean value from.

Returns:
    str: The extracted boolean value with the first letter capitalized.

Raises:
    ValueError: If no boolean value is found in the input string.
"""


def format_binary_output(input_str: str) -> bool:
    # Remove all non-word characters
    input_str = re.sub(r"[^\w\s]", "", input_str)

    # Extract the word "true" or "false"
    match = re.search(r"\b(true|false)\b", input_str.lower())
    if match:
        # Format the extracted word to have the first letter capitalized
        return match.group(1).capitalize() == "True"
    else:
        raise ValueError("No boolean value found in input string")


"""
Determine if the given stringified code is valid Python syntax.

Args:
    code (str): Source code

Returns:
    bool: True if the code is valid Python syntax, False otherwise.
"""


def is_valid_syntax(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
