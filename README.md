# Dynamic Metaprogramming with Large Language Models
Metaprogramming with safe code injection from [generative APIs](https://github.com/ch3njust1n/generative-api) for adaptable software

# Setup instructions
1. Create `.env` for your environment variables. See `.env.example`.
2. Add your API key

To run all unit tests. 

**Options:**
- `-s` shows print statements
- `-v` indicates when a tests passes
- `--durations=0` displays a list of n slowest tests at the end of the test session

```bash
pytest -s -v --durations=0
```

To run a specific unit test:
```bash
pytest -k <test name>
```

### Decorator usage

1. `OPENAI_API_KEY` must be set in `.env` or in your terminal `OPENAI_API_KEY=your-api-key-here`
2. Define your custome LLM solution. Then import the decorators and your llm function and pass it to the decorator.
3. Use as follows:

### Function decorators

`@adapt` decorator example using a large language model:
```python
from meta import adapt

@adapt(model=llm)
def func(a, b):
   prompt = """
   Write a complete python 3 function, including the header and
   return statement that computes the N-th Fibonacci number.
   """

assert func(8) == 21
```

`@catch` decorator example:
```python
from meta import catch

@catch(model=llm)
def func(a, b):
      raise Exception("Original function exception")
```

`@stack_trace` decorator example:
```python
from meta import stack_trace

@stack_trace(model=llm)
def funkodunko():
      items = [1, 2, 3]
      return items[5]
```

Produces a human-readable summary of the stack trace:
```
tests/test_adapt_decorator.py Traceback (most recent call last):
  File "/Users/justin/Documents/dev/personal/ml/dynamic-mp-llm/meta.py", line 167, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/justin/Documents/dev/personal/ml/dynamic-mp-llm/tests/test_adapt_decorator.py", line 100, in funkodunko
    return items[5]
           ~~~~~^^^
IndexError: list index out of range


Human-readable summary:
(funkodunko) Attempted to access an element of a list that does not exist. 

Suggestions for how to fix the error:
1. Check the length of the list to make sure there are enough elements to access the desired index. 
2. If the list is too short, add elements to the list in order to access the desired index.
3. If the list is empty, consider initializing the list with data.
```

### Metaclasses

Define your class:
```
from model import gpt
from meta import GenerativeMetaClass
from prompt import format_generative_function

class Doggo(metaclass=GenerativeMetaClass):
    def __init__(self, name: str):
        self.name = name

    def set_treat(self, treat: str):
        self.stomach = treat

prompt = "Write a function with the header `def do_trick(self)` that returns a string '*sit*'"
prompt = format_generative_function(prompt)
new_trick = gpt(prompt)
GenerativeMetaClass.generate(Doggo, new_trick)
a_good_boy = Doggo('Chewy')
a_good_boy.set_treat('roast beef')
```

### Check which functions are generative
```python
import inspect
all_funcs = inspect.getmembers(
    cls, predicate=inspect.isfunction
)
[f for f in all_funcs if f._is_generative]
```

### Code Injection