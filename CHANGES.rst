
Changes
=======

1.1 (2022-10-06)
----------------

- Add ``node.schema.DateTime``, ``node.schema.DateTimeSerializer`` and
  ``node.schema.datetime_serializer``.
  [rnix]

- Subclass ``threading.local`` for
  ``node.behaviors.lifecycle._lifecycle_context``,
  ``node.behaviors.events._attribute_subscribers`` and
  ``node.behaviors.schema._schema_property`` objects in order to safely provide
  default values.
  [rnix]

- Introduce ``node.interfaces.IChildFilter``, ``node.behaviors.MappingFilter``
  and ``node.behaviors.SequenceFilter``.
  [rnix]

- Introduce ``node.interfaces.IWildcardFactory`` and
  ``node.behaviors.WildcardFactory``.
  [rnix]

- Introduce ``node.interfaces.INodeInit`` and ``node.behaviors.NodeInit``.
  [rnix]

- Deprecate ``IFixedChildren.fixed_children_factories`` Use
  ``IFixedChildren.factories`` instead.
  [rnix]

- Introduce ``node.interfaces.IContentishNode`` and
  ``node.behaviors.ContentishNode``. Use as base for mapping and sequence nodes.
  [rnix]

- ``insertbefore``, ``insertafter`` and ``swap`` in ``node.behaviors.Order``
  alternatively accept node names as arguments where possible.
  [rnix]

- ``insertbefore``, ``insertafter``, and ``insertfirst`` and ``insertlast`` in
  ``node.behaviors.Order`` internally use ``movebefore``, ``moveafter``,
  ``movefirst`` and ``movelast`` of ``odict`` to avoid modifying the data
  structure before ``__setitem__`` gets called.
  [rnix]

- Extend ``node.interfaces.IOrder``  respective ``node.behaviors.Order``
  by ``movebefore``, ``moveafter``, ``movefirst`` and ``movelast``.
  [rnix]

- Reset ``__parent__`` in ``node.behaviors.Node.detach``. Node is no longer
  contained in tree.
  [rnix]

- Introduce ``IndexViolationError`` which inherits from ``ValueError`` and
  raise it in reference related behaviors instead of ``ValueError`` where
  appropriate.
  [rnix]

- Introduce ``node.interfaces.INodeReference`` and
  ``node.behaviors.NodeReference``.
  [rnix]

- Introduce ``node.interfaces.ISequenceReference`` and
  ``node.behaviors.SequenceReference``.
  [rnix]

- Rename ``node.interfaces.IReference`` to ``node.interfaces.IMappingReference``
  and ``node.behaviors.Reference`` to ``node.behaviors.MappingReference``.
  B/C is kept.
  [rnix]

**Breaking changes**:

- Remove ``_notify_suppress`` flag from ``Lifecycle`` behavior. Introduce
  ``suppress_lifecycle_events`` contextmanager as substitute.
  [rnix]

- Importing ``ChildFactory`` and ``FixedChildren`` from
  ``node.behaviors.common`` not works any more. Please import from
  ``node.behaviors``.
  [rnix]

- Importing B/C ``Reference`` behavior from ``node.behaviors.reference``
  not works any more. Please import from ``node.behaviors``.
  [rnix]


1.0 (2022-03-17)
----------------

- Implement ``__copy__`` and ``__deepcopy__`` on ``node.utils.UNSET``.
  [rnix]

- Introduce ``node.interfaces.ISequenceConstraints`` and
  ``node.behaviors.SequenceConstraints``.
  [rnix]

- Rename ``node.interfaces.INodeChildValidate`` to
  ``node.interfaces.IMappingConstraints`` and
  ``node.behaviors.NodeChildValidate`` to ``node.behaviors.MappingConstraints``.
  ``MappingConstraints`` implementation moved from ``node.behaviors.common`` to
  ``node.behaviors.constraints``. B/C is kept.
  [rnix]

- Introduce ``node.interfaces.ISequenceAdopt`` and
  ``node.behaviors.SequenceAdopt``.
  [rnix]

