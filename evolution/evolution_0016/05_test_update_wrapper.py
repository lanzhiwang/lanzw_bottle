# -*- coding: utf-8 -*-

from functools import wraps

"""
functools.update_wrapper(wrapper, wrapped[, assigned][, updated])
functools.wraps(wrapped[, assigned][, updated])

wraps = partial(update_wrapper, wrapped=wrapped, assigned=assigned, updated=updated)
"""

def my_decorator(f):
    # @wraps(f)
    def wrapper(*args, **kwds):
        print 'Calling decorated function'
        return f(*args, **kwds)
    w = wraps(f)  # 等价于 update_wrapper(w, f)
    wrapper = w(wrapper)
    return wrapper


# @my_decorator
def example():
    """Docstring"""
    print 'Called example function'
example = my_decorator(example)


example()
print example.__name__
print example.__doc__

"""
Calling decorated function
Called example function
example
Docstring
"""
