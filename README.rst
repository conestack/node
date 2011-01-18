node
====

This package is the successor of `zodict <http://pypi.python.org/pypi/zodict>`_.


Motivation
----------

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


Base Objects
------------

An unordered node. This can be used as base for trees where oder of items
doesn't matter.
::
    >>> from node.base import BaseNode
    >>> root = BaseNode(name='root')
    >>> root['child'] = BaseNode()
    >>> root.printtree()
    <class 'node.base.BaseNode'>: root
      <class 'node.base.BaseNode'>: child

An ordered node. Order of items is preserved.
::
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

``BaseNode`` and ``OrderedNode`` inherit from dict respective `odict 
<http://pypi.python.org/pypi/odict>`_ by default (this could be changed). If
someone wants a more basic implementation for some reason, an ``AbstractNode``
is provided as well (See tests and sources of ``node.base``).

A full API desctiption of the node interface can be found at
``node.interfaces.INode``.

Behaviors
---------

A node might provide additional behaviors, like being orderable, holding a
internal treeish reference index for cross access, provide attributes, et
cetera.

Behaviors have a common ground:

- They are orthogonal to nodes.

- They might respond on data structure changes.

- Their API is available on the node.

Someone might argue that too heavy multiple inheritance just causes headache,
and an approach to implement such behaviors in a way that they can be mixed
together arbitrarily by subclassing would probably be a dead end.

We agree on this, so here are the design principles:

- Behavior related functionality is available and directly accessible on node.

- Behavior implementations do not have the behavioral enhanced node as base
  class, but act as an adapter on the node.

- Behaviors are bound to a node by a decorator.

- Node related functions, attributes and properties always have precedence to
  behaviors. This way, we can overwrite behavior contracts (don't do this
  unless you have good reasons).

- If more than one behavior defines the same attribute or function, return the
  first one. This is analog to new-class style object inheritance. This avoids
  namespace conflicts when providing behaviors. Shipped implementations do not
  conflict at all.

- Behaviors can hook before and after property access or function calls of
  nodes. This is done with the ``before`` and ``after`` decorators, which
  expect the name of a property or function beeing hooked.

Why using a decorator?

- It is not possible to hook import statements from the users point of view
  (which was another idea how to do it).

- Beside the fact that they provide an easy hooking point for manipulating
  class objects, they are elegant.

Using behaviors. Import required objects.
::
    >>> from node.base import OrderedNode
    >>> from node.behavior import Attributed
    >>> from node.behavior import behavior

Provide a class and decorate it with an behavior.
::
    >>> @behavior(Attributed)
    ... class AttributedNode(OrderedNode): pass

Now the contract of ``node.interfaces.IAttributed`` is available on the node.
::
    >>> node = AttributedNode()
    >>> node.attrs
    <NodeAttributes object 'None' at ...>

A node can be decorated with multiple behaviors. Additionally to ``Attributed``
add the behavior described by ``node.interfaces.IReferenced`` to another node
::
    >>> from node.behavior import Referenced
    
    >>> @behavior(Attributed, Referenced)
    ... class AttributedReferencedNode(OrderedNode): pass
    
    >>> root = AttributedReferencedNode()
    >>> root['foo'] = AttributedReferencedNode()
    >>> bar = root['bar'] = AttributedReferencedNode()
    
    >>> root.node(bar.uuid)
    <AttributedReferencedNode object 'bar' at ...>
    
    >>> bar.attrs
    <NodeAttributes object 'bar' at ...>

The behavior implementations shipped with this package are:

- Attributed (see ``node.interfaces.IAttributed``)

- Referenced (see ``node.interfaces.IReferenced``)

- Orderable (see ``node.interfaces.IOrderable``)

- to be continued... (see ``node.interfaces`` :) )

If you need to provide your own behaviors, look a tests of ``node.meta`` for a 
deeper understanding of the implementation and already existent
``node.behavior.*`` stuff.


Nodespaces
----------

XXX


Contributors
============

- Robert Niederreiter <rnix@squarewave.at>
- Florian Friesdorf <flo@chaoflow.net>
- Jens Klein <jens@bluedynamics.com>


Changes
=======

dev
---

- Make it work [rnix, chaoflow, et al]
