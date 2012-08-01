node
====

This package is the successor of `zodict <http://pypi.python.org/pypi/zodict>`_.


Overview
--------

Data structures could be described as tree. Some are by nature ``treeish``,
like XML documents, LDAP directories or filesystem directory trees, while others
could be treaten as.

Further, python has elegant ways for customizing all sorts of datamodel related
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
doesn't matter::

    >>> from node.base import BaseNode
    >>> root = BaseNode(name='root')
    >>> root['child'] = BaseNode()
    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: child

An ordered node. Order of items is preserved::

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

Thus, different behaviors of nodes are provided by ``plumbing behaviors``. Read
the documentation of ``plumber`` for details about the plumbing system::

    >>> from plumber import plumber
    >>> from node.behaviors import (
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
    '_nodespaces', '_notify_suppress', 'acquire', 'allow_non_node_childs', 
    'attribute_access_for_attrs', 'attributes', 'attributes_factory', 
    'attrs', 'clear', 'copy', 'deepcopy', 'detach', 'events', 'filtereditems', 
    'filtereditervalues', 'filteredvalues', 'get', 'has_key', 'items', 
    'iteritems', 'iterkeys', 'itervalues', 'keys', 'name', 'noderepr', 
    'nodespaces', 'parent', 'path', 'pop', 'popitem', 'printtree', 
    'root', 'setdefault', 'storage', 'update', 'values']

As ``dir`` call shows,  ``CustomNode`` class was plumbed using given behaviors,
now defining a complete ``INode`` implementation with some additional
behaviours and is now ready to use::

    >>> node = CustomNode()
    >>> node['child'] = CustomNode()
    >>> node.printtree()
    <class 'CustomNode'>: None
      <class 'CustomNode'>: child
    
    >>> from node.interfaces import INode
    >>> INode.providedBy(node)
    True


Behaviors
---------

``node`` package provides several plumbing behaviors:

node.behaviors.DefaultInit
    Plumbing part providing default ``__init__`` function on node.
    See ``node.interfaces.IDefaultInit``.

node.behaviors.Nodify
    Plumbing part to Fill in gaps for full INode API.
    See ``node.interfaces.INodify``.

node.behaviors.Adopt
    Plumbing part that provides adoption of children.
    See ``node.interfaces.IAdopt``.

node.behaviors.NodeChildValidate
    Plumbing part for child node validation.
    See ``node.interfaces.INodeChildValidate``.

node.behaviors.UnicodeAware
    Plumbing part to ensure unicode for keys and string values.
    See ``node.interfaces.IUnicodeAware``.

node.behaviors.Alias
    Plumbing part that provides aliasing of child keys.
    See ``node.interfaces.IAlias``.

node.behaviors.AsAttrAccess
    Plumbing part to get node as IAttributeAccess implementation.
    See ``node.interfaces.IAsAttrAccess``.

node.behaviors.ChildFactory
    Plumbing part providing child factories which are invoked at
    ``__getitem__`` if object by key is not present at plumbing endpoint yet.
    See ``node.interfaces.IChildFactory``.

node.behaviors.FixedChildren
    Plumbing part that initializes a fixed dictionary as children.
    See ``node.interfaces.IFixedChildren``.

node.behaviors.GetattrChildren
    Plumbing part for child access via ``__getattr__``, given the attribute
    name is unused.
    See ``node.interfaces.IGetattrChildren``.

node.behaviors.Nodespaces
    Plumbing part for providing nodespaces on node.
    See ``node.interfaces.INodespaces``.

node.behaviors.Attributes
    Plumbing part to provide attributes on node.
    Requires ``node.behaviors.Nodespaces`` part.
    See ``node.interfaces.IAttributes``.

node.behaviors.Lifecycle
    Plumbing part taking care of lifecycle events.
    See ``node.interfaces.ILifecycle``.

node.behaviors.AttributesLifecycle
    Plumbing part for handling ifecycle events at attributes manipulation.
    See ``node.interfaces.IAttributesLifecycle``.

node.behaviors.Invalidate
    Plumbing part for node invalidation.
    See ``node.interfaces.Invalidate``.

node.behaviors.Cache
    Plumbing part for caching.
    See ``node.interfaces.ICache``.

node.behaviors.Order
    Plumbing part for ordering support.
    See ``node.interfaces.IOrder``.

node.behaviors.UUIDAware
    Plumbing part providing a uuid on nodes.
    See ``node.interfaces.IUUIDAware``.

node.behaviors.Reference
    Plumbing part holding an index of all nodes contained in the tree.
    See ``node.interfaces.IReference``.

node.behaviors.Storage
    Provide abstract storage access.
    See ``node.interfaces.IStorage``.

