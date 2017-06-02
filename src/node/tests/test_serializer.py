from node.base import AbstractNode
from node.base import AttributedNode
from node.base import BaseNode
from node.base import OrderedNode
from node.serializer import deserialize
from node.serializer import deserializer
from node.serializer import serialize
from node.serializer import serializer
from node.tests import NodeTestCase
from node.utils import UNSET
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implementer
import json
import uuid


###############################################################################
# Mock objects
###############################################################################

def referenced_function():
    pass                                                     # pragma: no cover


class ReferencedClass(object):
    def foo(self):
        pass                                                 # pragma: no cover


class ICustomNode(Interface):
    iface_attr = Attribute('Custom Attribute')


@implementer(ICustomNode)
class CustomNode(AttributedNode):
    iface_attr = None
    class_attr = None


class CustomInitNode(CustomNode):
    def __init__(self, a, b):
        self.a = a
        self.b = b


@serializer(ICustomNode)
def iface_bound_serialize_custom_node(encoder, node, data):
    data['iface_attr'] = node.iface_attr


@deserializer(ICustomNode)
def iface_bound_deserialize_custom_node(encoder, node, data):
    node.iface_attr = data['iface_attr']


@serializer(CustomNode)
def class_bound_serialize_custom_node(encoder, node, data):
    data['class_attr'] = node.class_attr


@deserializer(CustomNode)
@deserializer(CustomInitNode)
def class_bound_deserialize_custom_node(encoder, node, data):
    node.class_attr = data['class_attr']


@serializer(CustomInitNode)
def serialize_custom_node(encoder, node, data):
    class_bound_serialize_custom_node(encoder, node, data)
    data['kw'] = {
        'a': node.a,
        'b': node.b
    }


###############################################################################
# Tests
###############################################################################

