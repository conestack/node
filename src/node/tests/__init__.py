import doctest
import unittest


class patch(object):

    def __init__(self, module, name, ob):
        self.module = module
        self.name = name
        self.ob = ob

    def __call__(self, ob):
        ob.__test_patch__ = (self.module, self.name, self.ob)

        def _wrapped(*args, **kw):
            module, name, obj = ob.__test_patch__
            orgin = (module, name, getattr(module, name))
            setattr(module, name, obj)
            try:
                ob(*args, **kw)
            except Exception as e:
                raise e
            finally:
                module, name, obj = orgin
                setattr(module, name, obj)
        return _wrapped


class Example(object):

    def __init__(self, want):
        self.want = want + '\n'


class Failure(Exception):
    pass


class NodeTestCase(unittest.TestCase):

    def __init__(self, *args, **kw):
        unittest.TestCase.__init__(self, *args, **kw)
        self._checker = doctest.OutputChecker()
        self._optionflags = (
            doctest.NORMALIZE_WHITESPACE
            | doctest.ELLIPSIS
            | doctest.REPORT_ONLY_FIRST_FAILURE
        )

    def expectError(self, exc, func, *args, **kw):
        try:
            func(*args, **kw)
        except exc as e:
            return e
        else:
            msg = 'Expected \'{}\' when calling \'{}\''.format(exc, func)
            raise Exception(msg)

    # B/C
    expect_error = expectError

    def checkOutput(self, want, got, optionflags=None):
        if optionflags is None:
            optionflags = self._optionflags
        success = self._checker.check_output(want, got, optionflags)
        if not success:
            raise Failure(self._checker.output_difference(
                Example(want),
                got, optionflags
            ))

    # B/C
    check_output = checkOutput
