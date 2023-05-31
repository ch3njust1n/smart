# Dynamic Metaprogramming with Large Language Models
Metaprogramming with safe code injection from [generative APIs](https://github.com/ch3njust1n/generative-api) for adaptable software

# Setup instructions
1. Create `.env` for your environment variables. See `.env.example`.
2. Add your API key

To run unit tests

```bash
pytest -s
```

### Decorator usage

1. `OPENAI_API_KEY` must be set in `.env` or in your terminal `OPENAI_API_KEY=your-api-key-here`

2. Use as follows:

`@adapt` decorator example using a large language model:
```
from meta import adapt, setup_openai

@adapt(use_llm=True)
def func(a, b):
   prompt = """
   Write a complete python 3 function, including the header and
   return statement that computes the N-th Fibonacci number.
   """

assert func(8) == 21
```

`@catch` decorator example:
```
@catch(llm=llm)
def func(a, b):
      raise Exception("Original function exception")
```

`@stack_trace` decorator example:
```
@stack_trace(llm=llm)
def funkodunko():
      items = [1, 2, 3]
      return items[5]
```

Produces a human-readable summary of the stack trace:
```
tests/test_adapt_decorator.py new_exception_message: Traceback (most recent call last):
  File "/Users/justin/Documents/dev/personal/ml/dynamic-mp-llm/meta.py", line 173, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/justin/Documents/dev/personal/ml/dynamic-mp-llm/tests/test_adapt_decorator.py", line 100, in funkodunko
    return items[5]
           ~~~~~^^^
IndexError: list index out of range


Human-readable summary:
(funkodunko) IndexError: list index out of range
```