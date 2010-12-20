from zope.interface import implements
from node.interfaces import (
    INode,
    IBehavior,
)

BEFORE_HOOKS = dict()
AFTER_HOOKS = dict()


class before(object):
    """Behavior before hook decorator.
    """
    
    def __init__(self, func_name):
        self.func_name = func_name
    
    def __call__(self, func):
        func.hook_name = self.func_name
        BEFORE_HOOKS.setdefault(self.func_name, list()).append(func)
        return func


class after(object):
    """Behavior before hook decorator.
    """
    
    def __init__(self, func_name):
        self.func_name = func_name
    
    def __call__(self, func):
        func.hook_name = self.func_name
        AFTER_HOOKS.setdefault(self.func_name, list()).append(func)
        return func


class behavior(object):
    """Decorator for extending nodes by behaviors.
    """
    
    def __init__(self, *behaviors):
        for beh in behaviors:
            if not IBehavior.implementedBy(beh):
                msg = '``IBehavior`` not implemented by ``%s``' % beh.__name__
                raise TypeError(msg)
        self.behaviors = behaviors

    def __call__(self, obj):
        if not INode.implementedBy(obj):
            msg = '``INode`` not implemented by ``%s``' % obj.__name__
            raise TypeError(msg)
        
        ###
        # node wrapper metaclass.
        
        class NodeBehaviorMeta(type):
            """Metaclass for NodeBehaviorWrapper.
            
            Writes behavior class objects to cls.__behaviors_cls and creates
            empty dict cls.__behaviors_ins, which later contains the bahavior
            class instances.
            """
            
            def __init__(cls, name, bases, dct):
                setattr(cls, '__behaviors_cls', self.behaviors)
                super(NodeBehaviorMeta, cls).__init__(name, bases, dct)
        
        ###
        # wrapper for decorated node.
        
        class NodeBehaviorWrapper(obj):
            """Derives from given ``obj`` by decorator and wrap node behavior.
            """
            __metaclass__ = NodeBehaviorMeta
            __default_marker = object()
            
            implements(INode) # after __metaclass__ definition.
            
            def __getattribute__(self, name):
                # ``super`` is at such places confusing and seem to be buggy as
                # well. address directly where we want to do something.
                try:
                    # try to get requested attribute from self (the node)
                    attr = obj.__getattribute__(self, name)
                    
                    # we've found attribute, consider before and after hooks
                    
                    # before hooks
                    before_hooks = list()
                    
                    # after hooks, later
                    after_hooks = list()
                    
                    # requested attr in before hooks ?
                    if name in BEFORE_HOOKS:
                        
                        # get own behavior classes
                        behaviors = obj.__getattribute__(self, '__behaviors_cls')
                        
                        # iterate all registered before hooks by requested 
                        # attribute name
                        for hook in BEFORE_HOOKS[name]:
                            
                            # iterate own behavior classes
                            for behavior in behaviors:
                                
                                # try to get hook function from hook
                                try:
                                    func = getattr(behavior, hook.__name__)
                                # behavior does not provide hook, ignore
                                except:
                                    continue
                            
                                # hook func is behavior func. ??
                                # XXX: not sure if this test is valid
                                if not func.__code__ is hook.__code__:
                                    continue
                                
                                # hook func found on behavior, add to 
                                # before_hooks
                                before_hooks.append((behavior, func))
                    
                    # wrap if hook is found
                    if before_hooks or after_hooks:
                        
                        node = self
                        
                        # wrap. Currently expected as function
                        def wrapper(*args, **kw):
                            
                            # execute before hooks
                            for hook in before_hooks:
                                pass
                                
                                # self does not work here 
                                #print node
                                #import pdb;pdb.set_trace()
                                
                                #try:
                                #    ins = obj.__getattribute__(self, '__behaviors_ins')
                                #except AttributeError:
                                #    obj.__setattr__(self, '__behaviors_ins', dict())
                                #    ins = obj.__getattribute__(self, '__behaviors_ins')
                                
                                #b_name = behavior.__name__
                            
                            # XXX: execute after hooks
                            #for hook in after_hooks:
                            #    pass
                            return attr(*args, **kw)
                        
                        wrapper.func_name = attr.func_name
                        wrapper.__doc__ = attr.__doc__
                        wrapper.wrapped = attr
                        return wrapper
                    
                    return attr
                    
                except AttributeError, e:
                    # try to find requested attribute on behavior
                    # create behavior instance if necessary
                    behaviors = obj.__getattribute__(self, '__behaviors_cls')
                    try:
                        ins = obj.__getattribute__(self, '__behaviors_ins')
                    except AttributeError:
                        obj.__setattr__(self, '__behaviors_ins', dict())
                        ins = obj.__getattribute__(self, '__behaviors_ins')
                    for behavior in behaviors:
                        unbound = getattr(behavior, name, self.__default_marker)
                        if unbound is self.__default_marker:
                            continue
                        b_name = behavior.__name__
                        instance = ins.get(b_name, self.__default_marker)
                        if instance is self.__default_marker:
                            instance = ins[b_name] = behavior(self)
                        return getattr(instance, name)
                    raise AttributeError(name)
            
            def __repr__(self):
                name = unicode(self.__name__).encode('ascii', 'replace')
                return "<%s object '%s' at %s>" % (obj.__name__,
                                                   name,
                                                   hex(id(self))[:-1])
            
            __str__ = __repr__
            
            @property
            def noderepr(self):
                return "<%s object of '%s' at %s>" % (self.__class__.__name__,
                                                      obj.__name__,
                                                      hex(id(self))[:-1])
        
        # return wrapped
        return NodeBehaviorWrapper
