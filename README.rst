Node
====

.. image:: https://img.shields.io/pypi/v/node.svg
    :target: https://pypi.python.org/pypi/node
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/node.svg
    :target: https://pypi.python.org/pypi/node
    :alt: Number of PyPI downloads

.. image:: https://github.com/conestack/node/actions/workflows/test.yaml/badge.svg
    :target: https://github.com/conestack/node/actions/workflows/test.yaml
    :alt: Test node


Overview
--------

Node is a library to create nested data models and structures.

These data models are described as trees of nodes, optionally with attributes
and schema definitions.

They utilize:

- Python's
  `mapping and sequence API's <http://docs.python.org/reference/datamodel.html>`_
  for accessing node members.
- The contract of
  `zope.location.interfaces.ILocation <https://zopelocation.readthedocs.io/en/latest/api.html#zope.location.interfaces.ILocation>`_
  for hierarchy information.

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

Check tree structure with ``printtree``:

.. code-block:: pycon

    >>> root.printtree()
    <class 'node.base.ListNode'>: listnode
      <class 'node.base.BaseNode'>: 0
      <class 'node.base.BaseNode'>: 1

.. note::

    Sequence nodes are introduced as of node 1.0 and are not as feature rich
    as mapping nodes (yet). If you find inconsistencies or missing features,
    please file an issue or create a pull request at github.


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
    class CustomNode:
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

While it is not strictly necessary, it's a good idea to separate the
hierarchical structure of a model from the node related attributes to avoid
naming conflicts. Attributes are provided via ``node.behaviors.Attributes``
plumbing behavior:

.. code-block:: python

    from node.behaviors import Attributes
    from node.behaviors import DefaultInit
    from node.behaviors import DictStorage
    from node.behaviors import MappingNode
    from plumber import plumbing

    @plumbing(
        Attributes,
        DefaultInit,
        MappingNode,
        DictStorage)
    class NodeWithAttributes:
        pass

The node now provides an ``attrs`` attribute. Node attributes are itself just
a node:

.. code-block:: pycon

    >>> node = NodeWithAttributes()
    >>> attrs = node.attrs
    >>> attrs
    <NodeAttributes object 'None' at ...>

    >>> attrs['foo'] = 'foo'

If it's desired to access attribute members via python attribute access,
``attribute_access_for_attrs`` must be set on node:

.. code-block:: pycon

    >>> node.attribute_access_for_attrs = True
    >>> attrs = node.attrs
    >>> attrs.foo = 'bar'
    >>> attrs.foo
    'bar'

A custom attributes implementation can be set by defining
``attributes_factory`` on the node:

.. code-block:: python

    from node.behaviors import NodeAttributes

    class CustomAttributes(NodeAttributes):
        pass

    class CustomAttributesNode(NodeWithAttributes):
        attributes_factory = CustomAttributes

This factory is then used to instantiate the attributes:

.. code-block:: pycon

    >>> node = CustomAttributesNode()
    >>> node.attrs
    <CustomAttributes object 'None' at ...>


Schema
~~~~~~

To describe the data types of node members, this package provides a mechanism
for defining schemata.

This can happen in different ways. One is to define the schema for node members
directly. This is useful for nodes representing a leaf in the hierarchy or for
node attribute nodes:

.. code-block:: python

    from node import schema
    from node.base import BaseNode
    from node.behaviors import DefaultInit
    from node.behaviors import DictStorage
    from node.behaviors import MappingNode
    from node.behaviors import Schema
    from plumber import plumbing

    @plumbing(
        DefaultInit,
        MappingNode,
        DictStorage,
        Schema)
    class SchemaNode:
        schema = {
            'int': schema.Int(),
            'float': schema.Float(default=1.),
            'str': schema.Str(),
            'bool': schema.Bool(default=False),
            'node': schema.Node(BaseNode)
        }

Children defined in the schema provide a default value. If not explicitely
defined, the default value is always ``node.utils.UNSET``:

.. code-block:: pycon

    >>> node = SchemaNode()
    >>> node['int']
    <UNSET>

    >>> node['float']
    1.0

    >>> node['bool']
    False

Children defined in the schema are validated against the defined type when
setting it's value:

.. code-block:: pycon

    >>> node = SchemaNode()
    >>> node['int'] = 'A'
    Traceback (most recent call last):
      ...
    ValueError: A is no <class 'int'> type

For accessing members defined in the schema as node attributes,
``SchemaAsAttributes`` plumbing behavior can be used:

.. code-block:: python

    from node.behaviors import SchemaAsAttributes

    @plumbing(SchemaAsAttributes)
    class SchemaAsAttributesNode(BaseNode):
        schema = {
            'int': schema.Int(default=1),
        }

