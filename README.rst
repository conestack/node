node
====

This package is the successor of `zodict <http://pypi.python.org/pypi/zodict>`_.


Overview
--------

Data structures could be described as tree. Some are by nature ``treeish``,
like XML documents, LDAP directories or filesystem directory trees, while others
could be treaten as. Consider SQL as example. A Database has tables, these
contain rows which contain columns.

Next, python has elegant ways for customizing all sorts of datamodel related
API. The `dictionary container type 
<http://docs.python.org/reference/datamodel.html#emulating-container-types>`_
fits almost completely the purpose of representing a node of a tree. The same
API is also described in ``zope.interface.common.mapping.IFullMapping``.
Additionaly a node must provide hierarchy information. In this case the
contract of ``zope.location.interfaces.ILocation`` is used.

Having data structures as such trees has some advantages:

- Unified data access API to different data models and/or sources

- Trees are traversable in both directions

- Once in memory, node trees are fast to deal with

- Software working on node trees may not need to know about internal data
  structures, as long as the node tree implementation provides the correct
  interface contracts


Usage
-----

``node`` ships with some "ready-to-import-and-use" nodes.

An unordered node. This can be used as base for trees where oder of items
doesn't matter.::

    >>> from node.base import BaseNode
    >>> root = BaseNode(name='root')
    >>> root['child'] = BaseNode()
    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: child

An ordered node. Order of items is preserved.::

    >>> from node.base import OrderedNode
    >>> root = OrderedNode(name='orderedroot')
    >>> root['foo'] = OrderedNode()
    >>> root['bar'] = OrderedNode()
    >>> root.printtree()
    <class 'node.base.OrderedNode'>: orderedroot
      <class 'node.base.OrderedNode'>: foo
      <class 'node.base.OrderedNode'>: bar
    
    >>> root.items()
    [('foo', <OrderedNode object 'foo' at ...>), 
    ('bar', <OrderedNode object 'bar' at ...>)]

A full API description of the node interface can be found at
``node.interfaces.INode``.


A more fine granular control of node functionality
--------------------------------------------------

``node`` utilizes the `plumber <http://pypi.python.org/pypi/plumber>`_ package.

Thus, different behaviors of nodes are provided by ``plumbing parts``. Read
the documentation of ``plumber`` for details about the plumbing system.

    >>> from plumber import plumber
    >>> from node.parts import (
    ...     Nodespaces,
    ...     Attributes,
    ...     Lifecycle,
    ...     NodeChildValidate,
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage,
    ... )
    
    >>> class CustomNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         Nodespaces,
    ...         Attributes,
    ...         Lifecycle,
    ...         NodeChildValidate,
    ...         Adopt,
    ...         DefaultInit,
    ...         Nodify,
    ...         OdictStorage,
    ...     )
    
    >>> dir(CustomNode)
    ['__class__', '__contains__', '__delattr__', '__delitem__',
    '__dict__', '__doc__', '__format__', '__getattribute__',
    '__getitem__', '__hash__', '__implemented__', '__init__',
    '__iter__', '__len__', '__metaclass__', '__module__', '__name__',
    '__new__', '__nonzero__', '__parent__', '__plumbing__',
    '__plumbing_stacks__', '__provides__', '__reduce__',
    '__reduce_ex__', '__repr__', '__setattr__', '__setitem__',
    '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
    '_nodespaces', '_notify_suppress', 'allow_non_node_childs',
    'attribute_access_for_attrs', 'attributes', 'attributes_factory',
    'attrs', 'clear', 'copy', 'detach', 'events', 'filtereditems',
    'filtereditervalues', 'filteredvalues', 'get', 'has_key', 'items',
    'iteritems', 'iterkeys', 'itervalues', 'keys', 'name', 'noderepr',
    'nodespaces', 'parent', 'path', 'pop', 'popitem', 'printtree',
    'root', 'setdefault', 'storage', 'update', 'values']

As ``dir`` call shows,  ``CustomNode`` class was plumbed using given parts, now
defining a complete ``INode`` implementation with some additional behaviours
and is now ready to use::

    >>> node = CustomNode()
    >>> node['child'] = CustomNode()
    >>> node.printtree()
    <class 'CustomNode'>: None
      <class 'CustomNode'>: child
    
    >>> from node.interfaces import INode
    >>> INode.providedBy(node)
    True


Parts
-----

``node`` package provides several plumbing parts:

node.parts.DefaultInit
    Plumbing part providing default ``__init__`` function on node.
    See ``node.interfaces.IDefaultInit``.

node.parts.Nodify
    Plumbing part to Fill in gaps for full INode API.
    See ``node.interfaces.INodify``.

node.parts.Adopt
    Plumbing part that provides adoption of children.
    See ``node.interfaces.IAdopt``.

node.parts.NodeChildValidate
    Plumbing part for child node validation.
    See ``node.interfaces.INodeChildValidate``.

