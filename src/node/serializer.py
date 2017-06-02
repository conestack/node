# -*- coding: utf-8 -*-
from inspect import isclass
from inspect import isfunction
from inspect import ismethod
from node.compat import IS_PY2
from node.compat import STR_TYPE
from node.interfaces import IAttributes
from node.interfaces import INode
from node.utils import UNSET
from odict import odict
from zope.interface import Interface
import json
import uuid


###############################################################################
# API
###############################################################################

def serialize(ob, simple_mode=False, include_class=False):
    """Serialize ob.

    Return JSON dump.
    """
    if simple_mode:
        def encoder_factory(**kw):
            kw['simple_mode'] = True
            kw['include_class'] = include_class
            return NodeEncoder(**kw)
    else:
        encoder_factory = NodeEncoder
    return json.dumps(ob, cls=encoder_factory)


def deserialize(json_data, root=None):
    """Deserialize JSON dump.

    Return deserialized data.
    """
    data = json.loads(json_data)
    return NodeDecoder().decode(data, parent=root)


###############################################################################
# serializer registry
###############################################################################

class _serializer_registry(object):
    """Serializer registry decorator base class.
    """
    # must be set on subclass
    registry = None

    def __init__(self, ob):
        self.ob = ob

    def __call__(self, ob):
        self.registry[self.ob] = ob
        return ob


class serializer(_serializer_registry):
    """Serializer registry decorator.
    """
    registry = odict()


class deserializer(_serializer_registry):
    """Deserializer registry decorator.
    """
    registry = odict()


###############################################################################
# encoder
###############################################################################

class NodeEncoder(json.JSONEncoder):
    # flag whether to serialize without type information
    simple_mode = False
    # include class has no effect in non simple mode
    include_class = True

    def __init__(self, **kw):
        if 'simple_mode' in kw:
            self.simple_mode = kw.pop('simple_mode')
        if 'include_class' in kw:
            self.include_class = kw.pop('include_class')
        super(NodeEncoder, self).__init__(**kw)

    def dotted_name(self, ob):
        """Return dotted name of object.
        """
        if isclass(ob) or isfunction(ob):
            return '.'.join(
                [ob.__module__, ob.__name__ if IS_PY2 else ob.__qualname__]
            )
        elif ismethod(ob):
            # this block is not reached in python 3, ignore missing coverage
            return '.'.join(
                [ob.im_class.__module__, ob.im_class.__name__, ob.__name__]
            )
        else:
            return '.'.join([ob.__module__, ob.__class__.__name__])

    def default(self, ob):
        # serialize UNSET
        if ob is UNSET:
            return '<UNSET>'
        # serialize UUID
        if isinstance(ob, uuid.UUID):
            return '<UUID>:{}'.format(ob)
        # serialize Node
        if INode.providedBy(ob):
            ret = dict()
            if self.simple_mode:
                data = ret
            else:
                data = ret.setdefault('__node__', dict())
            if not self.simple_mode or self.include_class:
                data['class'] = self.dotted_name(ob)
            data['name'] = ob.name
            for cls, callback in serializer.registry.items():
                if issubclass(cls, Interface) and cls.providedBy(ob):
                    callback(self, ob, data)
                elif isinstance(ob, cls):
                    callback(self, ob, data)
            return ret
        # Serialize class, method or function
        if isclass(ob) or ismethod(ob) or isfunction(ob):
            if self.simple_mode:
                return self.dotted_name(ob)
            return {'__ob__': self.dotted_name(ob)}
        # no custom serialization required
        return ob


###############################################################################
# decoder
###############################################################################

class NodeDecoder(object):

    def resolve(self, name):
        """Resolve dotted name to object.
        """
        components = name.split('.')
        ob = __import__(components[0])
        for comp in components[1:]:
            ob = getattr(ob, comp)
        return ob

    def node_factory(self, data, parent=None):
        """Instanciate node by definitions from ``data``. New node gets set as
        child on ``parent`` if given.
        """
        factory = self.resolve(data['class'])
        kw = self.decode(data.get('kw', dict()))
        name = data['name']
        if parent is not None:
            node = parent[name] = factory(**kw)
        else:
            node = factory(**kw)
            node.__name__ = name
        return node

    def decode(self, data, parent=None):
        # decode data from string
        if isinstance(data, STR_TYPE):
            # decode UNSET
            if data == '<UNSET>':
                return UNSET
            # decode UUID
            if data.startswith('<UUID>:'):
                return uuid.UUID(data[7:])
            return data
        # decode data from list
        if isinstance(data, list):
            return [self.decode(it, parent=parent) for it in data]
        # return data as is if no dict
        if not isinstance(data, dict):
            return data
        # decode class, method or function
        if '__ob__' in data:
            return self.resolve(data['__ob__'])
        # decode node
        if '__node__' in data:
            node_data = data['__node__']
            node = self.node_factory(node_data, parent=parent)
            for cls, callback in deserializer.registry.items():
                if issubclass(cls, Interface) and cls.providedBy(node):
                    callback(self, node, node_data)
                elif isinstance(node, cls):
                    callback(self, node, node_data)
            return node
        # no custom deserialization required
        return data


###############################################################################
# node serializer and deserializer
###############################################################################

@serializer(INode)
def serialize_node(encoder, node, data):
    children = list()
    for child in node.values():
        children.append(encoder.default(child))
    if children:
        data['children'] = children


@deserializer(INode)
def deserialize_node(decoder, node, data):
    children = data.get('children')
    if not children:
        return
    for child in children:
        decoder.decode(child, parent=node)


###############################################################################
# attributes serializer and deserializer
###############################################################################

@serializer(IAttributes)
def serialize_node_attributes(encoder, node, data):
    attrs = data.setdefault('attrs', dict())
    for name, child in node.attrs.items():
        attrs[name] = encoder.default(child)


@deserializer(IAttributes)
def deserialize_node_attributes(decoder, node, data):
    attrs = data.get('attrs')
    if not attrs:
        return
    for attr, value in attrs.items():
        node.attrs[attr] = decoder.decode(value)
