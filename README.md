# Dynamic Meta-programming with Large Language Models
Metaprogramming with safe code injection from [generative APIs](https://github.com/ch3njust1n/generative-api) for adaptable software

# Setup instructions
1. Create `.env` for your environment variables
2. Add your API key

To run unit tests

```bash
pytest -s
```

### Decorator usage

1. `OPENAI_API_KEY` must be set in `.env` or in your terminal `OPENAI_API_KEY=your-api-key-here`

Then use as follows:

```
from meta import adapt, setup_openai

@adapt(use_llm=True)
def func(a, b):
	'''
	Write a python 3 function that 
	computes the N-th Fibonacci number.
	'''
	pass

assert func(8) == 13
```