- ``MappingAdopt`` now catches all exceptions instead of only
  ``AttributeError``, ``KeyError`` and ``ValueError``.
  [rnix]

- Rename ``node.interfaces.IAdopt`` to ``node.interfaces.IMappingAdopt`` and
  ``node.behaviors.Adopt`` to ``node.behaviors.MappingAdopt``. ``MappingAdopt``
  implementation moved from ``node.behaviors.common`` to
  ``node.behaviors.adopt``. B/C is kept.
  [rnix]

- ``node.behaviors.Attributes`` now also works if
  ``node.behaviors.Nodespaces`` is not applied.
  [rnix]

- Introduce ``node.behaviors.Node`` which implements only
  ``node.interfaces.INode`` contract. It is used as base for
  ``node.behaviors.MappingNode`` and ``node.behaviors.SequcneNode``.
  [rnix]

- Do not inherit ``node.interfaces.INode`` from
  ``zope.interfaces.common.mapping.IFullMapping`` any more. Data model specific
  interfaces are added now via ``node.interfaces.IMappingNode`` and
  ``node.interfaces.ISequenceNode``.
  [rnix]

- Introduce sequence nodes. Sequence nodes are implemented via
  ``node.behaviors.SequcneNode`` and ``node.behaviors.ListStorage``.
  [rnix]

- Rename ``node.interfaces.INodify`` to ``node.interfaces.IMappingNode`` and
  ``node.behaviors.Nodify`` to ``node.behaviors.MappingNode``. ``MappingNode``
  implementation moved from ``node.behaviors.nodify`` to
  ``node.behaviors.mapping``. B/C is kept.
  [rnix]

- Rename ``node.interfaces.IStorage`` to ``node.interfaces.IMappingStorage``
  and ``node.behaviors.Storage`` to ``node.behaviors.Storage``. B/C is kept.
  [rnix]

- Add key and value type validation to schema fields where appropriate.
  [rnix]

- Introduce serializer support to schema fields. Add a couple of concrete field
  serializer implementations to ``node.schema.serializer``.
  [rnix]

- Add ``ODict`` and ``Node`` schema fields to ``node.schema.fields``.
  [rnix]

- Add ``node.schema.fields.IterableField`` and use as base class for
  ``List``, ``Tuple`` and ``Set`` schema fields.

- Introduce ``node.behaviors.schema.SchemaProperties`` plumbing behavior.
  [rnix]

- Split up ``node.schema`` module into a package.
  [rnix]

- Introduce ``node.behaviors.context.BoundContext`` plumbing behavior.
  [rnix]

**Breaking changes**:

- Remove ``node.behaviors.GetattrChildren``. See ``node.utils.AttributeAccess``
  instead if you need to access node children via ``__getattr__``.
  [rnix]

- Importing B/C ``Adopt`` behavior from ``node.behaviors.common``
  not works any more. Please import from ``node.behaviors``.
  [rnix]

- Importing B/C ``NodeChildValidate`` behavior from ``node.behaviors.common``
  not works any more. Please import from ``node.behaviors``.
  [rnix]

- Importing B/C ``Nodify`` behavior from ``node.behaviors.nodify``
  not works any more. Please import from ``node.behaviors``.
  [rnix]

- Remove deprecated B/C import location ``node.parts``.
  [rnix]

- ``node.behaviors.schema.Schema`` no longer considers wildcard fields.
  [rnix]

- ``node.behaviors.schema.Schema.__setitem__`` deletes value from related
  storage for field if value is ``node.utils.UNSET``.
  [rnix]

- ``node.behaviors.schema.Schema.__getitem__`` always returns default value for
  field instead of raising ``KeyError`` if no default is set.
  [rnix]

- Default value of ``node.schema.fields.Field.default`` is ``node.utils.UNSET``
  now.
  [rnix]

- ``node.schema.fields.Field.validate`` raises exception if validation fails
  instead of returning boolean.
  [rnix]


0.9.28 (2021-11-08)
-------------------

