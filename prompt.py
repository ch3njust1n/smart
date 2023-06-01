import textwrap

"""
Prompt for generating entire functions

Args:
    code (string): Source code fo function to be appended to prompt.
    
Returns:
    Prompt for generating a function.
"""


def format_generative_function(code: str) -> str:
    return textwrap.dedent(
        f"""
	Follow these rules precisely:
	Do's:
    Only generate Python code.
	Generate a function with the same number of parameters as the original function!

	Don'ts:
	Do not write a driver program.
	Do not comment. 
	Do not explain the code. 
	Do not give a header introducing the code e.g. 'Rewritten source code:'
	Do not write any code outside of the function body.
	Do not call the function or return a reference to it.
	Do not use decorators.
	Do not print anything!
	Do not add text before ### BEGIN FUNCTION ###.
	Do not add text after ### END FUNCTION ###.
	Stop generating code when you see ### END FUNCTION ###.
	
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
 
	Source code:
	{code}
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
