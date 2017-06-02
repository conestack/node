Common Behaviors
================

Adopt
-----

General imports:

.. code-block:: pycon

    >>> from plumber import plumbing
    >>> from node.testing.env import MockupNode
    >>> from node.testing.env import NoNode

A dictionary is used as end point:

.. code-block:: pycon

    >>> from node.behaviors import Adopt

    >>> @plumbing(Adopt)
    ... class AdoptingDict(dict):
    ...     pass

    >>> ad = AdoptingDict()

The mockup node is adopted:

.. code-block:: pycon

    >>> node = MockupNode()
    >>> ad['foo'] = node
    >>> ad['foo'] is node
    True
    >>> node.__name__
    'foo'
    >>> node.__parent__ is ad
    True

The non-node object is not adopted:

.. code-block:: pycon

    >>> nonode = NoNode()
    >>> ad['bar'] = nonode
    >>> ad['bar'] is nonode
    True
    >>> hasattr(nonode, '__name__')
    False
    >>> hasattr(nonode, '__parent__')
    False

If something goes wrong, the adoption does not happen.  See plumbing.Adopt for
exceptions that are handled.

XXX: In case this should be configurable, it would be nice if a plumbing
element could be instatiated which is currently not possible. It would be
possible by defining the plumbing __init__ method with a different name.
Maybe it is also possible to have two __init__ one decorated one not, if the
plumbing decorator could influence that all plumbing functions are stored under
a different name. If the decorator cannot do that a Plumbing metaclass will
work for sure, however, it is questionable whether it justifies a metaclass
instead of just naming the plumbing init eg plumbing__init__:

.. code-block:: pycon

    >>> class FakeDict(object):
    ...     def __setitem__(self, key, val):
    ...         raise KeyError(key)
    ...     def setdefault(self, key, default=None):
    ...         pass

    >>> @plumbing(Adopt)
    ... class FailingAD(FakeDict):
    ...     pass

    >>> fail = FailingAD()
    >>> node = MockupNode()
    >>> fail['foo'] = node
    Traceback (most recent call last):
    ...
    KeyError: 'foo'
    >>> node.__name__ is None
    True
    >>> node.__parent__ is None
    True


UnicodeAware
------------

.. code-block:: pycon

    >>> from node.behaviors import UnicodeAware
    >>> from node.behaviors import OdictStorage
    >>> from node.behaviors import Nodify

    >>> @plumbing(Nodify, UnicodeAware, OdictStorage)
    ... class UnicodeNode(object):
    ...     pass

    >>> node = UnicodeNode()
    >>> node['foo'] = UnicodeNode()
    >>> node.keys()
    [u'foo']

    >>> node['bar'] = 'bar'
    >>> node.items()
    [(u'foo', <UnicodeNode object 'None' at ...>), (u'bar', u'bar')]

    >>> node['foo']
    <UnicodeNode object 'None' at ...>

    >>> del node['bar']
    >>> node.keys()
    [u'foo']


ChildFactory
------------

.. code-block:: pycon

    >>> from node.behaviors import ChildFactory

    >>> class FooChild(object): pass
    >>> class BarChild(object): pass

    >>> @plumbing(Nodify, ChildFactory, OdictStorage)
    ... class ChildFactoryNode(object):
    ...     factories = {
    ...         'foo': FooChild,
    ...         'bar': BarChild,
    ...     }
    >>> node = ChildFactoryNode()
    >>> node.items()
    [('foo', <FooChild object at ...>), 
    ('bar', <BarChild object at ...>)]


FixedChildren
-------------

.. code-block:: pycon

    >>> from node.behaviors import FixedChildren

    >>> @plumbing(Nodify, FixedChildren)
    ... class FixedChildrenNode(object):
    ...     fixed_children_factories = (
    ...         ('foo', FooChild),
    ...         ('bar', BarChild),
    ...         )

    >>> node = FixedChildrenNode()
    >>> node.keys()
    ['foo', 'bar']

    >>> node['foo']
    <FooChild object at ...>

    >>> node['bar']
    <BarChild object at ...>

    >>> node['foo'] is node['foo']
    True

    >>> del node['foo']
    Traceback (most recent call last):
      ...
    NotImplementedError: read-only

    >>> node['foo'] = 'foo'
    Traceback (most recent call last):
      ...
    NotImplementedError: read-only


