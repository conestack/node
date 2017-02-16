Attributes
==========

.. code-block:: pycon

    >>> from plumber import plumbing
    >>> from node.behaviors import NodeChildValidate
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage
    >>> from node.behaviors import Nodespaces
    >>> from node.behaviors import Attributes

    >>> @plumbing(
    ...     NodeChildValidate,
    ...     Nodespaces,
    ...     Attributes,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage)
    ... class AttributedNode(object):
    ...     pass

    >>> node = AttributedNode(name='attributed')
    >>> node.attribute_access_for_attrs
    False

    >>> node.attribute_access_for_attrs = True

    >>> node.attribute_access_for_attrs
    True

    >>> node.attrs
    <node.utils.AttributeAccess object at ...>

    >>> node.attrs.foo = 'bar'
    >>> node.attrs['foo']
    'bar'

    >>> node.attrs['bar'] = 'baz'
    >>> node.attrs.bar
    'baz'

    >>> node.attrs['oof'] = 'abc'
    >>> node.attrs.oof
    'abc'

    >>> node.attribute_access_for_attrs = False
    >>> node.attrs
    <NodeAttributes object 'attributed' at ...>

    >>> node.attrs['foo']
    'bar'

    >>> node.attrs.foo
    Traceback (most recent call last):
      ...
    AttributeError: 'NodeAttributes' object has no attribute 'foo'
