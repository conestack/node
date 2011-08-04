Tests for original node from zodict.::

    >>> from node.interfaces import INode
    >>> from node.base import Node
    >>> root = Node('root')
    >>> root
    <Node object 'root' at ...>

    >>> INode.providedBy(root)
    True

    >>> root.__name__
    'root'

    >>> root.__parent__

    >>> root.path
    ['root']

    >>> root.index
    <node.parts.reference.NodeIndex object at ...>

    >>> root.index
    <node.parts.reference.NodeIndex object at ...>

    >>> from zope.interface.common.mapping import IReadMapping
    >>> IReadMapping.providedBy(root.index)
    True

    >>> root.index[root.uuid]
    <Node object 'root' at ...>

    >>> root.index.get(root.uuid)
    <Node object 'root' at ...>

    >>> root.uuid in root.index
    True

    >>> len(root.index._index)
    1

    >>> root['child'] = Node()
    >>> root['child'].path
    ['root', 'child']

    >>> root.index._index is root['child'].index._index
    True

    >>> len(root.index._index)
    2

    >>> root['child']['subchild'] = Node()
    >>> root['child']['subchild'].path
    ['root', 'child', 'subchild']

    >>> len(root.index._index)
    3

    >>> root['child']['subchild2'] = Node()
    >>> root.keys()
    ['child']

    >>> len(root.index._index)
    4

    # Non-Node "child" is not indexed
    >>> root['child']['subchild3'] = 1
    Traceback (most recent call last):
    ...
    ValueError: Non-node childs are not allowed.

    >>> root['child'].allow_non_node_childs = True
    >>> root['child']['subchild3'] = 1
    >>> root['child']['subchild3']
    1

    >>> len(root.index._index)
    4

    >>> root['child'].keys()
    ['subchild', 'subchild2', 'subchild3']

    >>> root['child'].items()
    [('subchild', <Node object 'subchild' at ...>),
    ('subchild2', <Node object 'subchild2' at ...>),
    ('subchild3', 1)]

    >>> child = root['child']
    >>> child.__name__
    'child'

    >>> child.__parent__
    <Node object 'root' at ...>

    >>> len(root['child'].keys())
    3

    >>> root.printtree()
    <class 'node.base.Node'>: root
      <class 'node.base.Node'>: child
        <class 'node.base.Node'>: subchild
        <class 'node.base.Node'>: subchild2
      1

    >>> child = root['child']
    >>> root['child2'] = child
    Traceback (most recent call last):
      ...
    ValueError: Node with uuid already exists

    >>> del root['non-existent']
    Traceback (most recent call last):
    ...
    KeyError: 'non-existent'

    >>> class SomeClass(Node):
    ...     """for testing"""
    >>> root['aclasshere'] = SomeClass
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.

    >>> from zope.interface import Interface
    >>> from zope.interface import alsoProvides
    >>> class IMarker(Interface): pass
    >>> alsoProvides(root['child']['subchild'], IMarker)
    >>> IMarker.providedBy(root['child']['subchild'])
    True

    >>> for item in root['child'].filtereditems(IMarker):
    ...     print item.path
    ['root', 'child', 'subchild']

    >>> len(root._index.keys())
    4

    >>> uuid = root['child']['subchild'].uuid
    >>> uuid
    UUID('...')

    >>> root.node(uuid).path
    ['root', 'child', 'subchild']

    >>> root.uuid = uuid
    Traceback (most recent call last):
      ...
    ValueError: Given uuid was already used for another Node

    >>> import uuid
    >>> newuuid = uuid.uuid4()

    >>> root.uuid = newuuid
    >>> root['child'].node(newuuid).path
    ['root']

    >>> len(root._index.keys())
    4

    >>> delindexes = [
    ...     int(root['child'].uuid),
    ...     int(root['child']['subchild'].uuid),
    ...     int(root['child']['subchild2'].uuid),
    ... ]

    >>> iuuids = root._index.keys()
    >>> len(iuuids)
    4

    >>> delindexes[0] in iuuids
    True

    >>> delindexes[1] in iuuids
    True

    >>> delindexes[2] in iuuids
    True

    >>> del root['child']
    >>> root.keys()
    []

    >>> uuids = root._index.keys()
    >>> len(uuids)
    1

    >>> root.index[root.uuid] is root
    True

    >>> delindexes[0] in uuids
    False

    >>> delindexes[1] in uuids
    False

    >>> delindexes[2] in uuids
    False

    >>> root.printtree()
    <class 'node.base.Node'>: root

    >>> root['child1'] = Node()
    >>> root['child2'] = Node()
    >>> root.printtree()
    <class 'node.base.Node'>: root
      <class 'node.base.Node'>: child1
      <class 'node.base.Node'>: child2

    >>> node = Node()
    >>> root.insertbefore(node, root['child1'])
    Traceback (most recent call last):
      ...
    ValueError: Given node has no __name__ set.

    >>> root.insertbefore(root['child2'], root['child1'])
    Traceback (most recent call last):
      ...
    KeyError: u'Given node already contained in tree.'

    >>> node.__name__ = 'child3'
    >>> root.insertbefore(node, root['child2'])
    >>> root.printtree()
    <class 'node.base.Node'>: root
      <class 'node.base.Node'>: child1
      <class 'node.base.Node'>: child3
      <class 'node.base.Node'>: child2

    >>> node = Node('child4')
    >>> root.insertafter(node, root['child3'])
    >>> root.printtree()
    <class 'node.base.Node'>: root
      <class 'node.base.Node'>: child1
      <class 'node.base.Node'>: child3
      <class 'node.base.Node'>: child4
      <class 'node.base.Node'>: child2

    >>> node = Node('child5')
    >>> root.insertafter(node, root['child2'])
    >>> root.printtree()
    <class 'node.base.Node'>: root
      <class 'node.base.Node'>: child1
      <class 'node.base.Node'>: child3
      <class 'node.base.Node'>: child4
      <class 'node.base.Node'>: child2
      <class 'node.base.Node'>: child5

    >>> len(root._index.keys())
    6

    >>> node = root.detach('child4')
    >>> node
    <Node object 'child4' at ...>

    >>> len(node._index.keys())
    1
    >>> len(root._index.keys())
    5

    >>> len(root.values())
    4

    >>> root.insertbefore(node, root['child1'])
    >>> root.printtree()
    <class 'node.base.Node'>: root
      <class 'node.base.Node'>: child4
      <class 'node.base.Node'>: child1
      <class 'node.base.Node'>: child3
      <class 'node.base.Node'>: child2
      <class 'node.base.Node'>: child5

    >>> tree1 = Node()
    >>> tree1['a'] = Node()
    >>> tree1['b'] = Node()
    >>> tree2 = Node()
    >>> tree2['d'] = Node()
    >>> tree2['e'] = Node()
    >>> tree1._index is tree2._index
    False

    >>> len(tree1._index.keys())
    3

    >>> tree1.printtree()
    <class 'node.base.Node'>: None
      <class 'node.base.Node'>: a
      <class 'node.base.Node'>: b

    >>> len(tree2._index.keys())
    3

    >>> tree2.printtree()
    <class 'node.base.Node'>: None
      <class 'node.base.Node'>: d
      <class 'node.base.Node'>: e

    >>> tree1['c'] = tree2
    >>> len(tree1._index.keys())
    6

    >> sorted(tree1._index.values(), key=lambda x: x.__name__)

    >>> tree1._index is tree2._index
    True

    >>> tree1.printtree()
    <class 'node.base.Node'>: None
      <class 'node.base.Node'>: a
      <class 'node.base.Node'>: b
      <class 'node.base.Node'>: c
        <class 'node.base.Node'>: d
        <class 'node.base.Node'>: e

    >>> sub = tree1.detach('c')
    >>> sub.printtree()
    <class 'node.base.Node'>: c
      <class 'node.base.Node'>: d
      <class 'node.base.Node'>: e

    >>> tree1._index is sub._index
    False

    >>> sub._index is sub['d']._index is sub['e']._index
    True

    >>> len(sub._index.keys())
    3

    >>> tree1.printtree()
    <class 'node.base.Node'>: None
      <class 'node.base.Node'>: a
      <class 'node.base.Node'>: b

    >>> len(tree1._index.keys())
    3

    >>> sub.__name__ = 'x'
    >>> tree1.insertbefore(sub, tree1['a'])
    >>> tree1.printtree()
    <class 'node.base.Node'>: None
      <class 'node.base.Node'>: x
        <class 'node.base.Node'>: d
        <class 'node.base.Node'>: e
      <class 'node.base.Node'>: a
      <class 'node.base.Node'>: b

    >>> tree1._index is sub._index
    True

    >>> len(tree1._index.keys())
    6

    >>> tree1.insertbefore(sub, tree1['a'])
    Traceback (most recent call last):
      ...
    KeyError: u'Given node already contained in tree.'

    >>> attraccess = root.as_attribute_access()
    >>> attraccess.child1
    <Node object 'child1' at ...>
