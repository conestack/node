Lifecycle
---------

Check NodeCreation:

.. code-block:: pycon

    >>> import zope.component
    >>> from plumber import plumbing
    >>> from node.interfaces import INode
    >>> from node.interfaces import INodeCreatedEvent
    >>> from node.interfaces import INodeAddedEvent
    >>> from node.interfaces import INodeModifiedEvent
    >>> from node.interfaces import INodeRemovedEvent
    >>> from node.interfaces import INodeDetachedEvent
    >>> from node.behaviors import Lifecycle
    >>> from node.behaviors import AttributesLifecycle
    >>> from node.behaviors import Attributes
    >>> from node.behaviors import NodeAttributes
    >>> from node.behaviors import Nodespaces
    >>> from node.behaviors import DefaultInit
    >>> from node.behaviors import Nodify
    >>> from node.behaviors import DictStorage

    >>> class Handler(object):
    ...     handled = []
    ...     def __call__(self, obj, event):
    ...         self.handled.append(event)
    >>> handler = Handler()

    >>> zope.component.provideHandler(handler, [INode, INodeCreatedEvent])
    >>> zope.component.provideHandler(handler, [INode, INodeAddedEvent])
    >>> zope.component.provideHandler(handler, [INode, INodeModifiedEvent])
    >>> zope.component.provideHandler(handler, [INode, INodeRemovedEvent])
    >>> zope.component.provideHandler(handler, [INode, INodeDetachedEvent])

    >>> @plumbing(
    ...     DefaultInit,
    ...     Nodify,
    ...     DictStorage)
    ... class NoLifecycleNode(object):
    ...     pass

    >>> root = NoLifecycleNode(name='no_notify')
    >>> handler.handled
    []

    >>> @plumbing(AttributesLifecycle)
    ... class LifecycleNodeAttributes(NodeAttributes):
    ...     pass

    >>> @plumbing(
    ...     Nodespaces,
    ...     Attributes,
    ...     Lifecycle,
    ...     DefaultInit,
    ...     Nodify,
    ...     DictStorage)
    ... class LifecycleNode(object):
    ...     attributes_factory = LifecycleNodeAttributes

    >>> root = LifecycleNode(name='root')
    >>> handler.handled
    [<node.events.NodeCreatedEvent object at ...>]

Check Node adding:

.. code-block:: pycon

    >>> del handler.handled[0]
    >>> child1 = LifecycleNode()
    >>> root['child1'] = child1
    >>> handler.handled
    [<node.events.NodeCreatedEvent object at ...>, 
    <node.events.NodeAddedEvent object at ...>]

Check Node modification:

.. code-block:: pycon

    >>> del handler.handled[0]
    >>> del handler.handled[0]

    >>> ignore = child1.attrs

No event, despite the node creation for the attributes nodespace:

.. code-block:: pycon

    >>> handler.handled
    []

Node modified events if the attributes nodespace is changed:

.. code-block:: pycon

    >>> child1.attrs['foo'] = 1
    >>> handler.handled
    [<node.events.NodeModifiedEvent object at ...>]

    >>> del handler.handled[0]
    >>> del child1.attrs['foo']
    >>> handler.handled
    [<node.events.NodeModifiedEvent object at ...>]

Check Node Deletion:

.. code-block:: pycon

    >>> handler.handled = []
    >>> del root['child1']
    >>> handler.handled
    [<node.events.NodeRemovedEvent object at ...>]

Check Node Detach:

.. code-block:: pycon

    >>> child2 = LifecycleNode()
    >>> root['child2'] = child2
    >>> handler.handled = []
    >>> detached = root.detach('child2')
    >>> handler.handled
    [<node.events.NodeDetachedEvent object at ...>]

Check notify suppress on ``__setitem__``:

.. code-block:: pycon

    >>> handler.handled = []
    >>> root._notify_suppress = True
    >>> root['child'] = NoLifecycleNode()
    >>> handler.handled
    []

Check notify suppress on attributes manipulation:

.. code-block:: pycon

    >>> attrs = root.attrs
    >>> attrs
    <LifecycleNodeAttributes object 'root' at ...>

    >>> attrs['foo'] = 'foo'
    >>> del attrs['foo']
    >>> handler.handled
    []
