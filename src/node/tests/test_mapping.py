from node.behaviors import DefaultInit
from node.behaviors import DictStorage
from node.behaviors import FullMapping
from node.behaviors import MappingAdopt
from node.behaviors import MappingNode as MappingNodeBehavior
from node.behaviors import OdictStorage
from node.interfaces import IContentishNode
from node.interfaces import IMappingNode
from node.interfaces import INode
from node.testing import FullMappingTester
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import alsoProvides
from zope.interface import Interface


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


@plumbing(
    MappingAdopt,
    DefaultInit,
    MappingNodeBehavior,
    OdictStorage)
class MappingNode(object):
    pass


class RootMappingNode(MappingNode):
    pass


class INodeInterface(Interface):
    pass


class INoInterface(Interface):
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
        self.checkOutput("""\
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
        self.checkOutput("""\
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
        self.checkOutput("""\
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
        self.checkOutput("""\
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

    def test_MappingNode(self):
        root = MappingNode(name='root')
        self.assertTrue(INode.providedBy(root))
        self.assertTrue(IContentishNode.providedBy(root))
        self.assertTrue(IMappingNode.providedBy(root))

        root['child'] = MappingNode()
        self.assertEqual(root.name, 'root')
        self.assertEqual(root.parent, None)

        child = root['child']
        self.assertEqual(child.name, 'child')
        self.assertEqual(child.parent, root)
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_mapping.MappingNode\'>: root\n'
            '  <class \'node.tests.test_mapping.MappingNode\'>: child\n'
        ))
        self.assertTrue(bool(root))

        tester = FullMappingTester(MappingNode)
        tester.run()
        self.assertEqual(tester.combined, (
            '``__contains__``: OK\n'
            '``__delitem__``: OK\n'
            '``__getitem__``: OK\n'
            '``__iter__``: OK\n'
            '``__len__``: OK\n'
            '``__setitem__``: OK\n'
            '``clear``: OK\n'
            '``copy``: OK\n'
            '``get``: OK\n'
            '``has_key``: OK\n'
            '``items``: OK\n'
            '``iteritems``: OK\n'
            '``iterkeys``: OK\n'
            '``itervalues``: OK\n'
            '``keys``: OK\n'
            '``pop``: OK\n'
            '``popitem``: OK\n'
            '``setdefault``: OK\n'
            '``update``: OK\n'
            '``values``: OK'
        ))

        root = RootMappingNode(name='root')
        child = root['child'] = MappingNode()
        subchild = child['subchild'] = MappingNode()
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_mapping.RootMappingNode\'>: root\n'
            '  <class \'node.tests.test_mapping.MappingNode\'>: child\n'
            '    <class \'node.tests.test_mapping.MappingNode\'>: subchild\n'
        ))

        root[u'\xf6'] = MappingNode()
        self.checkOutput("""\
        <class 'node.tests.test_mapping.RootMappingNode'>: root
        __<class 'node.tests.test_mapping.MappingNode'>: child
        ____<class 'node.tests.test_mapping.MappingNode'>: subchild
        __<class 'node.tests.test_mapping.MappingNode'>: ...
        """, root.treerepr(prefix='_'))

        self.checkOutput("""\
        <MappingNode object '...' at ...>
        """, repr(root[u'\xf6']))

        alsoProvides(child, INodeInterface)
        self.assertEqual(subchild.acquire(RootMappingNode), root)
        self.assertEqual(subchild.acquire(INodeInterface), child)
        self.assertEqual(subchild.acquire(INode), child)
        self.assertEqual(subchild.acquire(INoInterface), None)

        # detach
        self.assertEqual(child.name, 'child')
        self.assertEqual(child.parent, root)
        child = root.detach('child')
        self.assertEqual(child.name, 'child')
        self.assertEqual(child.parent, None)
        self.assertFalse('child' in root)
        self.checkOutput("""\
        <class 'node.tests.test_mapping.MappingNode'>: child
        __<class 'node.tests.test_mapping.MappingNode'>: subchild
        """, child.treerepr(prefix='_'))

    def test_BC_imports(self):
        from node.behaviors import Nodify
        self.assertTrue(Nodify is MappingNodeBehavior)

        from node.interfaces import INodify
        self.assertTrue(INodify is IMappingNode)
