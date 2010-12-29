# http://www.python.org/download/releases/2.3/mro/
# http://users.rcn.com/python/download/Descriptor.htm
# http://www.ibm.com/developerworks/library/l-pymeta.html
# http://www.artima.com/weblogs/viewpost.jsp?thread=236275

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

_explicit_hooks = ['__delitem__', '__getitem__', '__setitem__']

_INS_ATTR = '__behaviors_ins'
_CLS_ATTR = '__behaviors_cls'

_ins_attr = _INS_ATTR
_cls_attr = _CLS_ATTR


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
        if self.func_name in ['__setattr__', '__getattribute__']:
            raise RuntimeError('Hooking forbidden for ``__setattr__`` and '
                               '``__getattribute__``')
        func.hook_name = self.func_name
        self.hooks.setdefault(self.func_name, list()).append(func)
        return func


class before(_BehaviorHook):
    """Before hook decorator.
    """
    def __init__(self, func_name):
        super(before, self).__init__(_BEFORE_HOOKS, func_name)


class after(_BehaviorHook):
    """After hook decorator.
    """
    def __init__(self, func_name):
        super(after, self).__init__(_AFTER_HOOKS, func_name)


###
# new meta
def _check_write_exposed_ns_conflict(node_cls, behavior_classes):
    provided = dir(node_cls)
    for behavior in behavior_classes:
        for exposed in behavior.expose_write_access_for:
            if exposed in provided:
                msg = '%s exposes "%s", which is already provided by %s' % (
                    str(behavior), exposed, str(node_cls))
                raise RuntimeError(msg)


def _wrapfunc(orgin, wrapped):
    wrapped.func_name = orgin.func_name
    wrapped.__doc__ = orgin.__doc__
    wrapped.wrapped = orgin
    return wrapped


###
# new meta
def _hook_names(classes):
    def collect_hooks(ret, classes, hooks):
        for cls in classes:
            for name in dir(cls):
                try:
                    hook_func = getattr(cls, name)
                except AttributeError:
                    continue
                if not hasattr(hook_func, 'func_code'):
                    continue
                for reg_name, reg_funcs in hooks.items():
                    for reg_func in reg_funcs:
                        if not hook_func.func_code is reg_func.func_code:
                            continue
                        ret.add(reg_name)
    ret = set()
    before = collect_hooks(ret, classes, _BEFORE_HOOKS)
    after = collect_hooks(ret, classes, _AFTER_HOOKS)
    return list(ret)


###
# new meta
def _collect_hooks_for(classes, name):
    """Collect hooks by name defined in behavior classes.
    
    Returns 2-tuple with before and after hooks.
    """
    def collect_hooks(classes, name, hooks):
        ret = list()
        if name in hooks:
            for hook in hooks[name]:
                # iterate instance behavior classes
                for cls in classes:
                    # try to get hook function from hook
                    try:
                        hook_func = getattr(cls, hook.__name__)
                    # behavior does not provide hook, ignore
                    except:
                        continue
                    # check if hook func is behavior func
                    if not hook_func.func_code is hook.func_code:
                        continue
                    # hook func found on behavior, add to 
                    # before_hooks
                    ret.append((cls, hook_func))
        return ret
    before = collect_hooks(classes, name, _BEFORE_HOOKS)
    after = collect_hooks(classes, name, _AFTER_HOOKS)
    return before, after


###
# new meta
def _hook_behaviored_functions(node_cls, behavior_classes):
    pass


def _create_behavior(instance, node_cls, behavior_cls):
    
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
            return node_cls.__getattribute__(context, name)
        
        def __repr__(self):
            return node_cls.__repr__(self.context)
    
    for func_name in _explicit_hooks:
        proxy = _wrap_proxy_method(node_cls, func_name)
        setattr(UnwrappedContextProxy, func_name, proxy)
    return behavior_cls(UnwrappedContextProxy(instance))


###
# new meta
def _add__behavior_instances_property(node_cls):
    def _behavior_instances(self):
        try:
            behaviors = node_cls.__getattribute__(self, _INS_ATTR)
        except AttributeError:
            node_cls.__setattr__(self, _INS_ATTR, odict())
            behaviors = node_cls.__getattribute__(self, _INS_ATTR)
            classes = node_cls.__getattribute__(self, _CLS_ATTR)
            for cls in classes:
                name = cls.__name__
                behaviors[name] = _create_behavior(self, node_cls, cls)
        return behaviors
    node_cls._behavior_instances = property(_behavior_instances)


###
# new meta
def _alter_node___setattr__(node_cls):
    # XXX remove when funcdef.wrapped is used
    __setattr__orgin = node_cls.__setattr__
    def __setattr__(self, name, val):
        for behavior in self._behavior_instances.values():
            if name in behavior.expose_write_access_for:
                setattr(behavior, name, val)
                return
        # XXX use funcdef.wrapped here
        __setattr__orgin(self, name, val)
    node_cls.__setattr__ = _wrapfunc(__setattr__orgin, __setattr__)


###
# new meta
def _alter_node___getattribute__(node_cls):
    def __getattribute__(self, name):
        try:
            # try to get requested attribute from self (the node)
            return self.__getattribute__.wrapped(self, name)
        except AttributeError, e:
            # try to find requested attribute on behavior
            classes = self.__getattribute__.wrapped(self, _CLS_ATTR)
            for cls in classes:
                unbound = getattr(cls, name, _default_marker)
                if unbound is _default_marker:
                    continue
                behavior = self._behavior_instances[cls.__name__]
                return getattr(behavior, name)
            raise AttributeError(name)
    node_cls.__getattribute__ = _wrapfunc(node_cls.__getattribute__,
                                          __getattribute__)


