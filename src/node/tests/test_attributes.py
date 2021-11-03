from node.behaviors import Attributes
from node.behaviors import DefaultInit
from node.behaviors import NodeChildValidate
from node.behaviors import Nodespaces
from node.behaviors import Nodify
from node.behaviors import OdictStorage
from node.behaviors.attributes import NodeAttributes
from node.interfaces import INodeAttributes
from node.tests import NodeTestCase
from node.utils import AttributeAccess
from plumber import plumbing


class TestAttributes(NodeTestCase):

    def test_Attributes(self):
        @plumbing(
            NodeChildValidate,
            Nodespaces,
            Attributes,
            DefaultInit,
            Nodify,
            OdictStorage)
        class AttributedNode(object):
            pass

        node = AttributedNode(name='attributed')
        self.assertFalse(node.attribute_access_for_attrs)

        node.attribute_access_for_attrs = True
        self.assertIsInstance(node.attrs, AttributeAccess)

        expected = '<node.utils.AttributeAccess object at'
        self.assertTrue(repr(node.attrs).startswith(expected))

        node.attrs.foo = 'bar'
        self.assertEqual(node.attrs['foo'], 'bar')

        node.attrs['bar'] = 'baz'
        self.assertEqual(node.attrs.bar, 'baz')

        node.attrs['oof'] = 'abc'
        self.assertEqual(node.attrs.oof, 'abc')

        node.attribute_access_for_attrs = False
        self.assertIsInstance(node.attrs, NodeAttributes)
        self.assertTrue(INodeAttributes.providedBy(node.attrs))

        expected = '<NodeAttributes object \'attributed\' at '
        self.assertTrue(repr(node.attrs).startswith(expected))

        self.assertEqual(node.attrs['foo'], 'bar')

        with self.assertRaises(AttributeError) as arc:
            node.attrs.foo
        self.assertEqual(
            str(arc.exception),
            '\'NodeAttributes\' object has no attribute \'foo\''
        )
