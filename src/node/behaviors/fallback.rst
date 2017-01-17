=======================
node.behaviors.fallback
=======================

Prepare test
============

Required Imports::

    >>> from node.behaviors import Adopt
    >>> from node.behaviors import Attributes
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Fallback
    >>> from node.behaviors import NodeChildValidate
    >>> from node.behaviors import Nodespaces
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage
    >>> from plumber import plumbing

Attribute Node for testing::

    >>> @plumbing(
    ...     Nodespaces,
    ...     Fallback,
    ...     Adopt,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class FallbackAttributeNode(object):
    ...     pass

Normal Node for testing::

    >>> @plumbing(
    ...     NodeChildValidate,
    ...     Nodespaces,
    ...     Adopt,
    ...     Attributes,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class FallbackNode(object):
    ...     attributes_factory = FallbackAttributeNode

Setup test data::

    >>> no = FallbackNode(name='root')
    >>> no.fallback_key = 'x'
    >>>
    >>> no['x'] = FallbackNode()
    >>> no['x'].fallback_key = '1'
    >>> no['x']['1'] = FallbackNode()
    >>> no['x']['1'].attrs['a'] = 1
    >>> no['x']['1'].attrs['d'] = -3
    >>> no['x']['2'] = FallbackNode()
    >>> no['x']['2'].attrs['b'] = 2
    >>> no['x']['2'].attrs['d'] = -2
    >>>
    >>> no['y'] = FallbackNode()
    >>> no['y'].fallback_key = '1'
    >>> no['y']['1'] = FallbackNode()
    >>> no['y']['1'].attrs['c'] = 3
    >>> no['y']['1'].attrs['d'] = -1
    >>> no['y']['2'] = FallbackNode()
    >>> no['y']['2'].attrs['d'] = 4
    >>> no.printtree()
    <class 'FallbackNode'>: root
      <class 'FallbackNode'>: x
        <class 'FallbackNode'>: 1
        <class 'FallbackNode'>: 2
      <class 'FallbackNode'>: y
        <class 'FallbackNode'>: 1
        <class 'FallbackNode'>: 2

Testing
=======

Fallbacks::

    >>> no['y']['2'].attrs['d']
    4

    >>> no['y']['2'].attrs['c']
    3

    >>> no['y']['2'].attrs['b']
    2

    >>> no['y']['2'].attrs['a']
    1

When there is no fallback::

    >>> no['y']['2'].attrs['z']
    Traceback (most recent call last):
    ...
    KeyError: 'z'

