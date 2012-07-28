node.behaviors.Attributes
=========================

::

    >>> from plumber import plumber
    >>> from node.behaviors import (
    ...     NodeChildValidate,
    ...     DefaultInit,
    ...     Nodify,
    ...     OdictStorage,
    ...     Nodespaces,
    ...     Attributes,
    ... )
    
    >>> class AttributedNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         NodeChildValidate,
    ...         Nodespaces,
    ...         Attributes,
    ...         DefaultInit,
    ...         Nodify,
    ...         OdictStorage,
    ...     )

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
