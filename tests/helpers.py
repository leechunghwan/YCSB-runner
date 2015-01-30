import itertools
import runner.constants as const

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
