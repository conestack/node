JSON serialization
==================

Imports::

    >>> from node.base import AttributedNode
    >>> from node.base import BaseNode
    >>> from node.serializer import serialize
    >>> from node.serializer import deserialize
    >>> from node.utils import UNSET
    >>> import json
    >>> import uuid

``UNSET`` serializition::

    >>> json_data = serialize(UNSET)
    >>> json_data
    '"<UNSET>"'

    >>> deserialize(json_data)
    <UNSET>

Basic ``INode`` implementing object serializition::

    >>> json_data = serialize(BaseNode())
    >>> json_data
    '{"__node__": 
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
    '{"__node__": 
    {"__name__": "base", 
    "__class__": "node.base.BaseNode", 
    "__children__": [{"__node__": 
    {"__name__": "child", 
    "__class__": "node.base.BaseNode", 
    "__children__": [{"__node__": 
    {"__name__": "sub", "__class__": "node.base.BaseNode"}}]}}]}}'

    >>> node = deserialize(json_data)
    >>> node.printtree()
    <class 'node.base.BaseNode'>: base
      <class 'node.base.BaseNode'>: child
        <class 'node.base.BaseNode'>: sub

Deserialize using given root node::

    >>> root = BaseNode(name='root')
    >>> node = deserialize(json_data, root=root)
    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: base
        <class 'node.base.BaseNode'>: child
          <class 'node.base.BaseNode'>: sub

Serialize node implementing ``IAttributes``::

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
    {"__name__": "base", 
    "__class__": "node.base.AttributedNode", 
    "__attrs__": 
    {"uuid": "<UUID>:fcb30f5a-20c7-43aa-9537-2a25fef0248d", 
    "int": 0, 
    "float": 0.0, 
    "list": [0, 0.0, "str", "<UNSET>"], 
    "str": "str", 
    "unset": "<UNSET>"}}}'

Deserialize node implementing ``IAttributes``::

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
