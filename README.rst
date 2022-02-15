Node
====

.. image:: https://img.shields.io/pypi/v/node.svg
    :target: https://pypi.python.org/pypi/node
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/node.svg
    :target: https://pypi.python.org/pypi/node
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/bluedynamics/node.svg?branch=master
    :target: https://travis-ci.org/bluedynamics/node


Overview
--------

Node is a library to create nested data models and structures.

These data models are described as trees of nodes, optionally with attributes
and schema definitions.

They utilize:

- Python's `mapping and sequence API's <http://docs.python.org/reference/datamodel.html>`_
  for accessing node members.
- The contract of `zope.location.interfaces.ILocation <https://zopelocation.readthedocs.io/en/latest/api.html#zope.location.interfaces.ILocation>`_ for hierarchy information.

One purpose of this package is to provide a unified API to different backend
storages. Specific storage related implementations are for example:

- `node.ext.directory <https://pypi.org/project/node.ext.directory>`_
- `node.ext.ldap <https://pypi.org/project/node.ext.ldap>`_
- `node.ext.yaml <https://pypi.org/project/node.ext.yaml>`_
- `node.ext.zodb <https://pypi.org/project/node.ext.zodb>`_

Another usecase is providing interfaces for specific application domains.

E.g. for user and group management,
`node.ext.ugm <https://pypi.org/project/node.ext.ugm>`_ defines the interfaces.
Additional it implements a file based default implementation. Then there are
specific implementations of those interfaces in
`node.ext.ldap <https://pypi.org/project/node.ext.ldap>`_ and
`cone.sql <https://pypi.org/project/cone.sql>`_, to access users and groups in
LDAP and SQL databases.

This package is also used to build in-memory models of all sorts.

E.g.  `yafowil <https://pypi.org/project/yafowil>`_ is a HTML form processing
and rendering library. It uses node trees for declarative description of the
form model.

Another one to mention is `cone.app <https://pypi.org/project/cone.app>`_,
a `Pyramid <https://pypi.org/project/pyramid>`_ based development environment
for web applications, which uses node trees to describe the application model.


Basic Usage
-----------

There are two basic node types. Mapping nodes and sequence nodes. This
package provides some basic nodes to start from.


Mapping Nodes
~~~~~~~~~~~~~

Mapping nodes implement ``node.interfaces.IMappingNode``. A mapping in python
is a container object that supports arbitrary key lookups and implements the
methods specified in the ``MutableMapping`` of pythons abstract base classes
respective ``zope.interface.common.mapping.IFullMapping``.

An unordered node. This can be used as base for trees where order of items
doesn't matter:

.. code-block:: python

    from node.base import BaseNode

    root = BaseNode(name='root')
    root['child'] = BaseNode()

An ordered node. The order of items is preserved:

.. code-block:: python

    from node.base import OrderedNode

    root = OrderedNode(name='orderedroot')
    root['foo'] = OrderedNode()
    root['bar'] = OrderedNode()

With ``printtree`` we can do a quick inspection of our node tree:

.. code-block:: pycon

    >>> root.printtree()
    <class 'node.base.OrderedNode'>: orderedroot
      <class 'node.base.OrderedNode'>: foo
      <class 'node.base.OrderedNode'>: bar


Sequence Nodes
~~~~~~~~~~~~~~

Sequence nodes implement ``node.interfaces.ISequenceNode``. In the context
of this library, a sequence is an implementation of the methods
specified in the ``MutableSequence`` of pythons abstract base classes respective
``zope.interface.common.collections.IMutableSequence``.

Using a list node:

.. code-block:: python

    from node.base import BaseNode
    from node.base import ListNode

    root = ListNode(name='listroot')
    root.insert(0, BaseNode())
    root.insert(1, BaseNode())

Check tree structire with ``printtree``:

.. code-block:: pycon

    >>> root.printtree()
    <class 'node.base.ListNode'>: listnode
      <class 'node.base.BaseNode'>: 0
      <class 'node.base.BaseNode'>: 1

.. note::

    Sequence nodes are introduced as of node 1.0 and are not as feature rich
    as mapping nodes (yet). If you find inconsistencies or missing features,
    please file an issue or create a pull request at github. Any help is
    appreciated.


Behaviors
~~~~~~~~~

``node`` utilizes the `plumber <http://pypi.python.org/pypi/plumber>`_ package.

The different functionalities of nodes are provided as plumbing behaviors:

.. code-block:: python

    from node.behaviors import DefaultInit
    from node.behaviors import MappingNode
    from node.behaviors import OdictStorage
    from plumber import plumbing

    @plumbing(
        DefaultInit,
        MappingNode,
        OdictStorage)
    class CustomNode(object):
        pass

When inspecting the ``CustomNode`` class, we can see it was plumbed using given
behaviors, now representing a complete node implementation:

