JSON serialization
==================

Imports:

.. code-block:: pycon

    >>> from node import base
    >>> from node.base import AttributedNode
    >>> from node.base import BaseNode
    >>> from node.serializer import serialize
    >>> from node.serializer import serializer
    >>> from node.serializer import deserialize
    >>> from node.serializer import deserializer
    >>> from node.utils import UNSET
    >>> from zope.interface import Attribute
    >>> from zope.interface import Interface
    >>> from zope.interface import implementer
    >>> import json
    >>> import uuid


Node serialization
------------------

Basic ``INode`` implementing object serializition:

.. code-block:: pycon

    >>> json_data = serialize(BaseNode())
    >>> json_data
    '{"__node__": 
    {"class": "node.base.BaseNode", 
    "name": null}}'

    >>> deserialize(json_data)
    <BaseNode object 'None' at ...>

Node children serializition:

.. code-block:: pycon

    >>> node = BaseNode(name='base')
    >>> node['child'] = BaseNode()
    >>> node['child']['sub'] = BaseNode()
    >>> node.printtree()
    <class 'node.base.BaseNode'>: base
      <class 'node.base.BaseNode'>: child
        <class 'node.base.BaseNode'>: sub

    >>> json_data = serialize(node)
    >>> json_data
    '{"__node__": 
    {"children": [{"__node__": 
    {"children": [{"__node__": 
    {"class": "node.base.BaseNode", 
    "name": "sub"}}], 
    "class": "node.base.BaseNode", 
    "name": "child"}}], 
    "class": "node.base.BaseNode", 
    "name": "base"}}'

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.BaseNode'>: base
      <class 'node.base.BaseNode'>: child
        <class 'node.base.BaseNode'>: sub

Deserialize using given root node:

.. code-block:: pycon

    >>> root = BaseNode(name='root')
    >>> node = deserialize(json_data, root=root)
    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: base
        <class 'node.base.BaseNode'>: child
          <class 'node.base.BaseNode'>: sub

Serialize list of nodes:

.. code-block:: pycon

    >>> node = BaseNode(name='base')
    >>> node['child_1'] = BaseNode()
    >>> node['child_2'] = BaseNode()
    >>> node.printtree()
    <class 'node.base.BaseNode'>: base
      <class 'node.base.BaseNode'>: child_1
      <class 'node.base.BaseNode'>: child_2

    >>> json_data = serialize(node.values())
    >>> json_data
    '[{"__node__": 
    {"class": "node.base.BaseNode", 
    "name": "child_1"}}, 
    {"__node__": 
    {"class": "node.base.BaseNode", 
    "name": "child_2"}}]'

Deserialize list of nodes using given root node:

.. code-block:: pycon

    >>> root = BaseNode(name='root')
    >>> nodes = deserialize(json_data, root=root)
    >>> nodes
    [<BaseNode object 'child_1' at ...>, 
    <BaseNode object 'child_2' at ...>]

    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: child_1
      <class 'node.base.BaseNode'>: child_2


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
