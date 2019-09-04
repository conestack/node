# -*- coding: utf-8 -*-
from node.behaviors import Adopt
from node.behaviors import DefaultInit
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.interfaces import INode
from node.testing import FullMappingTester
from node.tests import NodeTestCase
from plumber import plumbing
from zope.interface import Interface
from zope.interface import alsoProvides


###############################################################################
# Mock objects
###############################################################################

@plumbing(
    Adopt,
    DefaultInit,
    Nodify,
    OdictStorage)
class Node(object):
    pass


class RootNode(Node):
    pass


class INodeInterface(Interface):
    pass


class INoInterface(Interface):
    pass


###############################################################################
# Tests
###############################################################################

class TestNodify(NodeTestCase):

    def test_Nodify(self):
        root = Node(name='root')
        root['child'] = Node()
        self.assertEqual(root.name, 'root')
        self.assertEqual(root.parent, None)

        child = root['child']
        self.assertEqual(child.name, 'child')
        self.assertEqual(child.parent, root)
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_nodify.Node\'>: root\n'
            '  <class \'node.tests.test_nodify.Node\'>: child\n'
        ))
        self.assertTrue(bool(root))

        tester = FullMappingTester(Node)
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

        root = RootNode('root')
        child = root['child'] = Node()
        subchild = child['subchild'] = Node()
        self.assertEqual(root.treerepr(), (
            '<class \'node.tests.test_nodify.RootNode\'>: root\n'
            '  <class \'node.tests.test_nodify.Node\'>: child\n'
            '    <class \'node.tests.test_nodify.Node\'>: subchild\n'
        ))

        root[u'\xf6'] = Node()
        self.checkOutput("""\
        <class 'node.tests.test_nodify.RootNode'>: root
        __<class 'node.tests.test_nodify.Node'>: child
        ____<class 'node.tests.test_nodify.Node'>: subchild
        __<class 'node.tests.test_nodify.Node'>: ...
        """, root.treerepr(prefix='_'))

        self.checkOutput("""\
        <Node object '...' at ...>
        """, repr(root[u'\xf6']))

        alsoProvides(child, INodeInterface)
        self.assertEqual(subchild.acquire(RootNode), root)
        self.assertEqual(subchild.acquire(INodeInterface), child)
        self.assertEqual(subchild.acquire(INode), child)
        self.assertEqual(subchild.acquire(INoInterface), None)