def _wrap_proxy_method(cls, func_name):
    def wrapper(self, *args, **kw):
        context = object.__getattribute__(self, 'context')
        func = cls.__getattribute__(context, func_name)
        return func(__hooks=False, *args, **kw)
    return wrapper


def _collect_hooks(cls, instance, hooks, name):
    ret = list()
    # requested attr in hooks ?
    if name in hooks:
        # get own behavior classes
        behaviors = cls.__getattribute__(instance, _cls_attr)
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


def _wrap_class_method(node_cls, method, name):
    def wrapper(self, *pargs, **kw):
        hooks = kw.pop('__hooks', True)
        if hooks:
            # collect before and after hooks
            before = _collect_hooks(node_cls, self, _BEFORE_HOOKS, name)
            after = _collect_hooks(node_cls, self, _AFTER_HOOKS, name)
            if before or after:
                behavior_instances = self._behavior_instances
                # execute before hooks
                for behavior, hook in before:
                    instance = behavior_instances[behavior.__name__]
                    getattr(instance, hook.func_name)(*pargs, **kw)
        # get return value of requested method
        ret = method(self, *pargs, **kw)
        if hooks and after:
            # execute after hooks
            for behavior, hook in after:
                instance = behavior_instances[behavior.__name__]
                getattr(instance, hook.func_name)(*pargs, **kw)
        # return ret value from requested method
        return ret
    return _wrapfunc(method, wrapper)


def _wrap_instance_member(node_cls, instance, member, name):
    # collect before and after hooks
    before = _collect_hooks(node_cls, instance, _BEFORE_HOOKS, name)
    after = _collect_hooks(node_cls, instance, _AFTER_HOOKS, name)
    # wrap attribute if hooks are found
    if before or after:
        behavior_instances = instance._behavior_instances
        def wrapper(*args, **kw):
            # execute before hooks
            for behavior, hook in before:
                instance = behavior_instances[behavior.__name__]
                getattr(instance, hook.func_name)(*args, **kw)
            # get return value of requested member
            ret = member(*args, **kw)
            # execute after hooks
            for behavior, hook in after:
                instance = behavior_instances[behavior.__name__]
                getattr(instance, hook.func_name)(*args, **kw)
            # return ret value from requested member
            return ret
        return _wrapfunc(member, wrapper)
    return member


class behavior(object):
    """Decorator for extending nodes by behaviors.
    """
    
    def __init__(self, *behaviors):
        for beh in behaviors:
            if not IBehavior.implementedBy(beh):
                msg = '``IBehavior`` not implemented by ``%s``' % beh.__name__
                raise TypeError(msg)
        self.behaviors = behaviors

    def __call__(self, node_cls):
        if not INode.implementedBy(node_cls):
            msg = '``INode`` not implemented by ``%s``' % node_cls.__name__
            raise TypeError(msg)
        
        class NodeBehaviorMeta(type):
            """Metaclass for NodeBehaviorWrapper.
            
            Writes behavior class objects to cls.__behaviors_cls.
            """
            def __init__(cls, name, bases, dct):
                super(NodeBehaviorMeta, cls).__init__(name, bases, dct)
                # wrap explicit.
                for name in dir(cls):
                    if name not in _explicit_hooks:
                        continue
                    method = getattr(cls, name)
                    setattr(cls, name, _wrap_class_method(cls, method, name))
                setattr(cls, _cls_attr, self.behaviors)
        
        class NodeBehaviorWrapper(node_cls):
            """Wrapper for decorated node.
            
            Derives from given ``node_cls`` by decorator and wrap node behavior.
            """
            __metaclass__ = NodeBehaviorMeta
            _wrapped = node_cls
            
            implements(INode) # after __metaclass__ definition!
            
            @property
            def _behavior_instances(self):
                """Return behavior instances in odict. If not existent create.
                """
                try:
                    behaviors = node_cls.__getattribute__(self, _ins_attr)
                except AttributeError:
                    node_cls.__setattr__(self, _ins_attr, odict())
                    behaviors = node_cls.__getattribute__(self, _ins_attr)
                    classes = node_cls.__getattribute__(self, _cls_attr)
                    for cls in classes:
                        name = cls.__name__
                        behaviors[name] = _create_behavior(self, node_cls, cls)
                return behaviors
            
            def __setattr__(self, name, val):
                for behavior in self._behavior_instances.values():
                    if name in behavior.expose_write_access_for:
                        setattr(behavior, name, val)
                        return
                node_cls.__setattr__(self, name, val)
            
            def __getattribute__(self, name):
                try:
                    # try to get requested attribute from self (the node)
                    member = node_cls.__getattribute__(self, name)
                    return _wrap_instance_member(node_cls, self, member, name)
                except AttributeError, e:
                    # try to find requested attribute on behavior
                    # create behavior instance if necessary
                    classes = node_cls.__getattribute__(self, _cls_attr)
                    for class_ in classes:
                        unbound = getattr(class_, name, _default_marker)
                        if unbound is _default_marker:
                            continue
                        behavior = self._behavior_instances[class_.__name__]
                        return getattr(behavior, name)
                    raise AttributeError(name)
            
            def __repr__(self):
                return node_cls.__repr__(self)

            @property
            def noderepr(self):
                return node_cls.noderepr.fget(self)           
            
            __str__ = __repr__
                    
        # return wrapped
        return NodeBehaviorWrapper