- Add missing ``node.interfaces.INodeAttributes`` interface.
  [rnix]

- Add missing ``attribute_access_for_attrs`` attribute to ``IAttributes``
  interface.
  [rnix]

- Rename ``node.behaviors.common.NodeChildValidate.allow_non_node_childs``
  to ``allow_non_node_children``. A Deprecation warning is printed if the
  old attribute is used.
  [rnix]

- Introduce ``node.behaviors.schema.Schema``,
  ``node.behaviors.schema.SchemaAsAttributes`` and related schema definitions
  in ``node.schema``.
  [rnix]


0.9.27 (2021-10-21)
-------------------

- Expose ``first_key``, ``last_key``, ``next_key`` and ``prev_key`` from
  odict storage on ``Order`` behavior.
  [rnix, 2021-10-21]

- Add basic serializer settings mechanism.
  [rnix, 2021-07-20]


0.9.26 (2021-05-10)
-------------------

- Use ``node.utils.safe_decode`` in ``node.behaviors.nodify.Nodify.treerepr``.
  [rnix, 2021-05-04]

- Add ``node.utils.safe_encode`` and ``node.utils.safe_decode``.
  [rnix, 2021-05-04]


0.9.25 (2020-03-30)
-------------------

- Introduce ``uuid_factory`` function on ``node.interfaces.IUUIDAware`` and
  implement default function in ``node.behaviors.common.UUIDAware``.
  [rnix, 2020-03-01]

- Rename ``NodeTestCase.expect_error`` to ``NodeTestCase.expectError``.
  [rnix, 2019-09-04]

- Rename ``NodeTestCase.check_output`` to ``NodeTestCase.checkOutput``.
  [rnix, 2019-09-04]

- Introduce ``prefix`` keyword argument in ``Nodify.treerepr``.
  [rnix, 2019-09-04]


0.9.24 (2019-07-10)
-------------------

- Overhaul ``node.behaviors.Order``. Use related functions from ``odict`` where
  appropriate.
  [rnix, 2019-07-10]

- Remove superfluous ``extra_require`` from ``setup.py``.
  [rnix, 2019-04-25]

- Drop Support for python < 2.7 and < 3.3.
  [rnix, 2019-04-25]


0.9.23 (2018-11-07)
-------------------

- Use property decorators for ``node.behaviors.reference.Reference.uuid``.
  [rnix, 2017-12-15]


0.9.22 (2017-07-18)
-------------------

- Add ``always_dispatch`` keyword argument to
  ``node.behaviors.events.EventAttribute`` constructor which defines whether
  events are always dispatched on ``__set__``, not only if attribute value
  changes.
  [rnix, 2017-06-20]

- Use ``node.utils.UNSET`` as default ``default`` value in
  ``node.behaviors.events.EventAttribute.__init__``.
  [rnix, 2017-06-19]

- Introduce ``node.behaviors.events.EventAttribute.subscriber`` decorator which
  can be used to register attribute subscribers.
  [rnix, 2017-06-19]

- Move event dispatching related classes and functions from ``node.events``
  to ``node.behaviors.events`` and import it from there in ``node.events``.
  [rnix, 2017-06-16]

- Introduce ``node.interfaces.IEvents`` and implement
  ``node.behaviors.events.Events`` behavior. Contains business logic from
  ``node.events.EventDispatcher``. Use new behavior on ``EventDispatcher``.
  [rnix, 2017-06-16]

- Create ``suppress_events`` context manager which can be used to
  suppress event notification in conjunction with ``node.behaviors.Events``
  behavior.
  [rnix, 2017-06-15]

- Create ``node.behaviors.fallback.fallback_processing`` context manager and
  and use it in ``node.behaviors.fallback.Fallback.__getitem__`` to check
  whether fallback processing is active.
  [rnix, 2017-06-15]


0.9.21 (2017-06-15)
-------------------

- Introduce ``node.events.EventDispatcher`` and ``node.events.EventAttribute``.
  [rnix, 2017-06-15]

