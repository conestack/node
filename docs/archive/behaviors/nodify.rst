Nodify
------

.. code-block:: pycon

    >>> from plumber import plumbing

    >>> from node.testing import FullMappingTester
    >>> from node.behaviors import Adopt
    >>> from node.behaviors import DictStorage
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Nodify

    >>> @plumbing(
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     DictStorage)
    ... class Node(object):
    ...     pass

    >>> root = Node(name='root')
    >>> root['child'] = Node()
    >>> root.name
    'root'

    >>> root.parent

    >>> child = root['child']
    >>> child.name
    'child'

    >>> child.parent
    <Node object 'root' at ...>

    >>> root.printtree()
    <class 'Node'>: root
      <class 'Node'>: child

    >>> bool(root)
    True

    >>> tester = FullMappingTester(Node)
    >>> tester.run()
    >>> tester.combined
    ``__contains__``: OK
    ``__delitem__``: OK
    ``__getitem__``: OK
    ``__iter__``: OK
    ``__len__``: OK
    ``__setitem__``: OK
    ``clear``: OK
    ``copy``: OK
    ``get``: OK
    ``has_key``: OK
    ``items``: OK
    ``iteritems``: OK
    ``iterkeys``: OK
    ``itervalues``: OK
    ``keys``: OK
    ``pop``: OK
    ``popitem``: OK
    ``setdefault``: OK
    ``update``: OK
    ``values``: OK

    >>> class RootNode(Node):
    ...     pass

    >>> root = RootNode('root')
    >>> child = root['child'] = Node()
    >>> subchild = child['subchild'] = Node()
    >>> root.printtree()
    <class 'RootNode'>: root
      <class 'Node'>: child
        <class 'Node'>: subchild

    >>> root[u'ö'] = Node()
    >>> root.printtree()
    <class 'RootNode'>: root
      <class 'Node'>: ??
      <class 'Node'>: child
        <class 'Node'>: subchild

    >>> repr(root[u'ö'])
    "<Node object '??' at ...>"

    >>> from zope.interface import Interface
    >>> from zope.interface import alsoProvides
    >>> from node.interfaces import INode

    >>> class INodeInterface(Interface):
    ...     pass

    >>> class INoInterface(Interface):
    ...     pass

    >>> alsoProvides(child, INodeInterface)
    >>> subchild.acquire(RootNode)
    <RootNode object 'root' at ...>

    >>> subchild.acquire(INodeInterface)
    <Node object 'child' at ...>

    >>> subchild.acquire(INode)
    <Node object 'child' at ...>

    >>> subchild.acquire(INoInterface)
