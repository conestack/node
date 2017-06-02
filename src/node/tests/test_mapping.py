from node.behaviors import DictStorage
from node.behaviors import FullMapping
from node.testing import FullMappingTester
from node.tests import NodeTestCase
from plumber import plumbing


###############################################################################
# Mock objects
###############################################################################

@plumbing(FullMapping)
class FailingFullMapping(object):
    pass


@plumbing(
    FullMapping,
    DictStorage)
class SuccessFullMapping(object):
    pass


###############################################################################
# Tests
###############################################################################

class TestMapping(NodeTestCase):

    def test_fullmapping_fails(self):
        # A full mapping that is going to fail, because nobody takes care about
        # ``__delitem__``, ``__getitem__``, ``__iter__`` and ``__setitem__``
        tester = FullMappingTester(FailingFullMapping, node_checks=False)
        tester.run()
        self.check_output("""\
        ``__contains__``: failed: NotImplementedError()
        ``__delitem__``: failed: NotImplementedError()
        ``__getitem__``: failed: NotImplementedError()
        ``__iter__``: failed: NotImplementedError()
        ``__len__``: failed: NotImplementedError()
        ``__setitem__``: failed: NotImplementedError()
        ``clear``: failed: NotImplementedError()
        ``copy``: failed: NotImplementedError()
        ``get``: failed: NotImplementedError()
        ``has_key``: failed: NotImplementedError()
        ``items``: failed: NotImplementedError()
        ``iteritems``: failed: NotImplementedError()
        ``iterkeys``: failed: NotImplementedError()
        ``itervalues``: failed: NotImplementedError()
        ``keys``: failed: NotImplementedError()
        ``pop``: failed: NotImplementedError()
        ``popitem``: failed: NotImplementedError()
        ``setdefault``: failed: NotImplementedError()
        ``update``: failed: NotImplementedError()
        ``values``: failed: NotImplementedError()
        """, tester.combined)

        # All methods are defined on the class by the FullMapping behavior,
        # none are inherited from base classes
        self.check_output("""\
        __contains__: FailingFullMapping
        __delitem__: FailingFullMapping
        __getitem__: FailingFullMapping
        __iter__: FailingFullMapping
        __len__: FailingFullMapping
        __setitem__: FailingFullMapping
        clear: FailingFullMapping
        copy: FailingFullMapping
        get: FailingFullMapping
        has_key: FailingFullMapping
        items: FailingFullMapping
        iteritems: FailingFullMapping
        iterkeys: FailingFullMapping
        itervalues: FailingFullMapping
        keys: FailingFullMapping
        pop: FailingFullMapping
        popitem: FailingFullMapping
        setdefault: FailingFullMapping
        update: FailingFullMapping
        values: FailingFullMapping
        """, tester.wherefrom)

    def test_fullmapping_success(self):
        # Use a storage
        tester = FullMappingTester(SuccessFullMapping, node_checks=False)
        tester.run()
        self.check_output("""\
        ``__contains__``: OK
        ``__delitem__``: OK
        ``__getitem__``: OK
        ``__iter__``: OK
        ``__len__``: OK
        ``__setitem__``: OK
        ``clear``: OK
        ``copy``: OK
        ``get``: OK
        ``has_key``: OK
        ``items``: OK
        ``iteritems``: OK
        ``iterkeys``: OK
        ``itervalues``: OK
        ``keys``: OK
        ``pop``: OK
        ``popitem``: OK
        ``setdefault``: OK
        ``update``: OK
        ``values``: OK
        """, tester.combined)

        # Only the Four were taken from the base class, the others were filled
        # in by the FullMapping behavior
        self.check_output("""\
        __contains__: SuccessFullMapping
        __delitem__: SuccessFullMapping
        __getitem__: SuccessFullMapping
        __iter__: SuccessFullMapping
        __len__: SuccessFullMapping
        __setitem__: SuccessFullMapping
        clear: SuccessFullMapping
        copy: SuccessFullMapping
        get: SuccessFullMapping
        has_key: SuccessFullMapping
        items: SuccessFullMapping
        iteritems: SuccessFullMapping
        iterkeys: SuccessFullMapping
        itervalues: SuccessFullMapping
        keys: SuccessFullMapping
        pop: SuccessFullMapping
        popitem: SuccessFullMapping
        setdefault: SuccessFullMapping
        update: SuccessFullMapping
        values: SuccessFullMapping
        """, tester.wherefrom)