- Use ``setattr`` in ``instance_property`` decorator instead of
  ``object.__setattr__`` in order to avoid errors with custom low level
  ``__setattr__`` implementations.
  [rnix, 2017-06-14]


0.9.20 (2017-06-07)
-------------------

- Type cast sort key to ``node.compat.UNICODE_TYPE`` in
  ``node.behaviors.Nodify.treerepr`` to avoid unicode decode errors.
  [rnix, 2017-06-07]


0.9.19 (2017-06-07)
-------------------

- Python 3 and pypy compatibility.
  [rnix, 2017-06-02]

- Drop support for Python < 2.7.
  [rnix, 2017-06-02]

- Add ``__bool__`` to ``node.behaviors.Nodify``.
  [rnix, 2017-06-02]

- Add ``__bool__`` to ``node.utils.UNSET``.
  [rnix, 2017-06-02]

- Add ``treerepr`` in ``node.behaviors.nodify.Nodify`` and move code from
  ``printtree`` to it. Returs tree representation as string instead of printing
  it. ``printtree`` uses ``treerepr`` now. As enhancement ``treerepr`` sorts
  children of node if it does not implement ``IOrdered`` in order to ensure
  consistend output which can be used to write tests against.
  [rnix, 2017-06-02]

- Use ``object.__getattribute__`` explicitely in
  ``node.utils.instance_property`` to check whether property value already has
  been computed in order to avoid problems when oberwriting ``__getattr__``
  on classes using ``instance_property`` decorator.
  [rnix, 2017-06-02]


0.9.18.1 (2017-02-23)
---------------------

- Fix permissions.
  [rnix, 2017-02-23]


0.9.18 (2017-02-14)
-------------------

- Add ``node.utils.node_by_path``.
  [rnix, 2017-02-07]

- Do not depend on ``unittest2`` since its is not used.
  [jensens, 2017-01-17]

- Add ``node.behaviors.Fallback`` behavior.
  [jensens, 2017-01-17]


0.9.17 (2017-01-17)
-------------------

- Add basic JSON serializer and deserializer.
  [rnix, 2016-12-03]


0.9.16 (2015-10-08)
-------------------

- Only encode name in ``node.behaviors.nodify.Nodify.__repr__`` and
  ``node.behaviors.nodify.Nodify.noderepr`` if name is unicode instance.
  [rnix, 2015-10-03]

- Improve ``node.behaviors.nodify.Nodify.printtree``. None node children are
  printed with key.
  [rnix, 2015-10-03]


0.9.15 (2014-12-17)
-------------------

- Fix dependency declaration to ``odict`` in order to make setuptools 8.x+
  happy; using ``>=`` instead of ``>`` now.
  [jensens, 2014-12-17]


0.9.14
------

- use ``plumbing`` decorator instead of ``plumber`` metaclass.
  [rnix, 2014-07-31]


0.9.13
------

- Introduce ``node.behaviors.cache.VolatileStorageInvalidate``.
  [rnix, 2014-01-15]


0.9.12
------

- Add ``zope.component`` to install dependencies.
  [rnix, 2013-12-09]


0.9.11
------

- Use ``node.utils.UNSET`` instance in
  ``node.behaviors.mapping.ExtendedWriteMapping.pop``.
  [rnix, 2013-02-10]

- Improve ``node.utils.Unset``. Add ``Unset`` instance at
  ``node.utils.UNSET``.
  [rnix, 2013-02-10]


0.9.10
------

- Fix ``node.utils.StrCodec.encode`` to return value as is if str and decoding
  failed.
  [rnix, 2012-11-07]


0.9.9
-----

- Python 2.7 compatibility.
  [rnix, 2012-10-15]

- Remove ``zope.component.event`` B/C.
  [rnix, 2012-10-15]

- Remove ``zope.location`` B/C.
  [rnix, 2012-10-15]

- Remove ``zope.lifecycleevent`` B/C.
  [rnix, 2012-10-15]

- Pep8.
  [rnix, 2012-10-15]


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
