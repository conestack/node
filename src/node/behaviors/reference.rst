node.behaviors.Reference
------------------------

Tree node index.::

    >>> import copy
    >>> from plumber import plumber
    >>> from node.behaviors import (
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage,
    ...     Reference,
    ... )
    
    >>> class ReferenceNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         Adopt,
    ...         Reference,
    ...         DefaultInit,
    ...         Nodify,
    ...         OdictStorage,
    ...     )

    >>> node = ReferenceNode()
    >>> node.index
    <node.behaviors.reference.NodeIndex object at ...>

    >>> from zope.interface.common.mapping import IReadMapping
    >>> IReadMapping.providedBy(node.index)
    True

    >>> node.index[node.uuid]
    <ReferenceNode object 'None' ...>
    
    >>> node.index.get(node.uuid)
    <ReferenceNode object 'None' at ...>

    >>> node.uuid in node.index
    True

    >>> len(node.index._index)
    1

Add some children and check node containment stuff.::

    
    >>> node.__name__ = 'root'
    >>> node['child'] = ReferenceNode()
    >>> node['child'].path
    ['root', 'child']

    >>> node.index._index is node['child'].index._index
    True

    >>> len(node.index._index)
    2

    >>> node['child']['subchild'] = ReferenceNode()
    >>> len(node.index._index)
    3

    >>> node['child']['subchild2'] = ReferenceNode()
    >>> len(node.index._index)
    4

    >>> node.printtree()
    <class 'ReferenceNode'>: root
      <class 'ReferenceNode'>: child
        <class 'ReferenceNode'>: subchild
        <class 'ReferenceNode'>: subchild2

Adding in indexed Node with same uuid or the same node twice fails.::

    >>> child = node['child']
    >>> node['child2'] = child
    Traceback (most recent call last):
      ...
    ValueError: Node with uuid already exists

Check UUID stuff.::

    >>> uuid = node['child']['subchild'].uuid
    >>> uuid
    UUID('...')

    >>> node.node(uuid).path
    ['root', 'child', 'subchild']

    >>> node.uuid = uuid
    Traceback (most recent call last):
      ...
    ValueError: Given uuid was already used for another Node

    >>> import uuid
    >>> newuuid = uuid.uuid4()

    >>> node.uuid = newuuid
    >>> node['child'].node(newuuid).path
    ['root']

    >>> len(node._index.keys())
    4

Store the uuids of the nodes which are expected to be deleted from index if
child is deleted.::

    >>> delindexes = [
    ...     int(node['child'].uuid),
    ...     int(node['child']['subchild'].uuid),
    ...     int(node['child']['subchild2'].uuid),
    ... ]

Read the uuid index and check containment in index.::

    >>> iuuids = node._index.keys()
    >>> len(iuuids)
    4

    >>> delindexes[0] in iuuids
    True

    >>> delindexes[1] in iuuids
    True

    >>> delindexes[2] in iuuids
    True

Delete child. All checked uuids above must be deleted from index.::

    >>> del node['child']
    >>> node.keys()
    []

    >>> uuids = node._index.keys()
    >>> len(uuids)
    1

    >>> node.index[node.uuid] is node
    True

    >>> delindexes[0] in uuids
    False

    >>> delindexes[1] in uuids
    False

    >>> delindexes[2] in uuids
    False

    >>> node.printtree()
    <class 'ReferenceNode'>: root

    >>> node['child'] = ReferenceNode()
    
    >>> node['child'].allow_non_node_childs = True
    >>> node['child']['foo'] = 1
    
    >>> del node['child']
