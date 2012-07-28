node.behaviors.Lifecycle
------------------------

Check NodeCreation.::

    >>> import zope.component
    
    >>> from node.interfaces import (
    ...     INode,
    ...     INodeCreatedEvent,
    ...     INodeAddedEvent,
    ...     INodeModifiedEvent,
    ...     INodeRemovedEvent,
    ...     INodeDetachedEvent,
    ... )
    
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
    
    >>> from plumber import plumber
    >>> from node.behaviors import (
    ...     Lifecycle, 
    ...     AttributesLifecycle, 
    ...     Attributes, 
    ...     NodeAttributes, 
    ...     Nodespaces, 
    ...     DefaultInit,
    ...     Nodify, 
    ...     DictStorage, 
    ... )
    
    >>> class NoLifecycleNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         DefaultInit,
    ...         Nodify,
    ...         DictStorage,
    ...     )
    
    >>> root = NoLifecycleNode(name='no_notify')
    >>> handler.handled
    []
    
    >>> class LifecycleNodeAttributes(NodeAttributes):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = AttributesLifecycle
    
    >>> class LifecycleNode(object):
    ...     __metaclass__ = plumber
    ...     __plumbing__ = (
    ...         Nodespaces,
    ...         Attributes,
    ...         Lifecycle,
    ...         DefaultInit,
    ...         Nodify,
    ...         DictStorage,
    ...     )
    ...     attributes_factory = LifecycleNodeAttributes

    >>> root = LifecycleNode(name='root')
    >>> handler.handled
    [<node.events.NodeCreatedEvent object at ...>]

Check Node adding.::
    
    >>> del handler.handled[0]
    >>> child1 = LifecycleNode()
    >>> root['child1'] = child1
    >>> handler.handled
    [<node.events.NodeCreatedEvent object at ...>, 
    <node.events.NodeAddedEvent object at ...>]

Check Node modification.::

    >>> del handler.handled[0]
    >>> del handler.handled[0]

    >>> ignore = child1.attrs
    
No event, despite the node creation for the attributes nodespace.::

    >>> handler.handled
    []
    
Node modified events if the attributes nodespace is changed.::

    >>> child1.attrs['foo'] = 1
    >>> handler.handled
    [<node.events.NodeModifiedEvent object at ...>]
    
    >>> del handler.handled[0]
    >>> del child1.attrs['foo']  
    >>> handler.handled
    [<node.events.NodeModifiedEvent object at ...>]

Check Node Deletion.:: 

    >>> handler.handled = []
    >>> del root['child1']
    >>> handler.handled
    [<node.events.NodeRemovedEvent object at ...>]

Check Node Detach.:: 

    >>> child2 = LifecycleNode()
    >>> root['child2'] = child2
    >>> handler.handled = []
    >>> detached = root.detach('child2')    
    >>> handler.handled
    [<node.events.NodeDetachedEvent object at ...>]

Check notify suppress on __setitem__::

    >>> handler.handled = []
    >>> root._notify_suppress = True
    >>> root['child'] = NoLifecycleNode()
    >>> handler.handled
    []

Check notify suppress on attributes manipulation::

    >>> attrs = root.attrs
    >>> attrs
    <LifecycleNodeAttributes object 'root' at ...>
    
    >>> attrs['foo'] = 'foo'
    >>> del attrs['foo']
    >>> handler.handled
    []
