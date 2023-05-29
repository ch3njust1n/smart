# Demo code for dynamic metaprogramming decorator

from meta import adapt

a = "sum(args)"


@adapt(a)
def add(a, b):
    return a + b


print(add(3, 4))  # Prints: 7

b = ""


@adapt(b)
def multiply(a, b):
    return a * b


print(multiply(3, 4))  # Prints: 12
