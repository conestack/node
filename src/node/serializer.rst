JSON serialization
==================

Imports::

    >>> from node.base import AttributedNode
    >>> from node.base import BaseNode
    >>> from node.serializer import NodeDecoder
    >>> from node.serializer import NodeEncoder
    >>> from node.utils import UNSET
    >>> import json


UNSET serialization
-------------------

``UNSET`` serializition and deserialization::

    >>> json_UNSET = json.dumps(UNSET, cls=NodeEncoder)
    >>> json_UNSET
    '{"__node_serializer__": "node.utils.UNSET"}'

    >>> json.loads(json_UNSET, object_hook=NodeDecoder())
    <UNSET>


Node serialization
------------------

Basic ``BaseNode`` serializition and deserialization::

    >>> json_node = json.dumps(BaseNode(), cls=NodeEncoder)
    >>> json_node
    '{"__node_serializer__": 
    {"__name__": null, "__class__": "node.base.BaseNode"}}'

    >>> json.loads(json_node, object_hook=NodeDecoder())
    <BaseNode object 'None' at ...>