node.parts.UnicodeAware
    Plumbing part to ensure unicode for keys and string values.
    See ``node.interfaces.IUnicodeAware``.

node.parts.Alias
    Plumbing part that provides aliasing of child keys.
    See ``node.interfaces.IAlias``.

node.parts.AsAttrAccess
    Plumbing part to get node as IAttributeAccess implementation.
    See ``node.interfaces.IAsAttrAccess``.

node.parts.FixedChildren
    Plumbing part that initializes a fixed dictionary as children.
    See ``node.interfaces.IFixedChildren``.

node.parts.GetattrChildren
    Plumbing part for child access via ``__getattr__``, given the attribute
    name is unused.
    See ``node.interfaces.IGetattrChildren``.

node.parts.Nodespaces
    Plumbing part for providing nodespaces on node.
    See ``node.interfaces.INodespaces``.

node.parts.Attributes
    Plumbing part to provide attributes on node.
    Requires ``node.parts.Nodespaces`` part.
    See ``node.interfaces.IAttributes``.

node.parts.Lifecycle
    Plumbing part taking care of lifecycle events.
    See ``node.interfaces.ILifecycle``.

node.parts.AttributesLifecycle
    Plumbing part for handling ifecycle events at attributes manipulation.
    See ``node.interfaces.IAttributesLifecycle``.

node.parts.Invalidate
    Plumbing part for node invalidation.
    See ``node.interfaces.Invalidate``.

node.parts.Cache
    Plumbing part for caching.
    See ``node.interfaces.ICache``.

node.parts.Order
    Plumbing part for ordering support.
    See ``node.interfaces.IOrder``.

node.parts.Reference
    Plumbing part holding an index of all nodes contained in the tree.
    See ``node.interfaces.IReference``.

node.parts.DictStorage
    Provide dictionary storage.
    See ``node.interfaces.IStorage``.

node.parts.OdictStorage
    Provide ordered dictionary storage.
    See ``node.interfaces.IStorage``.


Migration
---------

A node which behaves like ``zodict.Node`` is contained at ``node.base.Node``.
This node is supposed to be used for migration from zodict.

It's also useful to take a look of which parts the original node is build of.

Probably an implementation does not need all the parts at once. In this case
define the node plumbing directly on node class instead of inheriting from
``node.base.Node``.


TestCoverage
------------

Summary of the test coverage report::

  lines   cov%   module
    106    72%   node.aliasing
     53   100%   node.base
     14   100%   node.events
    125   100%   node.interfaces
     23   100%   node.locking
     11   100%   node.parts.__init__
     46   100%   node.parts.alias
     38   100%   node.parts.attributes
     50   100%   node.parts.cache
     83   100%   node.parts.common
     52   100%   node.parts.lifecycle
    113   100%   node.parts.mapping
     31   100%   node.parts.nodespace
     70   100%   node.parts.nodify
     65   100%   node.parts.order
     81   100%   node.parts.reference
     27   100%   node.parts.storage
      1   100%   node.testing.__init__
     62   100%   node.testing.base
    214   100%   node.testing.fullmapping
      1   100%   node.tests.__init__
     19   100%   node.tests.env
     31   100%   node.tests.test_node
    109   100%   node.utils


Contributors
============

- Robert Niederreiter <rnix@squarewave.at>
- Florian Friesdorf <flo@chaoflow.net>
- Jens Klein <jens@bluedynamics.com>


Changes
=======

0.9.3
-----

- Increase test coverage
  [rnix, 2011-05-09]

- Add interfaces ``IFixedChildren`` and ``IGetattrChildren`` for related parts.
  [rnix, 2011-05-09]

- Rename ``Unicode`` part to ``UnicodeAware``.
  [rnix, 2011-05-09]

- Add ``node.utils.StrCodec``.
  [rnix, 2011-05-09]

- Inherit ``INodify`` interface from ``INode``.
  [rnix, 2011-05-08]

- Locking tests. Add ``time.sleep`` after thread start.
  [rnix, 2011-05-08]

- Cleanup ``BaseTester``, remove ``sorted_output`` flag (always sort), also 
  search class bases for detection in ``wherefrom``.
  [rnix, 2011-05-08]

- Remove useless try/except in ``utils.AttributeAccess``.
  [rnix, 2011-05-08]

- Add ``instance_property`` decorator to utils.
  [rnix, 2011-05-06]

- Add ``FixedChildren`` and ``GetattrChildren`` parts.
  [chaoflow, 2011-04-22]


0.9.2
-----

- Add ``__nonzero__`` on ``Nodifiy`` part always return True.
  [rnix, 2011-03-15]


0.9.1
-----

- Provide ``node.base.Node`` with same behavior like ``zodict.Node`` for
  migration purposes.
  [rnix, 2011-02-08]


0.9
---

- Make it work [rnix, chaoflow, et al]
