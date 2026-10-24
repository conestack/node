from functools import lru_cache  # noqa
from zope.deprecation import deprecated
import sys


IS_PYPY = '__pypy__' in sys.builtin_module_names

# Python 2 compatibility, kept for B/C only
IS_PY2 = False
STR_TYPE = str
UNICODE_TYPE = str
ITER_FUNC = 'items'


def iteritems(obj):
    return obj.items()


def func_name(func):
    return func.__name__


deprecated(
    [
        'IS_PY2',
        'STR_TYPE',
        'UNICODE_TYPE',
        'ITER_FUNC',
        'iteritems',
        'func_name',
        'lru_cache',
    ],
    'Python 2 compatibility is gone, use the builtins or ``functools`` '
    'instead. Will be removed in node 3.0.',
)
