# File: decorators.py

def adapt(code):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if code == "":
                # If no code is provided, run the decorated function as normal
                return func(*args, **kwargs)
            else:
                local_vars = {
                    'args': args,
                    'kwargs': kwargs,
                }
                exec(code, local_vars)
                return local_vars.get('result')
        return wrapper
    return decorator