Node ``attrs`` now provides access to the schema members:

.. code-block:: pycon

    >>> node = SchemaAsAttributesNode()
    >>> node.attrs['int']
    1

Schema members can also be defined as class attributes. This is syntactically
the most elegant way, but comes with the tradeoff of possible naming conflicts:

.. code-block:: python

    from node.behaviors import SchemaProperties

    @plumbing(
        DefaultInit,
        MappingNode,
        DictStorage,
        SchemaProperties)
    class SchemaPropertiesNode:
        text = schema.Str(default='Text')

Here we access ``text`` as class attribute:

.. code-block:: pycon

    >>> node = SchemaPropertiesNode()
    >>> node.text
    'Text'

    >>> node.text = 1
    Traceback (most recent call last):
      ...
    ValueError: 1 is no <class 'str'> type


Plumbing Behaviors
------------------

General Behaviors
~~~~~~~~~~~~~~~~~

**node.behaviors.DefaultInit**
    Plumbing behavior providing default ``__init__`` function on node. This
    behavior is going to be deprecated in future versions. Use
    ``node.behaviors.NodeInit`` instead.
    See ``node.interfaces.IDefaultInit``.

**node.behaviors.NodeInit**
    Plumbing behavior for transparent setting of ``__name__`` and ``__parent__``
    at object initialization time.
    See ``node.interfaces.INodeInit``.

**node.behaviors.Node**
    Fill in gaps for full INode API. See ``node.interfaces.INode``.

**node.behaviors.ContentishNode**
    A node which can contain children. See
    ``node.interfaces.IContentishNode``. Concrete implementations are
    ``node.behaviors.MappingNode`` and ``node.behaviors.SequenceNode``.

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

**node.behaviors.NodeReference**
    Plumbing behavior holding an index of nodes contained in the tree.
    See ``node.interfaces.INodeReference``.

**node.behaviors.WildcardFactory**
    Plumbing behavior providing factories by wildcard patterns.
    See ``node.interfaces.IWildcardFactory``.


Mapping Behaviors
~~~~~~~~~~~~~~~~~

**node.behaviors.MappingNode**
    Turn an object into a mapping node. Extends ``node.behaviors.Node``.
    See ``node.interfaces.IMappingNode``.

**node.behaviors.MappingAdopt**
    Plumbing behavior that provides ``__name__`` and ``__parent__`` attribute
    adoption on child nodes of mapping.
    See ``node.interfaces.IMappingAdopt``.

**node.behaviors.MappingConstraints**
    Plumbing behavior for constraints on mapping nodes.
    See ``node.interfaces.IMappingConstraints``.

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
    Plumbing behavior providing child factories.
    See ``node.interfaces.IChildFactory``.

**node.behaviors.FixedChildren**
    Plumbing Behavior that initializes a fixed dictionary as children.
    See ``node.interfaces.IFixedChildren``.

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

**node.behaviors.MappingReference**
    Plumbing behavior to provide ``node.interfaces.INodeReference`` on mapping
    nodes. See ``node.interfaces.IMappingReference``.

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

**node.behaviors.MappingFilter**
    Filter mapping children by class or interface.
    See ``node.interfaces.IChildFilter``.


Sequence Behaviors
~~~~~~~~~~~~~~~~~~

**node.behaviors.SequenceNode**
    Turn an object into a sequence node. Extends ``node.behaviors.Node``.
    See ``node.interfaces.IMappingNode``.

**node.behaviors.SequenceAdopt**
    Plumbing behavior that provides ``__name__`` and ``__parent__`` attribute
    adoption on child nodes of sequence.
    See ``node.interfaces.ISequenceAdopt``.

**node.behaviors.SequenceConstraints**
    Plumbing behavior for constraints on sequence nodes.
    See ``node.interfaces.ISequenceConstraints``.

**node.behaviors.SequenceStorage**
    Provide abstract sequence storage access.
    See ``node.interfaces.ISequenceStorage``.

**node.behaviors.ListStorage**
    Provide list storage. See ``node.interfaces.ISequenceStorage``.

**node.behaviors.SequenceReference**
    Plumbing behavior to provide ``node.interfaces.INodeReference`` on sequence
    nodes. See ``node.interfaces.ISequenceReference``.

**node.behaviors.SequenceFilter**
    Filter sequence children by class or interface.
    See ``node.interfaces.IChildFilter``.


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


Python Versions
---------------

- Python 2.7, 3.7+
- May work with other versions (untested)


Contributors
============

- Robert Niederreiter
- Florian Friesdorf
- Jens Klein
