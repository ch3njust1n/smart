# Dynamic Metaprogramming with Large Language Models
Metaprogramming with safe code injection from [generative APIs](https://github.com/ch3njust1n/generative-api) for adaptable software

![Tests](https://github.com/ch3njust1n/generative/actions/workflows/pull-request.yml/badge.svg)

# Setup instructions
1. Create `.env` for your environment variables. See `.env.example`.
2. Add your API key
3. `python setup.py install`
4. `pre-commit install`

To run all unit tests.

**Options:**
- `-s` shows print statements
- `-v` indicates when a tests passes
- `--durations=0` displays a list of n slowest tests at the end of the test session

```bash
pytest -s -v --durations=0
```

To run all tests in a specific file:
```bash
pytest <file name>
```

To run a specific unit test:
```bash
pytest -k <test name>
```

4. Linting and VSCode

To setup linting with `flake8` and auto formatting with `black`:
4.1. Create the subdirectory `.vscode` in the root directory
4.2. Add the following `settings.json` file:
```json
{
    "editor.formatOnSave": true,
    "python.formatting.provider": "none",
    "python.formatting.blackArgs": [
        "--line-length",
        "100"
    ],
    "python.linting.enabled": true,
    "python.linting.lintOnSave": true,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": [
        "--line-length",
        "100"
    ],
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        },
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

### Decorator usage

1. `OPENAI_API_KEY` must be set in `.env` or in your terminal `OPENAI_API_KEY=your-api-key-here`
2. Define your custome LLM solution. Then import the decorators and your llm function and pass it to the decorator.
3. Use as follows:

### Function decorators

`@adapt` decorator example using a large language model:
```python
from generative.decorator import adapt

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
from generative.decorator import catch

@catch(model=llm)
def func(a, b):
      raise Exception("Original function exception")
```

`@stack_trace` decorator example:
```python
from generative.decorator import stack_trace

@stack_trace(model=llm)
def funkodunko():
      items = [1, 2, 3]
      return items[5]
```

Produces a human-readable summary of the stack trace:
```bash
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
```python
from model import gpt3
from generative.metaclasses import GenerativeMetaClass
from prompt import format_generative_function

class Doggo(metaclass=GenerativeMetaClass):
    def __init__(self, name: str):
        self.name = name

    def set_treat(self, treat: str):
        self.stomach = treat

prompt = "Write a function with the header `def do_trick(self)` that returns a string '*sit*'"
prompt = format_generative_function(prompt)
new_trick = gpt3(prompt)
a_good_boy = Doggo('Chewy')
a_good_boy.generate(new_trick)
a_good_boy.do_trick()
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

### Integrate database

Clients can integrate custom database solutions to save the generated code, function name, and, if available, arguments and keyword arguments. This could be useful in large pipelines for embedding generated code. That could later be retreived given a similar input so that the model does not need to be run again.

```python
import redis

from generative.functions import adapt
from generative.metaclasses import AbstractDatabase
from models import claude

class VectorDB(AbstractDatabase):
    def __init__(self):
        self.db = redis.Redis(host='localhost', port=6379, db=0)

    def contains(self, key: str) -> bool:
        return self.db.exists(key)
    
    def get(self, query: str) -> List[Dict] :
        return self.db.get(query)

    """
    data will always take this form:

    data = {
        "function_name": func_name,
        "generated_code": code,
        "args": {...},
        "kwargs": {...},
    }
    """
    def set(self, data: Any) -> None:
        key: str = data.function_name
        self.db.set(key, data)

class Demo():
    db = VectorDB()

    @adapt(model=claude, critic=claude, database=db)
    def func(self):
        pass # some functionality to self-heal or adapt
```

### Code Injection