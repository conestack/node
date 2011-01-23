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

A full API desctiption of the node interface can be found at
``node.interfaces.INode``.


Writing Nodes
-------------

Nodes are implemented using the
`plumber <http://pypi.python.org/pypi/plumber>`_ package. If you want to write
your own Node implementations read the plumber documentation first to understand
the syntax and look at ``node.parts`` sources for blueprints.


Contributors
============

- Robert Niederreiter <rnix@squarewave.at>
- Florian Friesdorf <flo@chaoflow.net>
- Jens Klein <jens@bluedynamics.com>


Changes
=======

1.0
---

- Make it work [rnix, chaoflow, et al]
