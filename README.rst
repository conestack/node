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
    ['__class__', '__contains__', '__delattr__', '__delitem__', '__dict__', 
    '__doc__', '__format__', '__getattribute__', '__getitem__', '__hash__', 
    '__implemented__', '__init__', '__iter__', '__len__', '__metaclass__', 
    '__module__', '__name__', '__new__', '__parent__', '__plumbing__', 
    '__plumbing_stacks__', '__provides__', '__reduce__', '__reduce_ex__', 
    '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__', 
    '__subclasshook__', '__weakref__', '_nodespaces', '_notify_suppress', 
    'allow_non_node_childs', 'attribute_access_for_attrs', 'attributes', 
    'attributes_factory', 'attrs', 'clear', 'copy', 'detach', 'events', 
    'filtereditems', 'filtereditervalues', 'filteredvalues', 'get', 'has_key', 
    'items', 'iteritems', 'iterkeys', 'itervalues', 'keys', 'noderepr', 
    'nodespaces', 'path', 'pop', 'popitem', 'printtree', 'root', 'setdefault', 
    'storage', 'update', 'values']

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

Alias
    Provide ``node.interfaces.IAlias`` on node class.

Attributes
    Provide ``node.interfaces.IAttributes`` on node class, requires
    ``Nodespaces`` part.

Adopt
    Set ``__name__`` and ``__parent__`` attributes automatically during node
    tree manipulation.

AsAttrAccess
    Provide ``node.interfaces.IAsAttrAccess`` on node class.

Lifecycle
    Provide ``node.interfaces.ILifecycle`` on node class.

Nodespaces
    Provide ``node.interfaces.INodespaces`` on node class.

DefaultInit
    Provide a default ``__init__`` function on node class.

Nodify
    Hook basic ``INode`` API on node class.

Order
    Provide ``node.interfaces.IOrder`` on node class.

Reference
    Provide ``node.interfaces.IReference`` on node class.

DictStorage
    Provide data related methods utilizing ``dict``.

OdictStorage
    Provide data related methods utilizing ``odict``.


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
  
    106    88%   node.aliasing
     27   100%   node.base
     24    58%   node.events
    127    86%   node.interfaces
     23    95%   node.locking
     11   100%   node.parts.__init__
     46   100%   node.parts.alias
     38   100%   node.parts.attributes
     53    92%   node.parts.cache
     71    74%   node.parts.common
     54    90%   node.parts.lifecycle
    113   100%   node.parts.mapping
     31   100%   node.parts.nodespace
     67    97%   node.parts.nodify
     65   100%   node.parts.order
     81   100%   node.parts.reference
     34   100%   node.parts.storage
     73    98%   node.utils


Contributors
============

- Robert Niederreiter <rnix@squarewave.at>
- Florian Friesdorf <flo@chaoflow.net>
- Jens Klein <jens@bluedynamics.com>


Changes
=======


0.9.1
-----

- Provide ``node.base.Node`` with same behavior like ``zodict.Node`` for
  migration purposes.
  [rnix, 2011-02-08]


0.9
---

- Make it work [rnix, chaoflow, et al]