UUIDAware
---------

.. code-block:: pycon

    >>> from node.behaviors import UUIDAware
    >>> from node.behaviors import DefaultInit

Create a uid aware node. ``copy`` is not supported on UUIDAware node trees,
``deepcopy`` must be used:

.. code-block:: pycon

    >>> @plumbing(
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage,
    ...     UUIDAware)
    ... class UUIDNode(object):
    ...     pass

UUID is set at init time:

.. code-block:: pycon

    >>> root = UUIDNode(name='root')
    >>> root.uuid
    UUID('...')

Shallow ``copy`` is prohibited for UUID aware nodes:

.. code-block:: pycon

    >>> root_cp = root.copy()
    Traceback (most recent call last):
      ...
    RuntimeError: Shallow copy useless on UUID aware node trees, use deepcopy.

On ``deepcopy``, a new uid gets set:

.. code-block:: pycon

    >>> root_cp = root.deepcopy()
    >>> root is root_cp
    False

    >>> root.uuid == root_cp.uuid
    False

Create children, copy tree and check if all uuids have changed:

.. code-block:: pycon

    >>> c1 = root['c1'] = UUIDNode()
    >>> s1 = c1['s1'] = UUIDNode()
    >>> root.printtree()
    <class 'UUIDNode'>: root
      <class 'UUIDNode'>: c1
        <class 'UUIDNode'>: s1

    >>> root_cp = root.deepcopy()
    >>> root_cp.printtree()
    <class 'UUIDNode'>: root
      <class 'UUIDNode'>: c1
        <class 'UUIDNode'>: s1

    >>> root.uuid == root_cp.uuid
    False

    >>> root['c1'].uuid == root_cp['c1'].uuid
    False

    >>> root['c1']['s1'].uuid == root_cp['c1']['s1'].uuid
    False

When detaching part of a tree, uid's are not changed:

.. code-block:: pycon

    >>> c1_uid = root['c1'].uuid
    >>> s1_uid = root['c1']['s1'].uuid
    >>> detached = root.detach('c1')

    >>> root.printtree()
    <class 'UUIDNode'>: root

    >>> detached.printtree()
    <class 'UUIDNode'>: c1
      <class 'UUIDNode'>: s1

    >>> c1_uid == detached.uuid
    True

    >>> s1_uid == detached['s1'].uuid
    True


NodeChildValidate
-----------------

.. code-block:: pycon

    >>> from node.behaviors import NodeChildValidate
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage

    >>> @plumbing(NodeChildValidate, DefaultInit, Nodify, OdictStorage)
    ... class NodeChildValidateNode(object):
    ...     pass

    >>> node = NodeChildValidateNode()
    >>> node.allow_non_node_childs
    False

    >>> node['child'] = 1
    Traceback (most recent call last):
      ...
    ValueError: Non-node childs are not allowed.

    >>> class SomeClass(object): pass

    >>> node['aclasshere'] = SomeClass
    Traceback (most recent call last):
      ...
    ValueError: It isn't allowed to use classes as values.

    >>> node.allow_non_node_childs = True

    >>> node['child'] = 1
    >>> node['child']
    1


GetattrChildren
---------------

XXX: this test breaks coverage recording!!!:

.. code-block:: pycon

    >>> from node.base import BaseNode
    >>> from node.behaviors import GetattrChildren

    >>> class GetattrBase(BaseNode):
    ...     allow_non_node_childs = True
    ...     baseattr = 1

    >>> @plumbing(GetattrChildren)
    ... class GetattrNode(GetattrBase):
    ...     ourattr = 2

    >>> node = GetattrNode()
    >>> node['foo'] = 10
    >>> node['baseattr'] = 20
    >>> node['ourattr'] = 30

    >>> assert(node['foo'] == 10)
    >>> assert(node['baseattr'] == 20)
    >>> assert(node['ourattr'] == 30)

Only children not shadowed by real attributes can be accessed via getattr:

.. code-block:: pycon

    >>> assert(node.foo == 10)
    >>> assert(node.baseattr == 1)
    >>> assert(node.ourattr == 2)
