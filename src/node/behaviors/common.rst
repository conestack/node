Common Behaviors
================

Adopt
-----

General imports.::

    >>> from plumber import plumber
    >>> from node.testing.env import MockupNode
    >>> from node.testing.env import NoNode

A dictionary is used as end point.::

    >>> from node.behaviors import Adopt
    >>> class AdoptingDict(dict):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Adopt

    >>> ad = AdoptingDict()

The mockup node is adopted.::

    >>> node = MockupNode()
    >>> ad['foo'] = node
    >>> ad['foo'] is node
    True
    >>> node.__name__
    'foo'
    >>> node.__parent__ is ad
    True

The non-node object is not adopted.::

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
instead of just naming the plumbing init eg plumbing__init__.::

    >>> class FakeDict(object):
    ...     def __setitem__(self, key, val):
    ...         raise KeyError(key)
    ...     def setdefault(self, key, default=None):
    ...         pass

    >>> class FailingAD(FakeDict):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Adopt

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
::
    >>> from node.behaviors import UnicodeAware, OdictStorage, Nodify
    >>> class UnicodeNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         Nodify,
    ...         UnicodeAware,
    ...         OdictStorage,
    ...     )
    
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
::
    >>> from node.behaviors import ChildFactory
    
    >>> class FooChild(object): pass
    >>> class BarChild(object): pass
    
    >>> class ChildFactoryNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Nodify, ChildFactory, OdictStorage
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
::
    >>> from node.behaviors import FixedChildren
    >>> class FixedChildrenNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = Nodify, FixedChildren
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

::
    >>> from plumber import plumber
    >>> from node.behaviors import UUIDAware, DefaultInit

Create a uid aware node. ``copy`` is not supported on UUIDAware node trees,
``deepcopy`` must be used::

    >>> class UUIDNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         Adopt,
    ...         DefaultInit,
    ...         Nodify,
    ...         OdictStorage,
    ...         UUIDAware,
    ...     )

UUID is set at init time::

    >>> root = UUIDNode(name='root')
    >>> root.uuid
    UUID('...')

Shallow ``copy`` is prohibited for UUID aware nodes::

    >>> root_cp = root.copy()
    Traceback (most recent call last):
      ...
    RuntimeError: Shallow copy useless on UUID aware node trees, use deepcopy.

On ``deepcopy``, a new uid gets set::

    >>> root_cp = root.deepcopy()
    >>> root is root_cp
    False
    
    >>> root.uuid == root_cp.uuid
    False

Create children, copy tree and check if all uuids have changed::

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

When detaching part of a tree, uid's are not changed::

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
::
    >>> from node.behaviors import (
    ...     NodeChildValidate,
    ...     Nodify,
    ...     OdictStorage,
    ... )
    
    >>> class NodeChildValidateNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = NodeChildValidate, DefaultInit, Nodify, OdictStorage
    
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

XXX: this test breaks coverage recording!!!::

    >>> from node.base import BaseNode
    >>> from node.behaviors import GetattrChildren

    >>> class Base(BaseNode):
    ...     allow_non_node_childs = True
    ...     baseattr = 1
    ...     def __getattr__(self, name):
    ...         if name is not "baseblend":
    ...             raise AttributeError("baseblend")
    ...         return "42"

    >>> class GetattrNode(Base):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = GetattrChildren
    ...     ourattr = 2

    >>> node = GetattrNode()
    >>> node['foo'] = 10
    >>> node['baseattr'] = 20
    >>> node['ourattr'] = 30

    >>> node['foo']
    10
    >>> node['baseattr']
    20
    >>> node['ourattr']
    30

Only children not shadowed by real attributes can be accessed via getattr::

    >>> node.foo
    10
    >>> node.baseattr
    1
    >>> node.ourattr
    2

XXX: The base class' getattr does not work anymore. plumber directive
     plumbor override could solve this together with support for multiple
     behaviors hooking into __getattr__. -cfl
     
     Thats why i prefer AttributeAccess explicit for attribute access on node
     children. overwriting __getattr__ and/or __getattribue__ cause too many
     side effects imo. -rn