.. code-block:: pycon

    >>> dir(CustomNode)
    ['__bool__', '__class__', '__contains__', '__delattr__', '__delitem__',
    '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__',
    '__getattribute__', '__getitem__', '__gt__', '__hash__', '__implemented__',
    '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__',
    '__module__', '__name__', '__ne__', '__new__', '__nonzero__', '__parent__',
    '__plumbing__', '__plumbing_stacks__', '__provides__', '__reduce__',
    '__reduce_ex__', '__repr__', '__setattr__', '__setitem__', '__sizeof__',
    '__str__', '__subclasshook__', '__weakref__', 'acquire', 'clear', 'copy',
    'deepcopy', 'detach', 'filtereditems', 'filtereditervalues', 'filteredvalues',
    'get', 'has_key', 'items', 'iteritems', 'iterkeys', 'itervalues', 'keys',
    'name', 'noderepr', 'parent', 'path', 'pop', 'popitem', 'printtree', 'root',
    'setdefault', 'storage', 'treerepr', 'update', 'values']

Please read the documentation of ``plumber`` for detailed information about the
plumbing system.


Attributes
~~~~~~~~~~

XXX


Schema
~~~~~~

XXX


Plumbing Behaviors
------------------

General Behaviors
~~~~~~~~~~~~~~~~~

**node.behaviors.DefaultInit**
    Provide default ``__init__`` function on object.
    See ``node.interfaces.IDefaultInit``.

**node.behaviors.Node**
    Fill in gaps for full INode API. See ``node.interfaces.INode``. Normally
    not applied directly. Use ``node.behaviors.MappingNode`` and
    ``node.behaviors.SequenceNode`` instead.

**node.behaviors.Attributes**
    Provide attributes on node. See ``node.interfaces.IAttributes``. If
    ``node.behaviors.Nodespaces`` is applied on node, the attributes instance
    gets stored internally in ``__attrs__`` nodespace, otherwise its set on
    ``__attrs__`` attribute.

**node.behaviors.Events**
    Provide an event registration and dispatching mechanism.
    See ``node.interfaces.IEvents``.

**node.behaviors.BoundContext**
    Mechanism for scoping objects to interfaces and classes.
    See ``node.interfaces.IBoundContext``.


Mapping Behaviors
~~~~~~~~~~~~~~~~~

**node.behaviors.MappingNode**
    Turn an object into a mapping node. Extends ``node.behaviors.Node``.
    See ``node.interfaces.IMappingNode``.

**node.behaviors.Adopt**
    Plumbing behavior that provides adoption of children.
    See ``node.interfaces.IAdopt``.

**node.behaviors.NodeChildValidate**
    Plumbing behavior for child node validation.
    See ``node.interfaces.INodeChildValidate``.

**node.behaviors.UnicodeAware**
    Plumbing behavior to ensure unicode for keys and string values.
    See ``node.interfaces.IUnicodeAware``.

**node.behaviors.Alias**
    Plumbing behavior that provides aliasing of child keys.
    See ``node.interfaces.IAlias``.

**node.behaviors.AsAttrAccess**
    Plumbing behavior to get node as IAttributeAccess implementation.
    See ``node.interfaces.IAsAttrAccess``.

**node.behaviors.ChildFactory**
    Plumbing behavior providing child factories which are invoked at
    ``__getitem__`` if object by key is not present at plumbing endpoint yet.
    See ``node.interfaces.IChildFactory``.

**node.behaviors.FixedChildren**
    Plumbing behavior that initializes a fixed dictionary as children.
    See ``node.interfaces.IFixedChildren``.

**node.behaviors.GetattrChildren**
    Plumbing behavior for child access via ``__getattr__``, given the attribute
    name is unused.
    See ``node.interfaces.IGetattrChildren``.

**node.behaviors.Nodespaces**
    Plumbing behavior for providing nodespaces on node.
    See ``node.interfaces.INodespaces``.

**node.behaviors.Lifecycle**
    Plumbing behavior taking care of lifecycle events.
    See ``node.interfaces.ILifecycle``.

**node.behaviors.AttributesLifecycle**
    Plumbing behavior for handling lifecycle events on attribute manipulation.
    See ``node.interfaces.IAttributesLifecycle``.

**node.behaviors.Invalidate**
    Plumbing behavior for node invalidation.
    See ``node.interfaces.Invalidate``.

**node.behaviors.VolatileStorageInvalidate**
    Plumbing behavior for invalidating nodes using a volatile storage.
    See ``node.interfaces.Invalidate``.

**node.behaviors.Cache**
    Plumbing behavior for caching.
    See ``node.interfaces.ICache``.

**node.behaviors.Order**
    Plumbing behavior for ordering support.
    See ``node.interfaces.IOrder``.

**node.behaviors.UUIDAware**
    Plumbing behavior providing a uuid on nodes.
    See ``node.interfaces.IUUIDAware``.

**node.behaviors.Reference**
    Plumbing behavior holding an index of all nodes contained in the tree.
    See ``node.interfaces.IReference``.

**node.behaviors.MappingStorage**
    Provide abstract mapping storage access.
    See ``node.interfaces.IMappingStorage``.

