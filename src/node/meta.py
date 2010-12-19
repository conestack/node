from node.interfaces import INode

class behavior(object):
    """Decorator to hook behaviors to Nodes.
    """
    
    def __init__(self, *behaviors):
        self.behaviors = behaviors

    def __call__(self, obj):
        if not INode.implementedBy(obj):
            msg = '``INode`` not implemented by ``%s``' % obj.__name__
            raise TypeError(msg)
        
        class NodeBehaviorMeta(type):
            
            def __init__(cls, name, bases, dct):
                # XXX: validate name clashes
                setattr(cls, '__behaviors_cls', self.behaviors)
                setattr(cls, '__behaviors_impl', dict())
                super(NodeBehaviorMeta, cls).__init__(name, bases, dct)
        
        class NodeBehaviorWrapper(obj):
            
            __metaclass__ = NodeBehaviorMeta
            __default_marker = object()
            
            def __getattribute__(self, name):
                try:
                    return super(NodeBehaviorWrapper,
                                 self).__getattribute__(name)
                except AttributeError, e:
                    behaviors = obj.__getattribute__(self, '__behaviors_cls')
                    impls = obj.__getattribute__(self, '__behaviors_impl')
                    for behavior in behaviors:
                        unbound = getattr(behavior, name, self.__default_marker)
                        if unbound is self.__default_marker:
                            continue
                        b_name = behavior.__name__
                        impl = impls.get(b_name, self.__default_marker)
                        if impl is self.__default_marker:
                            impl = impls[b_name] = behavior(self)
                        return getattr(impl, name)
                    raise AttributeError(name)
            
            def __repr__(self):
                name = self.__class__.__name__
                of_name = self.__class__.__bases__[0].__name__
                return "<%s object of '%s' at %s>" % (name, of_name,
                                                      hex(id(self))[:-1])
            
            __str__ = __repr__
        
        return NodeBehaviorWrapper