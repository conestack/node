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
_INS_ATTR = '__behaviors_ins'
_CLS_ATTR = '__behaviors_cls'
_default_marker = object()


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
        _check_write_exposed_ns_conflict(node_cls, self.behaviors)
        setattr(node_cls, _CLS_ATTR, self.behaviors)
        _add__behavior_instances_property(node_cls)
        _hook_behaviored_functions(node_cls, self.behaviors)
        _alter_node___getattribute__(node_cls)
        _alter_node___setattr__(node_cls)
        return node_cls


def _wrapfunc(orgin, wrapped):
    if hasattr(orgin, 'func_name'):
        wrapped.func_name = orgin.func_name
    wrapped.__doc__ = orgin.__doc__
    wrapped.wrapped = orgin
    return wrapped


def _check_write_exposed_ns_conflict(node_cls, behavior_classes):
    provided = dir(node_cls)
    for behavior in behavior_classes:
        for exposed in behavior.expose_write_access_for:
            if exposed in provided:
                msg = '%s exposes "%s", which is already provided by %s' % (
                    str(behavior), exposed, str(node_cls))
                raise RuntimeError(msg)


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


def _collect_hooks_for(classes, name):
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


def _wrap_hooked(node_cls, behavior_classes, towrap, name):
    unwrapped = towrap
    before, after = _collect_hooks_for(behavior_classes, name)
    def hooked(self, *pargs, **kw):
        behavior_instances = self._behavior_instances
        # execute before hooks
        for behavior, hook in before:
            instance = behavior_instances[behavior.__name__]
            getattr(instance, hook.func_name)(*pargs, **kw)
        # get return value of requested
        ret = unwrapped(self, *pargs, **kw)
        # execute after hooks
        for behavior, hook in after:
            instance = behavior_instances[behavior.__name__]
            getattr(instance, hook.func_name)(*pargs, **kw)
        # return ret value from requested method
        return ret
    setattr(node_cls, name, _wrapfunc(towrap, hooked))


def _wrap_hooked_unwrapper(wrapper_cls, wrapped, name):
    orgin = wrapped.wrapped
    def unwrapped(self, *pargs, **kw):
        context = object.__getattribute__(self, 'context')
        return orgin(context, *pargs, **kw)
    setattr(wrapper_cls, name, unwrapped)


def _create_behavior(instance, node_cls, behavior_cls):
    
    class UnwrappedContextProxy(object):
        """Class to unwrap calls on behavior extended node.
        
        This is needed to acess self.context.whatever in behavior
        implementation without computing before and after hooks bound
        to ``whatever``.
        """
        def __init__(self, context):
            object.__setattr__(self, 'context', context)
        
        def __getattribute__(self, name):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                pass
            context = object.__getattribute__(self, 'context')
            attribute = node_cls.__getattribute__(context, name)
            if hasattr(attribute, 'wrapped'):
                attribute = types.MethodType(attribute.wrapped, context, node_cls)
            return attribute
        
        def __setattr__(self, name, value):
            setattr(self.context, name, value)
        
        def __getitem__(self, name):
            return self.context[name]
        
        def __setitem__(self, name, value):
            self.context[name] = value
        
        def __delitem__(self, name):
            del self.context[name]
        
        def __repr__(self):
            return node_cls.__repr__(self.context)
    
    behavior_classes = getattr(node_cls, _CLS_ATTR)
    for name in _hook_names(behavior_classes):
        try:
            wrapped = getattr(node_cls, name)
        except AttributeError, e:
            continue
        if not hasattr(wrapped, 'wrapped'):
            continue
        _wrap_hooked_unwrapper(UnwrappedContextProxy, wrapped, name)
    return behavior_cls(UnwrappedContextProxy(instance))


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


def _hook_behaviored_functions(node_cls, behavior_classes):
    for name in _hook_names(behavior_classes):
        try:
            towrap = getattr(node_cls, name)
        except AttributeError, e:
            continue
        _wrap_hooked(node_cls, behavior_classes, towrap, name)


def _alter_node___setattr__(node_cls):
    orgin = node_cls.__setattr__
    def __setattr__(self, name, val):
        classes = getattr(node_cls, _CLS_ATTR)
        for cls in classes:
            if not name in cls.expose_write_access_for:
                continue
            attr = getattr(cls, name, _default_marker)
            if attr is _default_marker:
                continue
            behavior = self._behavior_instances[cls.__name__]
            behavior.__setattr__(name, val)
            return
        orgin(self, name, val)
    node_cls.__setattr__ = _wrapfunc(node_cls.__setattr__, __setattr__)


def _alter_node___getattribute__(node_cls):
    orgin = node_cls.__getattribute__
    def __getattribute__(self, name):
        try:
            # try to get requested attribute from self (the node)
            return orgin(self, name)
        except AttributeError, e:
            # try to find requested attribute on behavior
            classes = getattr(node_cls, _CLS_ATTR)
            for cls in classes:
                unbound = getattr(cls, name, _default_marker)
                if unbound is _default_marker:
                    continue
                behavior = self._behavior_instances[cls.__name__]
                return getattr(behavior, name)
            raise AttributeError(name)
    node_cls.__getattribute__ = _wrapfunc(node_cls.__getattribute__,
                                          __getattribute__)
