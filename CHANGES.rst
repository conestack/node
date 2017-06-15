
Changes
=======

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