class TestSerializer(NodeTestCase):

    ###########################################################################
    # Node serialization
    ###########################################################################

    def test_INode(self):
        # Basic ``INode`` implementing object serialization
        json_data = serialize(BaseNode())
        data = json.loads(json_data)
        self.assertEqual(list(data.keys()), ['__node__'])

        node_data = data['__node__']
        self.assertEqual(list(sorted(node_data.keys())), ['class', 'name'])
        self.assertEqual(node_data['class'], 'node.base.BaseNode')
        self.assertEqual(node_data['name'], None)

        node = deserialize(json_data)
        self.assertTrue(str(node).startswith('<BaseNode object \'None\' at'))

    def test_children(self):
        # Node children serializition
        node = OrderedNode(name='base')
        node['child'] = OrderedNode()
        node['child']['sub'] = OrderedNode()
        self.assertEqual(node.treerepr(), (
            '<class \'node.base.OrderedNode\'>: base\n'
            '  <class \'node.base.OrderedNode\'>: child\n'
            '    <class \'node.base.OrderedNode\'>: sub\n'
        ))

        json_data = serialize(node)
        data = json.loads(json_data)
        self.assertEqual(list(data.keys()), ['__node__'])

        node_data = data['__node__']
        self.assertEqual(
            list(sorted(node_data.keys())),
            ['children', 'class', 'name']
        )
        self.assertEqual(node_data['class'], 'node.base.OrderedNode')
        self.assertEqual(node_data['name'], 'base')
        self.assertEqual(len(node_data['children']), 1)

        node_data = node_data['children'][0]['__node__']
        self.assertEqual(node_data['class'], 'node.base.OrderedNode')
        self.assertEqual(node_data['name'], 'child')
        self.assertEqual(len(node_data['children']), 1)

        node_data = node_data['children'][0]['__node__']
        self.assertEqual(list(sorted(node_data.keys())), ['class', 'name'])
        self.assertEqual(node_data['class'], 'node.base.OrderedNode')
        self.assertEqual(node_data['name'], 'sub')

        node = deserialize(json_data)
        self.assertEqual(node.treerepr(), (
            '<class \'node.base.OrderedNode\'>: base\n'
            '  <class \'node.base.OrderedNode\'>: child\n'
            '    <class \'node.base.OrderedNode\'>: sub\n'
        ))

        # Deserialize using given root node
        root = BaseNode(name='root')
        node = deserialize(json_data, root=root)
        self.assertEqual(root.treerepr(), (
            '<class \'node.base.BaseNode\'>: root\n'
            '  <class \'node.base.OrderedNode\'>: base\n'
            '    <class \'node.base.OrderedNode\'>: child\n'
            '      <class \'node.base.OrderedNode\'>: sub\n'
        ))

    def test_children_as_list(self):
        # Serialize list of nodes
        node = OrderedNode(name='base')
        node['child_1'] = OrderedNode()
        node['child_2'] = OrderedNode()
        self.assertEqual(node.treerepr(), (
            '<class \'node.base.OrderedNode\'>: base\n'
            '  <class \'node.base.OrderedNode\'>: child_1\n'
            '  <class \'node.base.OrderedNode\'>: child_2\n'
        ))

        json_data = serialize(node.values())
        data = json.loads(json_data)
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 2)

        node_data = data[0]['__node__']
        self.assertEqual(list(sorted(node_data.keys())), ['class', 'name'])
        self.assertEqual(node_data['class'], 'node.base.OrderedNode')
        self.assertEqual(node_data['name'], 'child_1')

        node_data = data[1]['__node__']
        self.assertEqual(list(sorted(node_data.keys())), ['class', 'name'])
        self.assertEqual(node_data['class'], 'node.base.OrderedNode')
        self.assertEqual(node_data['name'], 'child_2')

        # Deserialize list of nodes using given root node
        root = OrderedNode(name='root')
        nodes = deserialize(json_data, root=root)
        self.assertEqual(len(nodes), 2)
        self.check_output("""\
        [<OrderedNode object 'child_1' at ...>,
        <OrderedNode object 'child_2' at ...>]
        """, str(nodes))

        self.assertEqual(root.treerepr(), (
            '<class \'node.base.OrderedNode\'>: root\n'
            '  <class \'node.base.OrderedNode\'>: child_1\n'
            '  <class \'node.base.OrderedNode\'>: child_2\n'
        ))

    ###########################################################################
    # Attribute serialization
    ###########################################################################

    def test_IAttributes(self):
        # Serialize node implementing ``IAttributes``
        node = AttributedNode(name='base')
        node.attrs['int'] = 0
        node.attrs['float'] = 0.0
        node.attrs['str'] = 'str'
        node.attrs['unset'] = UNSET
        node.attrs['uuid'] = uuid.UUID('fcb30f5a-20c7-43aa-9537-2a25fef0248d')
        node.attrs['list'] = [0, 0.0, 'str', UNSET]

        json_data = serialize(node)
        data = json.loads(json_data)
        self.assertEqual(list(data.keys()), ['__node__'])

        node_data = data['__node__']
        self.assertEqual(
            list(sorted(node_data.keys())),
            ['attrs', 'class', 'name']
        )
        self.assertEqual(node_data['class'], 'node.base.AttributedNode')
        self.assertEqual(node_data['name'], 'base')

        attrs_data = node_data['attrs']
        self.assertEqual(
            list(sorted(attrs_data.keys())),
            ['float', 'int', 'list', 'str', 'unset', 'uuid']
        )
        self.assertEqual(attrs_data['int'], 0)
        self.assertEqual(attrs_data['float'], 0.0)
        self.assertEqual(attrs_data['str'], 'str')
        self.assertEqual(attrs_data['list'], [0, 0.0, 'str', '<UNSET>'])
        self.assertEqual(attrs_data['unset'], '<UNSET>')
        self.assertEqual(
            attrs_data['uuid'],
            '<UUID>:fcb30f5a-20c7-43aa-9537-2a25fef0248d'
        )

        # Deserialize node implementing ``IAttributes``
        node = deserialize(json_data)
        expected = '<AttributedNode object \'base\' at'
        self.assertTrue(str(node).startswith(expected))
        self.assertEqual(node.attrs['int'], 0)
        self.assertEqual(node.attrs['float'], 0.0)
        self.assertEqual(node.attrs['str'], 'str')
        self.assertEqual(node.attrs['list'], [0, 0.0, 'str', UNSET])
        self.assertEqual(node.attrs['unset'], UNSET)
        self.assertEqual(
            node.attrs['uuid'],
            uuid.UUID('fcb30f5a-20c7-43aa-9537-2a25fef0248d')
        )

    ###########################################################################
    # Referencing of classes, methods and functions
    ###########################################################################

    def test_referencing(self):
        # Serialize and deserialize references
        node = AttributedNode()
        node.attrs['func'] = referenced_function
        node.attrs['class'] = ReferencedClass
        node.attrs['method'] = ReferencedClass.foo

        json_data = serialize(node)
        data = json.loads(json_data)
        self.assertEqual(list(data.keys()), ['__node__'])

        node_data = data['__node__']
        self.assertEqual(
            list(sorted(node_data.keys())),
            ['attrs', 'class', 'name']
        )
        self.assertEqual(node_data['class'], 'node.base.AttributedNode')
        self.assertEqual(node_data['name'], None)

        attrs_data = node_data['attrs']
        self.assertEqual(
            list(sorted(attrs_data.keys())),
            ['class', 'func', 'method']
        )
        self.assertEqual(
            attrs_data['class']['__ob__'],
            'node.tests.test_serializer.ReferencedClass'
        )
        self.assertEqual(
            attrs_data['func']['__ob__'],
            'node.tests.test_serializer.referenced_function'
        )
        self.assertEqual(
            attrs_data['method']['__ob__'],
            'node.tests.test_serializer.ReferencedClass.foo'
        )

        node = deserialize(json_data)
        expected = '<AttributedNode object \'None\' at'
        self.assertTrue(str(node).startswith(expected))
        self.assertEqual(node.attrs['func'], referenced_function)
        self.assertEqual(node.attrs['class'], ReferencedClass)
        self.assertEqual(node.attrs['method'], ReferencedClass.foo)

    ###########################################################################
    # Custom serializer
    ###########################################################################

    def test_custom_bound(self):
        node = CustomNode(name='custom')
        # Interface bound custom serializer and deserializer handles iface_attr
        node.iface_attr = 'Iface Attr Value'
        # Class bound custom serializer and deserializer handles class_attr
        node.class_attr = 'Class Attr Value'

        json_data = serialize(node)
        data = json.loads(json_data)
        self.assertEqual(list(data.keys()), ['__node__'])

        node_data = data['__node__']
        self.assertEqual(
            list(sorted(node_data.keys())),
            ['attrs', 'class', 'class_attr', 'iface_attr', 'name']
        )
        self.assertEqual(
            node_data['class'],
            'node.tests.test_serializer.CustomNode'
        )
        self.assertEqual(node_data['name'], 'custom')
        self.assertEqual(node_data['attrs'], {})
        self.assertEqual(node_data['iface_attr'], 'Iface Attr Value')
        self.assertEqual(node_data['class_attr'], 'Class Attr Value')

        node = deserialize(json_data)
        expected = '<CustomNode object \'custom\' at'
        self.assertTrue(str(node).startswith(expected))
        self.assertEqual(node.iface_attr, 'Iface Attr Value')
        self.assertEqual(node.class_attr, 'Class Attr Value')

    def test_custom_init(self):
        # Serialize and deserialize node with custom constructor
        node = CustomInitNode(a='A', b='B')

        json_data = serialize(node)
        data = json.loads(json_data)
        self.assertEqual(list(data.keys()), ['__node__'])

        node_data = data['__node__']
        self.assertEqual(
            list(sorted(node_data.keys())),
            ['attrs', 'class', 'class_attr', 'iface_attr', 'kw', 'name']
        )
        self.assertEqual(
            node_data['class'],
            'node.tests.test_serializer.CustomInitNode'
        )
        self.assertEqual(node_data['name'], None)
        self.assertEqual(node_data['attrs'], {})
        self.assertEqual(node_data['kw'], {'a': 'A', 'b': 'B'})
        self.assertEqual(node_data['iface_attr'], None)
        self.assertEqual(node_data['class_attr'], None)

        node = deserialize(json_data)
        expected = '<CustomInitNode object \'None\' at'
        self.assertTrue(str(node).startswith(expected))
        self.assertEqual(node.a, 'A')
        self.assertEqual(node.b, 'B')

    ###########################################################################
    # Simplified serialization
    ###########################################################################

    def test_simplified(self):
        # Serialize node trees without type information. Such data is not
        # deserializable by default deserializer. Supposed to be used for
        # domain specific (Browser-) applications dealing with node data
        node = BaseNode(name='base')
        child = node['child'] = AttributedNode()
        child.attrs['foo'] = 'Foo'
        child.attrs['ref'] = AbstractNode

        # If all nodes are the same type, call ``serialize`` with
        # ``simple_mode=True``
        json_data = serialize(node, simple_mode=True)
        data = json.loads(json_data)
        self.assertEqual(sorted(list(data.keys())), ['children', 'name'])
        self.assertEqual(data['name'], 'base')
        self.assertEqual(len(data['children']), 1)

        child_data = data['children'][0]
        self.assertEqual(sorted(list(child_data.keys())), ['attrs', 'name'])
        self.assertEqual(child_data['name'], 'child')

        child_attrs = child_data['attrs']
        self.assertEqual(sorted(list(child_attrs.keys())), ['foo', 'ref'])
        self.assertEqual(child_attrs['foo'], 'Foo')
        self.assertEqual(child_attrs['ref'], 'node.base.AbstractNode')

        # If nodes are different types and you do not care about exposing the
        # class name, pass ``include_class=True`` to ``serialize``
        json_data = serialize(node, simple_mode=True, include_class=True)
        data = json.loads(json_data)
        self.assertEqual(
            sorted(list(data.keys())),
            ['children', 'class', 'name']
        )
        self.assertEqual(data['class'], 'node.base.BaseNode')
        self.assertEqual(data['name'], 'base')
        self.assertEqual(len(data['children']), 1)

        child_data = data['children'][0]
        self.assertEqual(
            sorted(list(child_data.keys())),
            ['attrs', 'class', 'name']
        )
        self.assertEqual(child_data['class'], 'node.base.AttributedNode')
        self.assertEqual(child_data['name'], 'child')

        child_attrs = child_data['attrs']
        self.assertEqual(sorted(list(child_attrs.keys())), ['foo', 'ref'])
        self.assertEqual(child_attrs['foo'], 'Foo')
        self.assertEqual(child_attrs['ref'], 'node.base.AbstractNode')