**node.behaviors.DictStorage**
    Provide dictionary storage. Extends ``node.behaviors.MappingStorage``.
    See ``node.interfaces.IMappingStorage``.

**node.behaviors.OdictStorage**
    Provide ordered dictionary storage. Extends
    ``node.behaviors.MappingStorage``. See ``node.interfaces.IMappingStorage``.

**node.behaviors.Fallback**
    Provide a way to fall back to values by subpath stored on another node.
    See ``node.interfaces.IFallback``.

**node.behaviors.Schema**
    Provide schema validation and value serialization on node values.
    See ``node.interfaces.ISchema``.

**node.behaviors.SchemaAsAttributes**
    Provide schema validation and value serialization on node values via
    dedicated attributes object.
    See ``node.interfaces.ISchemaAsAttributes``.

**node.behaviors.SchemaProperties**
    Provide schema fields as class properties.
    See ``node.interfaces.ISchemaProperties``.


Sequence Behaviors
~~~~~~~~~~~~~~~~~~

**node.behaviors.ListStorage**
    Provide list storage. See ``node.interfaces.ISequenceStorage``.

**node.behaviors.SequenceNode**
    Turn an object into a sequence node. Extends ``node.behaviors.Node``.
    See ``node.interfaces.IMappingNode``.


JSON Serialization
------------------

Nodes can be serialized to and deserialized from JSON:

.. code-block:: pycon

    >>> from node.serializer import serialize
    >>> json_dump = serialize(BaseNode(name='node'))

    >>> from node.serializer import deserialize
    >>> deserialize(json_dump)
    <BaseNode object 'node' at ...>

For details on serialization API please read file in
``docs/archive/serializer.rst``.


TestCoverage
------------

.. image:: https://travis-ci.org/bluedynamics/node.svg?branch=master
    :target: https://travis-ci.org/bluedynamics/node

Summary of the test coverage report::

    Name                                Stmts   Miss  Cover
    -------------------------------------------------------
    src/node/base.py                       23      0   100%
    src/node/behaviors/__init__.py         45      0   100%
    src/node/behaviors/alias.py           103      0   100%
    src/node/behaviors/attributes.py       39      0   100%
    src/node/behaviors/cache.py            69      0   100%
    src/node/behaviors/common.py          138      0   100%
    src/node/behaviors/context.py          38      0   100%
    src/node/behaviors/events.py          112      0   100%
    src/node/behaviors/fallback.py         45      0   100%
    src/node/behaviors/lifecycle.py        48      0   100%
    src/node/behaviors/mapping.py         117      0   100%
    src/node/behaviors/nodespace.py        33      0   100%
    src/node/behaviors/nodify.py           91      0   100%
    src/node/behaviors/order.py            52      0   100%
    src/node/behaviors/reference.py        83      0   100%
    src/node/behaviors/schema.py          157      0   100%
    src/node/behaviors/storage.py          31      0   100%
    src/node/compat.py                     10      0   100%
    src/node/events.py                     32      0   100%
    src/node/interfaces.py                116      0   100%
    src/node/locking.py                    23      0   100%
    src/node/schema/__init__.py            35      0   100%
    src/node/schema/fields.py             142      0   100%
    src/node/schema/scope.py               11      0   100%
    src/node/schema/serializer.py          77      0   100%
    src/node/serializer.py                160      0   100%
    src/node/testing/__init__.py            1      0   100%
    src/node/testing/base.py               66      0   100%
    src/node/testing/env.py                18      0   100%
    src/node/testing/fullmapping.py       177      0   100%
    src/node/tests/__init__.py             93      0   100%
    src/node/tests/test_alias.py          113      0   100%
    src/node/tests/test_attributes.py      37      0   100%
    src/node/tests/test_base.py           245      0   100%
    src/node/tests/test_cache.py           98      0   100%
    src/node/tests/test_common.py         158      0   100%
    src/node/tests/test_context.py         62      0   100%
    src/node/tests/test_events.py         184      0   100%
    src/node/tests/test_fallback.py        46      0   100%
    src/node/tests/test_lifecycle.py      105      0   100%
    src/node/tests/test_locking.py         43      0   100%
    src/node/tests/test_mapping.py         22      0   100%
    src/node/tests/test_nodespace.py       44      0   100%
    src/node/tests/test_nodify.py          45      0   100%
    src/node/tests/test_order.py          172      0   100%
    src/node/tests/test_reference.py       74      0   100%
    src/node/tests/test_schema.py         563      0   100%
    src/node/tests/test_serializer.py     268      0   100%
    src/node/tests/test_storage.py         41      0   100%
    src/node/tests/test_testing.py        669      0   100%
    src/node/tests/test_tests.py           50      0   100%
    src/node/tests/test_utils.py          135      0   100%
    src/node/utils.py                     150      0   100%
    -------------------------------------------------------
    TOTAL                                5509      0   100%


Python Versions
---------------

- Python 2.7, 3.3+, pypy
- May work with other versions (untested)


Contributors
============

- Robert Niederreiter
- Florian Friesdorf
- Jens Klein
