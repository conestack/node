import types
from odict import odict
from zope.interface import (
    implements,
    implementedBy,
)
from node.interfaces import (
    INode,
    IBehavior,
)

_BEFORE_HOOKS = dict()
_AFTER_HOOKS = dict()
_default_marker = object()
_private_hook_whitelist = ['__delitem__', '__getitem__', '__setitem__']


class BaseBehavior(object):
    """Base behavior class.
    """
    implements(IBehavior)
    
    expose_write_access_for = list()
    
    def __init__(self, context):
        self._context = context
    
    def _get_context(self):
        return self._context
    
    def _set_context(self, val):
        raise RuntimeError('Overriding ``context`` forbidden')
    
    context = property(_get_context, _set_context)
    
    def _debug(self, decorator, hooked, *args, **kw):
        print '* ' + decorator + ' ``' + hooked + '`` of ' + \
              str(self) + ' \n  on ' + str(self.context) + \
              ' \n  with args ``' + str(args) + \
              '`` \n  and kw ``' + str(kw) + '`` ---'


class _BehaviorHook(object):
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


class before(_BehaviorHook):
    """Before hook decorator.
    """
    def __init__(self, func_name):
        super(before, self).__init__(_BEFORE_HOOKS, func_name)


class after(_BehaviorHook):
    """Behavior before hook decorator.
    """
    def __init__(self, func_name):
        super(after, self).__init__(_AFTER_HOOKS, func_name)


def _wrap_proxy_method(class_, func_name):
    def wrapper(obj, *args, **kw):
        context = object.__getattribute__(obj, 'context')
        func = class_.__getattribute__(context, func_name)
        return func(__hooks=False, *args, **kw)
    return wrapper


def _create_behavior(instance, behavior_class):
    class_ = instance.__class__._wrapped
    name = behavior_class.__name__
    
    class UnwrappedContextProxy(object):
        """Class to unwrap calls on behavior extended node.
        
        This is needed to acess self.context.whatever in behavior
        implementation without computing before and after hooks bound
        to ``whatever``.
        """
        def __init__(self, context):
            self.context = context
        
        def __getattribute__(self, name):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                pass
            context = object.__getattribute__(self, 'context')
            return class_.__getattribute__(context, name)
        
        def __repr__(self):
            return self.context.__class__._wrapped.__repr__(self.context)
    
    for func_name in _private_hook_whitelist:
        proxy = _wrap_proxy_method(class_, func_name)
        setattr(UnwrappedContextProxy, func_name, proxy)
    return behavior_class(UnwrappedContextProxy(instance))


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


def _wrapfunc(old, new):
    new.func_name = old.func_name
    new.__doc__ = old.__doc__
    new.wrapped = old
    return new


def _wrap_class_method(attr, name):
    def wrapper(obj, *pargs, **kw):
        cla = obj._wrapped
        hooks = kw.pop('__hooks', True)
        if hooks:
            # collect before and after hooks
            before = _collect_hooks(cla, obj, _BEFORE_HOOKS, name)
            after = _collect_hooks(cla, obj, _AFTER_HOOKS, name)
            if before or after:
                behavior_instances = obj._behavior_instances
                # execute before hooks
                for behavior, hook in before:
                    instance = behavior_instances[behavior.__name__]
                    getattr(instance, hook.func_name)(*pargs, **kw)
        # get return value of requested attr
        ret = attr(obj, *pargs, **kw)
        if hooks and after:
            # execute after hooks
            for behavior, hook in after:
                instance = behavior_instances[behavior.__name__]
                getattr(instance, hook.func_name)(*pargs, **kw)
        # return ret value from requested attr
        return ret
    return _wrapfunc(attr, wrapper)


def _wrap_instance_method(cla, obj, attr, name):
    # collect before and after hooks
    before = _collect_hooks(cla, obj, _BEFORE_HOOKS, name)
    after = _collect_hooks(cla, obj, _AFTER_HOOKS, name)
    # wrap attribute if hooks are found
    if before or after:
        behavior_instances = obj._behavior_instances
        def wrapper(*args, **kw):
            # execute before hooks
            for behavior, hook in before:
                instance = behavior_instances[behavior.__name__]
                getattr(instance, hook.func_name)(*args, **kw)
            # get return value of requested attr
            ret = attr(*args, **kw)
            # execute after hooks
            for behavior, hook in after:
                instance = behavior_instances[behavior.__name__]
                getattr(instance, hook.func_name)(*args, **kw)
            # return ret value from requested attr
            return ret
        return _wrapfunc(attr, wrapper)
    return attr


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
        
        class NodeBehaviorMeta(type):
            """Metaclass for NodeBehaviorWrapper.
            
            Writes behavior class objects to cls.__behaviors_cls and creates
            empty dict cls.__behaviors_ins, which later contains the bahavior
            class instances.
            """
            def __init__(cls, name, bases, dct):
                # wrap class attribues.
                for name in dir(cls):
                    if name not in _private_hook_whitelist:
                        continue
                    attr = getattr(cls, name)
                    setattr(cls, name, _wrap_class_method(attr, name))
                setattr(cls, '__behaviors_cls', self.behaviors)
                super(NodeBehaviorMeta, cls).__init__(name, bases, dct)
        
        class NodeBehaviorWrapper(obj):
            """Wrapper for decorated node.
            
            Derives from given ``obj`` by decorator and wrap node behavior.
            """
            __metaclass__ = NodeBehaviorMeta
            _wrapped = obj
            
            implements(INode) # after __metaclass__ definition!

            @property
            def _behavior_instances(self):
                try:
                    behaviors = obj.__getattribute__(self, '__behaviors_ins')
                except AttributeError:
                    obj.__setattr__(self, '__behaviors_ins', odict())
                    behaviors = obj.__getattribute__(self, '__behaviors_ins')
                    classes = obj.__getattribute__(self, '__behaviors_cls')
                    for class_ in classes:
                        name = class_.__name__
                        behaviors[name] = _create_behavior(self, class_)
                return behaviors
            
            def __setattr__(self, name, val):
                for behavior in self._behavior_instances.values():
                    if name in behavior.expose_write_access_for:
                        setattr(behavior, name, val)
                        return
                obj.__setattr__(self, name, val)
            
            def __getattribute__(self, name):
                # ``super`` is at such places confusing and seem to be buggy as
                # well. address directly where we want to do something.
                try:
                    # try to get requested attribute from self (the node)
                    attr = obj.__getattribute__(self, name)
                    return _wrap_instance_method(obj, self, attr, name)
                except AttributeError, e:
                    # try to find requested attribute on behavior
                    # create behavior instance if necessary
                    classes = obj.__getattribute__(self, '__behaviors_cls')
                    for class_ in classes:
                        unbound = getattr(class_, name, _default_marker)
                        if unbound is _default_marker:
                            continue
                        behavior = self._behavior_instances[class_.__name__]
                        return getattr(behavior, name)
                    raise AttributeError(name)
            
            def __repr__(self):
                return self.__class__._wrapped.__repr__(self)

            @property
            def noderepr(self):
                import pdb;pdb.set_trace()
                return self.__class__._wrapped.noderepr.fget(self)            
            
            __str__ = __repr__
                    
        # return wrapped
        return NodeBehaviorWrapper