node.behaviors.DictStorage
    Provide dictionary storage.
    See ``node.interfaces.IStorage``.

node.behaviors.OdictStorage
    Provide ordered dictionary storage.
    See ``node.interfaces.IStorage``.


Migration
---------

A node which behaves like ``zodict.Node`` is contained at ``node.base.Node``.
This node is supposed to be used for migration from zodict.

It's also useful to take a look of which behaviors the original node is build
of.

Probably an implementation does not need all the behaviors at once. In this case
define the node plumbing directly on node class instead of inheriting from
``node.base.Node``.


TestCoverage
------------

Summary of the test coverage report::

  lines   cov%   module
     62   100%   node.base
     34   100%   node.behaviors.__init__
    112   100%   node.behaviors.alias
     43   100%   node.behaviors.attributes
     53   100%   node.behaviors.cache
    132   100%   node.behaviors.common
     58   100%   node.behaviors.lifecycle
    125   100%   node.behaviors.mapping
     35   100%   node.behaviors.nodespace
     85   100%   node.behaviors.nodify
    112   100%   node.behaviors.order
     85   100%   node.behaviors.reference
     30   100%   node.behaviors.storage
     21   100%   node.events
    133   100%   node.interfaces
     23   100%   node.locking
      1   100%   node.testing.__init__
     62   100%   node.testing.base
     24   100%   node.testing.env
    215   100%   node.testing.fullmapping
     29   100%   node.tests
    121   100%   node.utils


Contributors
============

- Robert Niederreiter <rnix __at__ squarewave __dot__ at>

- Florian Friesdorf <flo __at__ chaoflow __dot__ net>

- Jens Klein <jens __at__ bluedynamics __dot__ com>


Changes
=======

0.9.8
-----

- Deprecate the use of ``node.parts``. Use ``node.behaviors`` instead.
  [rnix, 2012-07-28]

- Adopt to ``plumber`` 1.2
  [rnix, 2012-07-28]


0.9.7
-----

- Introduce ``node.interfaces.IOrdered`` Marker interface. Set this interface
  on ``node.parts.storage.OdictStorage``.
  [rnix, 2012-05-21]

- ``node.parts.mapping.ClonableMapping`` now supports ``deepcopy``.
  [rnix, 2012-05-18]

- Use ``zope.interface.implementer`` instead of ``zope.interface.implements``
  all over the place.
  [rnix, 2012-05-18]

- Remove superfluos interfaces.
  [rnix, 2012-05-18]

- Remove ``Zodict`` from ``node.utils``.
  [rnix, 2012-05-18]

- Remove ``AliasedNodespace``, use ``Alias`` part instead.
  [rnix, 2012-05-18]

- Move aliaser objects from ``node.aliasing`` to ``node.parts.alias``.
  [rnix, 2012-05-18]

- Remove ``composition`` module.
  [rnix, 2012-05-18]

- Remove ``bbb`` module.
  [rnix, 2012-05-18]


0.9.6
-----

- Do not inherit ``node.parts.Reference`` from ``node.parts.UUIDAware``.
  [rnix, 2012-01-30]

- Set ``uuid`` in ``node.parts.Reference.__init__`` plumb.
  [rnix, 2012-01-30]


0.9.5
-----

- add ``node.parts.nodify.Nodify.acquire`` function.
  [rnix, 2011-12-05]

- add ``node.parts.ChildFactory`` plumbing part.
  [rnix, 2011-12-04]

- add ``node.parts.UUIDAware`` plumbing part.
  [rnix, 2011-12-02]

- fix ``node.parts.Order.swap`` in order to work with pickled nodes.
  [rnix, 2011-11-28]

- use ``node.name`` instead of ``node.__name__`` in
  ``node.parts.nodify.Nodify.path``.
  [rnix, 2011-11-17]

- add ``swap`` to  ``node.parts.Order``.
  [rnix, 2011-10-05]

- add ``insertfirst`` and ``insertlast`` to ``node.parts.Order``.
  [rnix, 2011-10-02]


0.9.4
-----

- add ``node.utils.debug`` decorator.
  [rnix, 2011-07-23]

- remove non storage contract specific properties from
  ``node.aliasing.AliasedNodespace``
  [rnix, 2011-07-18]

- ``node.aliasing`` test completion
  [rnix, 2011-07-18]

- Add non strict functionality to ``node.aliasing.DictAliaser`` for accessing
  non aliased keys as is as fallback
  [rnix, 2011-07-18]

- Consider ``INode`` implementing objects in ``node.utils.StrCodec``
  [rnix, 2011-07-16]

- Remove duplicate implements in storage parts
  [rnix, 2011-05-16]


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
