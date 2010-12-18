node
====

This package is the successor of ``zodict``.

A node behaves like a dictionary described by
``zope.interface.common.mapping.IFullMapping`` and has a hierarchy described by
``zope.location.interfaces.ILocation``.


### brainstorming ###

A fully functional node consists of three components:
- frontend
- middleware (name is not good)
- backend


Goals
-----

A node needs to be memory efficient for use case where many nodes are kept in
memory and it needs to be flexible enough to plugin in arbitrary backends.


Frontend
--------


XXX ("Middleware")
------------------

- adopting
- __contains__, if faster than via __getitem__


Backend
-------

- data storage, e.g. methods of an odict or another node


Example node
------------

    >>> class MyNode(SomeMiddleware, SomeBackend, SomeFrontend):
    ...     pass

### / brainstorming ###


Contributors
============

- Florian Friesdorf <flo@chaoflow.net>
- Robert Niederreiter <rnix@squarewave.at>


Changes
=======

dev
---

- Base refactoring, BBB testing.
  [rnix - 2010-12-18] 

- Move code from ``zodict`` to ``node`` (BBB imports are provided).
  [rnix - 2010-12-18]

- Implement aliasing package and AbstractNode.
  [chaoflow]

- Initial package creation.
  [chaoflow]