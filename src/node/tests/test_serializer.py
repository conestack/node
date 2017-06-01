from node import base
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


class TestSerializer(NodeTestCase):

    ###########################################################################
    # Node serialization
    ###########################################################################

    def test_INode_serialize_deserialize(self):
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

    def test_children_serialize_deserialize(self):
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

    def test_children_serialize_deserialize_as_list(self):
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
        json_data
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

"""
Attribute serialization
-----------------------

Serialize node implementing ``IAttributes``:

.. code-block:: pycon

    >>> node = AttributedNode(name='base')
    >>> node.attrs['int'] = 0
    >>> node.attrs['float'] = 0.0
    >>> node.attrs['str'] = 'str'
    >>> node.attrs['unset'] = UNSET
    >>> node.attrs['uuid'] = uuid.UUID('fcb30f5a-20c7-43aa-9537-2a25fef0248d')
    >>> node.attrs['list'] = [0, 0.0, 'str', UNSET]

    >>> json_data = serialize(node)
    >>> json_data
    '{"__node__": 
    {"attrs": 
    {"uuid": "<UUID>:fcb30f5a-20c7-43aa-9537-2a25fef0248d", 
    "int": 0, 
    "float": 0.0, 
    "list": [0, 0.0, "str", "<UNSET>"], 
    "str": "str", 
    "unset": "<UNSET>"}, 
    "class": "node.base.AttributedNode", 
    "name": "base"}}'

Deserialize node implementing ``IAttributes``:

.. code-block:: pycon

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.AttributedNode'>: base

    >>> node.attrs.printtree()
    <class 'node.behaviors.attributes.NodeAttributes'>: __attrs__
      uuid: UUID('fcb30f5a-20c7-43aa-9537-2a25fef0248d')
      int: 0
      float: 0.0
      list: [0, 0.0, u'str', <UNSET>]
      str: u'str'
      unset: <UNSET>


Referencing of classes, methods and functions
---------------------------------------------

Mock objects to reference:

.. code-block:: pycon

    >>> def referenced_function():
    ...     pass

    >>> base.referenced_function = referenced_function
    >>> referenced_function.__module__ = 'node.base'

    >>> class ReferencedClass(object):
    ...     def foo(self):
    ...         pass

    >>> base.ReferencedClass = ReferencedClass
    >>> ReferencedClass.__module__ = 'node.base'

Serialize and deserialize references:

.. code-block:: pycon

    >>> node = AttributedNode()
    >>> node.attrs['func'] = referenced_function
    >>> node.attrs['class'] = ReferencedClass
    >>> node.attrs['method'] = ReferencedClass.foo

    >>> json_data = serialize(node)
    >>> json_data
    '{"__node__": 
    {"attrs": 
    {"class": {"__ob__": "node.base.ReferencedClass"}, 
    "func": {"__ob__": "node.base.referenced_function"}, 
    "method": {"__ob__": "node.base.ReferencedClass.foo"}}, 
    "class": "node.base.AttributedNode", 
    "name": null}}'

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.AttributedNode'>: None

    >>> node.attrs.printtree()
    <class 'node.behaviors.attributes.NodeAttributes'>: __attrs__
      class: <class 'node.base.ReferencedClass'>
      func: <function referenced_function at ...>
      method: <unbound method ReferencedClass.foo>

Cleanup mock patches:

.. code-block:: pycon

    >>> del base.referenced_function
    >>> del base.ReferencedClass


Custom serializer
-----------------

Mock object used by class and interface bound serializers:

.. code-block:: pycon

    >>> class ICustomNode(Interface):
    ...     iface_attr = Attribute('Custom Attribute')

    >>> @implementer(ICustomNode)
    ... class CustomNode(AttributedNode):
    ...     iface_attr = None
    ...     class_attr = None

    >>> base.CustomNode = CustomNode
    >>> CustomNode.__module__ = 'node.base'

Interface bound custom serializer and deserializer:

.. code-block:: pycon

    >>> @serializer(ICustomNode)
    ... def serialize_custom_node(encoder, node, data):
    ...     data['iface_attr'] = node.iface_attr

    >>> @deserializer(ICustomNode)
    ... def deserialize_custom_node(encoder, node, data):
    ...     node.iface_attr = data['iface_attr']

    >>> node = base.CustomNode(name='custom')
    >>> node.iface_attr = 'Iface Attr Value'
    >>> json_data = serialize(node)
    >>> json_data
    '{"__node__": 
    {"iface_attr": "Iface Attr Value", 
    "attrs": {}, 
    "class": "node.base.CustomNode", 
    "name": "custom"}}'

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.CustomNode'>: custom

    >>> node.iface_attr
    u'Iface Attr Value'

    >>> node.class_attr

Class bound custom serializer and deserializer:

.. code-block:: pycon

    >>> @serializer(CustomNode)
    ... def serialize_custom_node(encoder, node, data):
    ...     data['class_attr'] = node.class_attr

    >>> @deserializer(CustomNode)
    ... def deserialize_custom_node(encoder, node, data):
    ...     node.class_attr = data['class_attr']

    >>> node = base.CustomNode(name='custom')
    >>> node.iface_attr = 'Iface Attr Value'
    >>> node.class_attr = 'Class Attr Value'

    >>> json_data = serialize(node)
    >>> json_data
    '{"__node__": 
    {"class_attr": "Class Attr Value", 
    "iface_attr": "Iface Attr Value", 
    "attrs": {}, 
    "class": "node.base.CustomNode", 
    "name": "custom"}}'

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.CustomNode'>: custom

    >>> node.iface_attr
    u'Iface Attr Value'

    >>> node.class_attr
    u'Class Attr Value'

Custom node constructor. Patch new constructor to ``CustomNode``:

.. code-block:: pycon

    >>> def custom_init(self, a, b):
    ...     self.a = a
    ...     self.b = b

    >>> CustomNode.__init__ = custom_init

Override class based custom serializer to export constructor arguments:

.. code-block:: pycon

    >>> @serializer(CustomNode)
    ... def serialize_custom_node(encoder, node, data):
    ...     data['class_attr'] = node.class_attr
    ...     data['kw'] = {
    ...         'a': node.a,
    ...         'b': node.b
    ...     }

Serialize and deserialize node with custom constructor:

.. code-block:: pycon

    >>> node = base.CustomNode(a='A', b='B')
    >>> json_data = serialize(node)
    >>> json_data
    '{"__node__": 
    {"name": null, 
    "iface_attr": null, 
    "class_attr": null, 
    "kw": {"a": "A", "b": "B"}, 
    "attrs": {}, 
    "class": "node.base.CustomNode"}}'

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.CustomNode'>: None

    >>> node.a
    u'A'

    >>> node.b
    u'B'

Cleanup mock patch:

.. code-block:: pycon

    >>> del base.CustomNode


Simplified serialization
------------------------

Serialize node trees without type information. Such data is not deserializable
by default deserializer. Supposed to be used for domain specific
(Browser-) applications dealing with node data:

.. code-block:: pycon

    >>> node = BaseNode(name='base')
    >>> child = node['child'] = AttributedNode()
    >>> child.attrs['foo'] = 'Foo'
    >>> child.attrs['ref'] = base.AbstractNode

If all nodes are the same type, call ``serialize`` with ``simple_mode=True``:

.. code-block:: pycon

    >>> serialize(node, simple_mode=True)
    '{"name": "base", 
    "children": 
    [{"name": "child", 
    "attrs": {"foo": "Foo", "ref": "node.base.AbstractNode"}}]}'

If nodes are different types and you do not care about exposing the class name,
pass ``include_class=True`` to ``serialize``:

.. code-block:: pycon

    >>> serialize(node, simple_mode=True, include_class=True)
    '{"children": 
    [{"attrs": {"foo": "Foo", "ref": "node.base.AbstractNode"}, 
    "class": "node.base.AttributedNode", 
    "name": "child"}], 
    "class": "node.base.BaseNode", 
    "name": "base"}'

"""