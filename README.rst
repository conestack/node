The node (WIP)
==============

currently a brainstorming area

A fully functional node consists of three components:
- frontend
- middleware (name is not good)
- backend

A node behaves like a dictionary described by
``zope.interface.common.mapping.IFullMapping``.

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

Contributors
============

- Florian Friesdorf <flo@chaoflow.net>