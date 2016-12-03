JSON serialization
==================

Imports::

    >>> from node.base import AttributedNode
    >>> from node.base import BaseNode
    >>> from node.serializer import serialize
    >>> from node.serializer import deserialize
    >>> from node.utils import UNSET
    >>> import json


UNSET serialization
-------------------

``UNSET`` serializition::

    >>> json_data = serialize(UNSET)
    >>> json_data
    '{"__node_serializer__": "node.utils.UNSET"}'

    >>> deserialize(json_data)
    <UNSET>


Node serialization
------------------

Basic ``INode`` implementing object serializition::

    >>> json_data = serialize(BaseNode())
    >>> json_data
    '{"__node_serializer__": 
    {"__name__": null, "__class__": "node.base.BaseNode"}}'

    >>> deserialize(json_data)
    <BaseNode object 'None' at ...>

Node children serializition::

    >>> node = BaseNode(name='base')
    >>> node['child'] = BaseNode()
    >>> node['child']['sub'] = BaseNode()
    >>> node.printtree()
    <class 'node.base.BaseNode'>: base
      <class 'node.base.BaseNode'>: child
        <class 'node.base.BaseNode'>: sub

    >>> json_data = serialize(node)
    >>> json_data
    '{"__node_serializer__": 
    {"__name__": "base", 
    "__class__": "node.base.BaseNode", 
    "__children__": [{"__node_serializer__": 
    {"__name__": "child", 
    "__class__": "node.base.BaseNode", 
    "__children__": [{"__node_serializer__": 
    {"__name__": "sub", "__class__": "node.base.BaseNode"}}]}}]}}'

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.BaseNode'>: base
      <class 'node.base.BaseNode'>: child
        <class 'node.base.BaseNode'>: sub

Deserialize using diven root node::

    >>> root = BaseNode(name='root')
    >>> node = deserialize(json_data, root=root)
    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: base
        <class 'node.base.BaseNode'>: child
          <class 'node.base.BaseNode'>: sub
