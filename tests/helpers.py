import itertools
from time import time

# This module contains helpers for test cases

def get(iterable, n):
    """get
    Yields n items from iterable, then breaks

    :param iterable: Iterable from which items should be yielded
    :param n: Number of items to yield
    """
    for i, x in enumerate(itertools.cycle(iterable)):
        if i < n:
            yield x
        else:
            return

def getlist(iterable, n):
    """getlist
    Returns a list containing n items from iterable.

    :param iterable: Iterable from which items should be fetched
    :param n: Number of items to fetch
    """
    return [x for x in get(iterable, n)]

def noattr(obj):
    """noattr
    Returns a string representing an attribute name which does not exist on
    obj.
    """
    attr = None
    while attr is None or hasattr(obj, attr):
        attr = "__test_{}".format(str(time()).replace('.', ''))
    return attr

def weirdtype():
    """weirdtype
    Generates a weird type for use in testing TypeErrors
    """
    class WeirdType:
        pass
    return WeirdType()

def hasattrs(obj, *attrs):
    for attr in attrs:
        if not hasattr(obj, attr):
            return False
    return True
