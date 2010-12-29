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
- Once in memory, node trees are fast to compute with
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
is provided as well (See tests and sources of ``base`` module).


Behaviors
---------

A node might provide additional behaviors, like being orderable, hold a tree
internal reference index for cross access, provide attributes, et cetera.

Behaviors have a common ground:

- They are orthogonal to nodes.
- They might react on data structure changes.
- Their API is available on the node.

Someone might argue that too heavy multiple inheritance just causes headache,
and an approach to implement such behaviors in a way that they can be mixed
together arbitrarily by subclassing would probably be a dead end.

We agree on this, so here is how it works:

XXX


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