import sys

IS_PY2 = sys.version_info[0] < 3
IS_PYPY = '__pypy__' in sys.builtin_module_names
STR_TYPE = basestring if IS_PY2 else str
UNICODE_TYPE = unicode if IS_PY2 else str
ITER_FUNC = 'iteritems' if IS_PY2 else 'items'


def iteritems(obj):
    return getattr(obj, ITER_FUNC)()


def func_name(func):
    return func.func_name if IS_PY2 else func.__name__
