# -*- coding: utf-8 -*-
from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import MappingNode as MappingNodeBehavior
from node.behaviors import OdictStorage
from node.interfaces import INode
from node.testing import FullMappingTester
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import alsoProvides
from zope.interface import Interface


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    Adopt,
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

class TestNodify(NodeTestCase):

    def test_MappingNode(self):
        root = MappingNode(name='root')
        root['child'] = MappingNode()
        self.assertEqual(root.name, 'root')
        self.assertEqual(root.parent, None)

        child = root['child']
        self.assertEqual(child.name, 'child')
        self.assertEqual(child.parent, root)
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_node.MappingNode\'>: root\n'
            '  <class \'node.tests.test_node.MappingNode\'>: child\n'
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

        root = RootMappingNode('root')
        child = root['child'] = MappingNode()
        subchild = child['subchild'] = MappingNode()
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_node.RootMappingNode\'>: root\n'
            '  <class \'node.tests.test_node.MappingNode\'>: child\n'
            '    <class \'node.tests.test_node.MappingNode\'>: subchild\n'
        ))

        root[u'\xf6'] = MappingNode()
        self.checkOutput("""\
        <class 'node.tests.test_node.RootMappingNode'>: root
        __<class 'node.tests.test_node.MappingNode'>: child
        ____<class 'node.tests.test_node.MappingNode'>: subchild
        __<class 'node.tests.test_node.MappingNode'>: ...
        """, root.treerepr(prefix='_'))

        self.checkOutput("""\
        <MappingNode object '...' at ...>
        """, repr(root[u'\xf6']))

        alsoProvides(child, INodeInterface)
        self.assertEqual(subchild.acquire(RootMappingNode), root)
        self.assertEqual(subchild.acquire(INodeInterface), child)
        self.assertEqual(subchild.acquire(INode), child)
        self.assertEqual(subchild.acquire(INoInterface), None)
