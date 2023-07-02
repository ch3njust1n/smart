from model import (
    # Palm, 
    Claude
)
from generative.prompt import format_semantic_checker
from generative.utils import format_binary_output

claude = Claude()
# palm = Palm()
dataset = []

for code in dataset:
    prompt = format_semantic_checker(code, input, context="")
    output = claude.generate(prompt)
    is_valid = format_binary_output(output)
