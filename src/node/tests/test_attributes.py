from node.behaviors import Attributes
from node.behaviors import DefaultInit
from node.behaviors import DictStorage
from node.behaviors import MappingNode
from node.behaviors import Nodespaces
from node.behaviors.attributes import NodeAttributes
from node.interfaces import INodeAttributes
from node.tests import NodeTestCase
from node.utils import AttributeAccess
from plumber import plumbing


class TestAttributes(NodeTestCase):

    def test_Attributes(self):
        @plumbing(Attributes, DefaultInit, MappingNode, DictStorage)
        class AttributedNode(object):
            pass

        node = AttributedNode(name='attributed')
        self.assertFalse(node.attribute_access_for_attrs)
        self.assertEqual(node.attributes_factory, NodeAttributes)

        with self.assertRaises(AttributeError):
            node.__attrs__
        attrs = node.attrs
        self.assertEqual(node.__attrs__, attrs)

        self.assertIsInstance(node.attrs, NodeAttributes)
        self.assertTrue(INodeAttributes.providedBy(node.attrs))

        expected = '<NodeAttributes object \'attributed\' at '
        self.assertTrue(repr(attrs).startswith(expected))

        attrs['foo'] = 'bar'
        self.assertEqual(attrs['foo'], 'bar')

        with self.assertRaises(AttributeError) as arc:
            node.attrs.foo
        self.assertEqual(
            str(arc.exception),
            '\'NodeAttributes\' object has no attribute \'foo\''
        )

    def test_AttributesWithNodespaces(self):
        @plumbing(Nodespaces, Attributes, MappingNode, DictStorage)
        class AttributedNode(object):
            pass

        node = AttributedNode()
        self.assertFalse('__attrs__' in node.nodespaces)
        attrs = node.attrs
        self.assertEqual(node.nodespaces['__attrs__'], attrs)

    def test_attribute_access_for_attrs(self):
        @plumbing(Attributes, MappingNode, DictStorage)
        class AttributedNode(object):
            pass

        node = AttributedNode()
        node.attribute_access_for_attrs = True

        attrs = node.attrs
        self.assertIsInstance(attrs, AttributeAccess)

        expected = '<node.utils.AttributeAccess object at'
        self.assertTrue(repr(attrs).startswith(expected))

        attrs.foo = 'bar'
        self.assertEqual(attrs['foo'], 'bar')

        attrs['bar'] = 'baz'
        self.assertEqual(attrs.bar, 'baz')
