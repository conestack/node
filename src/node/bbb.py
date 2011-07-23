import uuid
import inspect
from odict import odict
from odict.pyodict import _nil
from zope.interface import implements
from zope.interface.common.mapping import (
    IReadMapping,
    IFullMapping)
from zope.deprecation import deprecated
try:
    from zope.component.event import objectEventNotify
except ImportError, e:
    from zope.app.event.objectevent import objectEventNotify # BBB
from interfaces import (
    INode,
    INodeAttributes,
    IAttributedNode,
    ILifecycleNode)
from events import (
    NodeCreatedEvent,
    NodeAddedEvent,
    NodeRemovedEvent,
    NodeModifiedEvent,
    NodeDetachedEvent)
from utils import (
    Zodict,
    AttributeAccess,
    LocationIterator)


###############################################################################
# original from zodict
###############################################################################

class NodeIndex(object):
    implements(IReadMapping)

    def __init__(self, index):
        self._index = index

    def __getitem__(self, key):
        return self._index[int(key)]

    def get(self, key, default=None):
        return self._index.get(int(key), default)

    def __contains__(self, key):
        return int(key) in self._index


class _Node(object):
    """Abstract node implementation. Subclass must mixin ``_node_impl()``.

    A node implemententation must provide:
        __getitem__
        __setitem__
        __delitem__
        __iter__
    """
    implements(INode)
    allow_non_node_childs = False
    
    def _node_impl(self):
        return None

    def __init__(self, name=None, index=True):
        """
        XXX: switch ``index`` to False by default in 2.1
        
        ``name``
            optional name used for ``__name__`` declared by ``ILocation``.
        ``index``
            flag wether node index is enabled or not.
        """
        # XXX: this looks to me like we are calling the node_impl's
        # super-class' __init__ and not node_impl's __init__. Is this what we
        # want?
        # XXX: feels hackish, should be split into a abstract node and one that
        # expects an implementation like here. Corresponding test in node.txt
        # very beginning should then be enabled again
        if self._node_impl() is not None:
            super(self._node_impl(), self).__init__()
        self.__parent__ = None
        self.__name__ = name
        self._adopting = True
        if index:
            self._index = dict()
            self._uuid = None
            self.uuid = uuid.uuid4()
        else:
            self._index = None
        self.aliaser = None
        self._nodespaces = None

    # a storage and general way to access our nodespaces
    # an AttributedNode uses this to store the attrs nodespace
    @property
    def nodespaces(self):
        if self._nodespaces is None:
            self._nodespaces = odict()
            self._nodespaces['__children__'] = self
        return self._nodespaces

    def __contains__(self, key):
        """uses __getitem__
        """
        try:
            self[key]
        except KeyError:
            return False
        return True
    
    def get(self, key, default=None):
        """uses __getitem__
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            return self.nodespaces[key]
        try:
            return self._node_impl().__getitem__(self, key)
        except KeyError:
            raise KeyError(key)

    def _adopt(self, key, val):
        """Adopting happens eg during ``__setitem__``.
        """
        # remember val __name__ and __parent__ for reverting
        old__name__ = val.__name__
        old__parent__ = val.__parent__
        # immediately set __name__ and __parent__ on val, implementation often
        # require hierarchy information to acquire keys
        val.__name__ = key
        val.__parent__ = self
        has_children = False
        # XXX: maybe skip this check and just use self._index for condition in
        #      next code block. then remembering origin __name__ and __parent__
        #      gets obsolete
        if self._index is not None:
            # XXX: this iterkeys was a problem with the current LDAPNode's
            # __setitem__. As we don't have indexing on them we circumvented
            # the problem.
            for valkey in val.iterkeys():
                has_children = True
                break
            if has_children:
                keys = set(self._index.keys())
                if keys.intersection(val._index.keys()):
                    val.__name__ = old__name__
                    val.__parent__ = old__parent__
                    raise ValueError, u"Node with uuid already exists"
            self._index.update(val._index)
            val._index = self._index

    def __setitem__(self, key, val):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            if isinstance(val, _Node):
                val.__name__ = key
                val.__parent__ = self
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            self.nodespaces[key] = val
            # index checks below must not happen for other nodespace.
            return
        if not self.allow_non_node_childs and inspect.isclass(val):
            raise ValueError, u"It isn't allowed to use classes as values."
        if isinstance(val, _Node):
            if self._adopting:
                self._adopt(key, val)
        else:
            if not self.allow_non_node_childs:
                raise ValueError("Non-node childs are not allowed.")
        self._node_impl().__setitem__(self, key, val)

    def __delitem__(self, key):
        # blend in our nodespaces as children, with name __<name>__
        if key.startswith('__') and key.endswith('__'):
            # a reserved child key mapped to the nodespace behind
            # nodespaces[key], nodespaces is an odict
            del self.nodespaces[key]
            return
        # fail immediately if key does not exist
        self[key]
        if self._index is not None:
            for iuuid in self[key]._to_delete():
                del self._index[iuuid]
        self._node_impl().__delitem__(self, key)

# XXX: If these are undesired here, because they override the ones of a
# node_impl, we need to move them to some other class. It is convenient to
# have them here in order to create full-blown nodes by subclassing _Node and
# providing __delitem__, __getitem__, __iter__, __setitem__.

    def iteritems(self):
        for key in self:
            yield key, self[key]

    def iterkeys(self):
        return self.__iter__()

    def itervalues(self):
        for key in self:
            yield self[key]

    def items(self):
        return [x for x in self.iteritems()]

    def keys(self):
        return [x for x in self]

    def __len__(self):
        # XXX: could also be an idea:
        #try:
        #    return self._node_impl().__len__()
        #except AttributeError:
        #    return len(self.keys())
        return len(self.keys())

    def values(self):
        return [x for x in self.itervalues()]
    
    def _to_delete(self):
        todel = [int(self.uuid)]
        for childkey in self:
            try:
                todel += self[childkey]._to_delete()
            except AttributeError:
                # Non-Node values are not told about deletion
                continue
        return todel

    def _get_uuid(self):
        return self._uuid

    def _set_uuid(self, uuid):
        iuuid = uuid is not None and int(uuid) or None
        if self._index is not None \
          and iuuid in self._index \
          and self._index[iuuid] is not self:
            raise ValueError, u"Given uuid was already used for another Node"
        siuuid = self._uuid is not None and int(self._uuid) or None
        if self._index is not None and siuuid in self._index:
            del self._index[siuuid]
        if self._index is not None:
            self._index[iuuid] = self
        self._uuid = uuid

    uuid = property(_get_uuid, _set_uuid)

    @property
    def path(self):
        path = list()
        for parent in LocationIterator(self):
            path.append(parent.__name__)
        path.reverse()
        return path

    @property
    def root(self):
        root = None
        for parent in LocationIterator(self):
            root = parent
        return root

    @property
    def index(self):
        if self._index is None:
            raise AttributeError(u"No index support configured on this Node.")
        return NodeIndex(self._index)

    def node(self, uuid):
        if self._index is None:
            raise ValueError(u"No index support configured on this Node.")
        return self._index.get(int(uuid))

    def filtereditems(self, interface):
        # XXX: inconsistent naming, this should be filtereditervalues()
        for node in self.values():
            if interface.providedBy(node):
                yield node

    def _validateinsertion(self, newnode, refnode):
        nodekey = newnode.__name__
        if nodekey is None:
            raise ValueError, u"Given node has no __name__ set."
        if self.node(newnode.uuid) is not None:
            raise KeyError, u"Given node already contained in tree."
        index = self._nodeindex(refnode)
        if index is None:
            raise ValueError, u"Given reference node not child of self."

    def _nodeindex(self, node):
        index = 0
        for key in self.keys():
            if key == node.__name__:
                return index
            index += 1
        return None

    def insertbefore(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        prevnode = None
        prevkey = None
        if index > 0:
            prevkey = self.keys()[index - 1]
            prevnode = dict.__getitem__(self, prevkey)
        if prevnode is not None:
            dict.__getitem__(self, prevkey)[2] = nodekey
            newnode = [prevkey, newnode, refkey]
        else:
            self.lh = nodekey
            newnode = [_nil, newnode, refkey]
        dict.__getitem__(self, refkey)[0] = nodekey
        dict.__setitem__(self, nodekey, newnode)
        self[nodekey] = newnode[1]

    def insertafter(self, newnode, refnode):
        self._validateinsertion(newnode, refnode)
        nodekey = newnode.__name__
        refkey = refnode.__name__
        index = self._nodeindex(refnode)
        nextnode = None
        nextkey = None
        keys = self.keys()
        if index < len(keys) - 1:
            nextkey = self.keys()[index + 1]
            nextnode = dict.__getitem__(self, nextkey)
        if nextnode is not None:
            dict.__getitem__(self, nextkey)[0] = nodekey
            newnode = [refkey, newnode, nextkey]
        else:
            self.lt = nodekey
            newnode = [refkey, newnode, _nil]
        dict.__getitem__(self, refkey)[2] = nodekey
        dict.__setitem__(self, nodekey, newnode)
        self[nodekey] = newnode[1]

    # orderable related
    def _index_nodes(self):
        for node in self.values():
            try:
                uuid = int(node.uuid)
            except AttributeError:
                # non-Node values are a dead end, no magic for them
                continue
            self._index[uuid] = node
            node._index = self._index
            node._index_nodes()

    def detach(self, key):
        node = self[key]
        del self[key]
        if self._index is not None:
            node._index = { int(node.uuid): node }
            node._index_nodes()
        return node
    
    def as_attribute_access(self):
        return AttributeAccess(self)

    @property
    def noderepr(self):
        # XXX: why do we have noderepr and __repr__?
        name = unicode(self.__name__).encode('ascii', 'replace')
        return str(self.__class__) + ': ' + name[name.find(':') + 1:]

    def printtree(self, indent=0):
        print "%s%s" % (indent * ' ', self.noderepr)
        for node in self.values():
            try:
                node.printtree(indent+2)
            except AttributeError:
                # Non-Node values are just printed
                print "%s%s" % (indent * ' ', node)

    def __repr__(self):
        # XXX: This is mainly used in doctest, I think
        # doctest fails if we output utf-8
        name = unicode(self.__name__).encode('ascii', 'replace')
        return "<%s object '%s' at %s>" % (self.__class__.__name__,
                                           name,
                                           hex(id(self))[:-1])

    __str__ = __repr__


class Node(_Node, Zodict):
    """Inherit from _Node and mixin Zodict.
    """
    def _node_impl(self):
        return Zodict

deprecated('Node',
           "'index' kwarg of ``__init__`` will be changed to False by default "
           "in 2.1")


class NodeAttributes(Node):
    """Semantic object.
    """
    allow_non_node_childs = True

    def __init__(self, node):
        Node.__init__(self, index=False)
        self._node = node


class AttributedNode(Node):
    """A node that has another nodespace behind self.attrs[]
    """
    implements(IAttributedNode)

    attributes_factory = NodeAttributes
    attribute_aliases = None

    def __init__(self, name=None, index=True):
        super(AttributedNode, self).__init__(name, index=index)
        # XXX: Currently attributes_acces_for_attrs is default, this might
        # change, as the dict api to attrs is broken by it.
        self.attribute_access_for_attrs = True

    # Another nodespace access via the .attrs attribute
    @property
    def attrs(self):
        try:
            attrs = self.nodespaces['__attrs__']
        except KeyError:
            attrs = self.nodespaces['__attrs__'] = self.attributes_factory(self)
            attrs.__name__ = '__attrs__'
            attrs.__parent__ = self
        if self.attribute_access_for_attrs:
            return AttributeAccess(attrs)
        return attrs

    # BBB
    attributes = attrs

deprecated('AttributedNode',
           "'attribute_access_for_attrs' flag will be changed to False by "
           "default in 2.1")


class LifecycleNodeAttributes(NodeAttributes):
    """XXX If we merge this into node, do we really need the event on the node?
    a) LifecycleNode current would trigger event on the attrs node
    b) we use to trigger only on the node not on us, shall we suppress us and
       trigger on node instead (imagine we are an LifecycleNode configured to be
       used for the attrs nodespace
    c) we raise an event on us (the attrs nodespace) and on our parent node, that
       keeps us in .attrs
    """

    def __setitem__(self, key, val):
        NodeAttributes.__setitem__(self, key, val)
        if self._node._notify_suppress:
            return
        objectEventNotify(self._node.events['modified'](self._node))

    def __delitem__(self, key):
        NodeAttributes.__delitem__(self, key)
        if self._node._notify_suppress:
            return
        objectEventNotify(self._node.events['modified'](self._node))


class LifecycleNode(AttributedNode):
    implements(ILifecycleNode)

    events = {
        'created': NodeCreatedEvent,
        'added': NodeAddedEvent,
        'modified': NodeModifiedEvent,
        'removed': NodeRemovedEvent,
        'detached': NodeDetachedEvent,
    }

    attributes_factory = LifecycleNodeAttributes

    def __init__(self, name=None, index=True):
        super(LifecycleNode, self).__init__(name=name, index=index)
        self._notify_suppress = False
        objectEventNotify(self.events['created'](self))

    def __setitem__(self, key, val):
        super(LifecycleNode, self).__setitem__(key, val)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['added'](val, newParent=self,
                                               newName=key))

    def __delitem__(self, key):
        delnode = self[key]
        super(LifecycleNode, self).__delitem__(key)
        if self._notify_suppress:
            return
        objectEventNotify(self.events['removed'](delnode, oldParent=self,
                                                 oldName=key))

    def detach(self, key):
        notify_before = self._notify_suppress
        self._notify_suppress = True
        node = super(LifecycleNode, self).detach(key)
        # XXX: looks like bug, notify_before, however, I do not understand why
        # we enforce notify_suppress before calling super
        self._notify_suppress = False
        objectEventNotify(self.events['detached'](node, oldParent=self,
                                                  oldName=key))
        return node


# XXX: WIP
class FilteredNodespace(object):
    def filterediter(self, flter=None):
        """Apply filter

        flter can be:
        - interface that children need to provide
        - dict 
        - ...

        XXX: use backend support if available, i.e. query keys from backend and
        return only those

        XXX: feels like a backend issue
        """