import re

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
