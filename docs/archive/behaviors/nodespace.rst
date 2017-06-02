Nodespaces
----------

.. code-block:: pycon

    >>> from odict import odict
    >>> from plumber import plumbing
    >>> from node.behaviors import Adopt
    >>> from node.behaviors import Nodespaces
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import OdictStorage

    >>> @plumbing(
    ...     Adopt,
    ...     Nodespaces,
    ...     Nodify,
    ...     OdictStorage)
    ... class NodespacesNode(odict):
    ...     pass

    >>> node = NodespacesNode()
    >>> node.nodespaces
    odict([('__children__', <NodespacesNode object 'None' at ...>)])

    >>> @plumbing(
    ...     Adopt,
    ...     Nodify,
    ...     DefaultInit,
    ...     OdictStorage)
    ... class SomeNode(object):
    ...     pass

    >>> node['__children__']['child'] = SomeNode()
    >>> node['child']
    <SomeNode object 'child' at ...>

    >>> node['__children__']['child'] is node['child']
    True

    >>> node['__foo__'] = SomeNode()
    >>> node['__foo__']
    <SomeNode object '__foo__' at ...>

    >>> node['__foo__']['child'] = SomeNode()
    >>> node['__foo__']['child']
    <SomeNode object 'child' at ...>

    >>> node['__foo__']['child'] is node['child']
    False

    >>> node.nodespaces
    odict([('__children__', <NodespacesNode object 'None' at ...>), 
    ('__foo__', <SomeNode object '__foo__' at ...>)])

    >>> node['__inexistent__']
    Traceback (most recent call last):
      ...
    KeyError: '__inexistent__'

    >>> node['inexistent']
    Traceback (most recent call last):
      ...
    KeyError: 'inexistent'

    >>> del node['child']
    >>> node.keys()
    []

    >>> node['__foo__'].keys()
    ['child']

    >>> del node['__foo__']
    >>> node.nodespaces
    odict([('__children__', <NodespacesNode object 'None' at ...>)])
