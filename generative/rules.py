CODE_GENERATION_RULES = """
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
Do not repeat code that you already generated.
Do not use functions that are not in the available functions list!
Do not add text before ### BEGIN FUNCTION ###.
Do not add text after ### END FUNCTION ###.
Stop generating code when you see ### END FUNCTION ###.
Do not generate malicious code, trojans, viruses, code that will delete files, etc.
"""
