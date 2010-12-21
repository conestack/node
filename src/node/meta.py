from zope.interface import implements
from node.interfaces import (
    INode,
    IBehavior,
)

_BEFORE_HOOKS = dict()
_AFTER_HOOKS = dict()
_default_marker = object()


class _hook(object):
    """Abstract hook decorator.
    """
    def __init__(self, hooks, func_name):
        self.hooks = hooks
        self.func_name = func_name
    
    def __call__(self, func):
        # no way here to determine class func is member of, just register
        # XXX: check if hook was already added? should not happen that hook
        #      gets registered twice???
        func.hook_name = self.func_name
        self.hooks.setdefault(self.func_name, list()).append(func)
        return func


class before(_hook):
    """Before hook decorator.
    """
    def __init__(self, func_name):
        super(before, self).__init__(_BEFORE_HOOKS, func_name)


class after(_hook):
    """Behavior before hook decorator.
    """
    def __init__(self, func_name):
        super(after, self).__init__(_AFTER_HOOKS, func_name)


def _behavior_ins(class_, instance):
    """Return behaviors instances container of instance by
    class_.__getattribute__.
    """
    try:
        ins = class_.__getattribute__(instance, '__behaviors_ins')
    except AttributeError:
        class_.__setattr__(instance, '__behaviors_ins', dict())
        ins = class_.__getattribute__(instance, '__behaviors_ins')
    return ins


def _behavior_get(instance, ins, behavior):
    """
    """
    name = behavior.__name__
    ret = ins.get(name, _default_marker)
    if ret is _default_marker:
        # XXX: unwrap (or rewrap?) __getattribute__ of instance first
        #      we dont want hooks to be called from within bahavior.
        ret = ins[name] = behavior(instance)
    return ret


def _collect_hooks(class_, instance, hooks, name):
    ret = list()
    # requested attr in hooks ?
    if name in hooks:
        # get own behavior classes
        behaviors = class_.__getattribute__(instance, '__behaviors_cls')
        # iterate all registered hooks by requested attribute name
        for hook in hooks[name]:
            # iterate instance behavior classes
            for behavior in behaviors:
                # try to get hook function from hook
                try:
                    func = getattr(behavior, hook.__name__)
                # behavior does not provide hook, ignore
                except:
                    continue
                # check is hook func is behavior func
                if not func.func_code is hook.func_code:
                    continue
                # hook func found on behavior, add to 
                # before_hooks
                ret.append((behavior, func))
    return ret

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
            
            implements(INode) # after __metaclass__ definition.
            
            def __getattribute__(self, name):
                # ``super`` is at such places confusing and seem to be buggy as
                # well. address directly where we want to do something.
                try:
                    # try to get requested attribute from self (the node)
                    attr = obj.__getattribute__(self, name)
                    # attribute found, collect before and after hooks
                    before = _collect_hooks(obj, self, _BEFORE_HOOKS, name)
                    after = _collect_hooks(obj, self, _AFTER_HOOKS, name)
                    # wrap attribute if hooks are found
                    if before or after:
                        node = self # write self to node for access in wrapper
                        def wrapper(*args, **kw):
                            ins = _behavior_ins(obj, node)
                            # execute before hooks
                            for behavior, hook in before:
                                instance = _behavior_get(node, ins, behavior)
                                getattr(instance, hook.func_name)(*args, **kw)
                            # get return value of requested attr
                            try:
                                ret = attr(*args, **kw)
                            except Exception, e:
                                # XXX: raise directly or call after hooks first?
                                #      i suppose raise...
                                raise e
                            # execute after hooks
                            for behavior, hook in after:
                                instance = _behavior_get(node, ins, behavior)
                                getattr(instance, hook.func_name)(*args, **kw)
                            return ret
                        wrapper.func_name = attr.func_name
                        wrapper.__doc__ = attr.__doc__
                        wrapper.wrapped = attr
                        return wrapper
                    return attr
                except AttributeError, e:
                    # try to find requested attribute on behavior
                    # create behavior instance if necessary
                    behaviors = obj.__getattribute__(self, '__behaviors_cls')
                    ins = _behavior_ins(obj, self)
                    for behavior in behaviors:
                        unbound = getattr(behavior, name, _default_marker)
                        if unbound is _default_marker:
                            continue
                        instance = _behavior_get(self, ins, behavior)
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
