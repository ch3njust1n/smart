"""
Prompt for generating entire functions

Args:
    code (string): Source code fo function to be appended to prompt.
    
Returns:
    Prompt for generating a function.
"""


def format_generative_function(code: str) -> str:
    return f"""
	Do not write a driver program, do not comment, do not explain. 
	Do not write any code outside of the function body.
	Do not call the function or return a reference to it.
	For example, only do this:
	```
	def func():
	# function body
	```
	and do not do this:
	```
	def func():
	# function body
	return func()
	```
	Only return the function header and body!
 
	Source code:
	{code}
	"""


"""
Prompt for summarizing as human-readable stack traces

Args:
    text (string): Stack trace to be appended to prompt.
    
Returns:
    Prompt for summarizing a stack trace.
"""


def format_stack_trace(text: str) -> str:
    return f"""
	Summarize the following stack trace and keep and relevant line numbers.
	Stack trace:
	{text}
	"""
