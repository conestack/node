node
====

This package is the successor of `zodict <http://pypi.python.org/pypi/zodict>`_.


Overview
--------

Data structures could be described as trees. Some are by nature ``treeish``,
like XML documents, LDAP directories or filesystem directory trees, while others
can be treated that way.

Furthermore, python has elegant ways for customizing all sorts of datamodel related
APIs. The `dictionary container type
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

An unordered node. This can be used as base for trees where order of items
doesn't matter::

    >>> from node.base import BaseNode
    >>> root = BaseNode(name='root')
    >>> root['child'] = BaseNode()
    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: child

An ordered node. The order of items is preserved::

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

    >>> from plumber import plumbing
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

    >>> @plumbing(
    ...     Nodespaces,
    ...     Attributes,
    ...     Lifecycle,
    ...     NodeChildValidate,
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class CustomNode(object):
    ...     pass

    >>> dir(CustomNode)
    ['__class__', '__contains__', '__delattr__', '__delitem__',
    '__dict__', '__doc__', '__format__', '__getattribute__',
    '__getitem__', '__hash__', '__implemented__', '__init__',
    '__iter__', '__len__', '__module__', '__name__',
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

As the ``dir`` call shows, the ``CustomNode`` class was plumbed using given behaviors,
so defining a complete ``INode`` implementation with some additional
behaviours and is now easily done::

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

The ``node`` package provides several plumbing behaviors:

**node.behaviors.DefaultInit**
    Plumbing part providing default ``__init__`` function on node.
    See ``node.interfaces.IDefaultInit``.

**node.behaviors.Nodify**
    Plumbing part to Fill in gaps for full INode API.
    See ``node.interfaces.INodify``.

**node.behaviors.Adopt**
    Plumbing part that provides adoption of children.
    See ``node.interfaces.IAdopt``.

**node.behaviors.NodeChildValidate**
    Plumbing part for child node validation.
    See ``node.interfaces.INodeChildValidate``.

**node.behaviors.UnicodeAware**
    Plumbing part to ensure unicode for keys and string values.
    See ``node.interfaces.IUnicodeAware``.

**node.behaviors.Alias**
    Plumbing part that provides aliasing of child keys.
    See ``node.interfaces.IAlias``.

**node.behaviors.AsAttrAccess**
    Plumbing part to get node as IAttributeAccess implementation.
    See ``node.interfaces.IAsAttrAccess``.

**node.behaviors.ChildFactory**
    Plumbing part providing child factories which are invoked at
    ``__getitem__`` if object by key is not present at plumbing endpoint yet.
    See ``node.interfaces.IChildFactory``.

**node.behaviors.FixedChildren**
    Plumbing part that initializes a fixed dictionary as children.
    See ``node.interfaces.IFixedChildren``.

**node.behaviors.GetattrChildren**
    Plumbing part for child access via ``__getattr__``, given the attribute
    name is unused.
    See ``node.interfaces.IGetattrChildren``.

**node.behaviors.Nodespaces**
    Plumbing part for providing nodespaces on node.
    See ``node.interfaces.INodespaces``.

**node.behaviors.Attributes**
    Plumbing part to provide attributes on node.
    Requires ``node.behaviors.Nodespaces`` part.
    See ``node.interfaces.IAttributes``.

**node.behaviors.Lifecycle**
    Plumbing part taking care of lifecycle events.
    See ``node.interfaces.ILifecycle``.

**node.behaviors.AttributesLifecycle**
    Plumbing part for handling ifecycle events at attributes manipulation.
    See ``node.interfaces.IAttributesLifecycle``.

**node.behaviors.Invalidate**
    Plumbing part for node invalidation.
    See ``node.interfaces.Invalidate``.

**node.behaviors.VolatileStorageInvalidate**
    Plumbing part for invalidating nodes using a volatile storage.
    See ``node.interfaces.Invalidate``.

**node.behaviors.Cache**
    Plumbing part for caching.
    See ``node.interfaces.ICache``.

**node.behaviors.Order**
    Plumbing part for ordering support.
    See ``node.interfaces.IOrder``.

**node.behaviors.UUIDAware**
    Plumbing part providing a uuid on nodes.
    See ``node.interfaces.IUUIDAware``.

**node.behaviors.Reference**
    Plumbing part holding an index of all nodes contained in the tree.
    See ``node.interfaces.IReference``.

**node.behaviors.Storage**
    Provide abstract storage access.
    See ``node.interfaces.IStorage``.

**node.behaviors.DictStorage**
    Provide dictionary storage.
    See ``node.interfaces.IStorage``.

**node.behaviors.OdictStorage**
    Provide ordered dictionary storage.
    See ``node.interfaces.IStorage``.

**node.behaviors.Fallback**
    Provide a way to fall back to values by subpath stored on another node.
    See ``node.interfaces.IFallback``.


JSON Serialization
------------------

Nodes can be serialized to and deserialized from JSON::

    >>> from node.serializer import serialize
    >>> json_dump = serialize(BaseNode(name='node'))

    >>> from node.serializer import deserialize
    >>> deserialize(json_dump)
    <BaseNode object 'node' at ...>

For details on serialization API please read tests in
``src/node/serializer.rst``.


Migration
---------

A node which behaves like ``zodict.Node`` is contained in ``node.base.Node``.
This node is supposed to be used for migration from zodict.

It's also useful to take a look at the behaviors the original node is build
from.

Probably an implementation does not need all the behaviors at once. In this case
define the node plumbing directly on a node class instead of inheriting from
``node.base.Node``.


TestCoverage
------------

.. image:: https://travis-ci.org/bluedynamics/node.svg?branch=master
    :target: https://travis-ci.org/bluedynamics/node

Summary of the test coverage report::

    lines   cov%   module
        1   100%   node.__init__
       61   100%   node.base
       36   100%   node.behaviors.__init__
      111   100%   node.behaviors.alias
       42   100%   node.behaviors.attributes
       68   100%   node.behaviors.cache
      131   100%   node.behaviors.common
       41   100%   node.behaviors.fallback
       56   100%   node.behaviors.lifecycle
      124   100%   node.behaviors.mapping
       34   100%   node.behaviors.nodespace
       92   100%   node.behaviors.nodify
      109   100%   node.behaviors.order
       84   100%   node.behaviors.reference
       30   100%   node.behaviors.storage
       25   100%   node.events
      133   100%   node.interfaces
       23   100%   node.locking
      136   100%   node.serializer
        1   100%   node.testing.__init__
       62   100%   node.testing.base
       24   100%   node.testing.env
      216   100%   node.testing.fullmapping
       31   100%   node.tests
      138   100%   node.utils


Contributors
============

- Robert Niederreiter <rnix [at] squarewave [dot] at>

- Florian Friesdorf <flo [at] chaoflow [dot] net>

- Jens Klein <jens [at] bluedynamics [dot] com>
