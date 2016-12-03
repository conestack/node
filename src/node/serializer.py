from node.interfaces import IAttributes
from node.interfaces import INode
from node.utils import UNSET
from odict import odict
from zope.interface import Interface
import json


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
# encoding
###############################################################################

class NodeEncoder(json.JSONEncoder):

    def dotted_name(self, ob):
        """Return dotted name of object.
        """
        return '.'.join([ob.__module__, ob.__class__.__name__])

    def default(self, ob):
        # serialize UNSET
        if ob is UNSET:
            return {'__node_serializer__': 'node.utils.UNSET'}
        # delegate encoding to super class
        if not INode.providedBy(ob):
            return json.JSONEncoder.default(self, ob)
        # serialize node
        ret = dict()
        data = ret.setdefault('__node_serializer__', dict())
        data['__class__'] = self.dotted_name(ob)
        data['__name__'] = ob.name
        for cls, callback in serializer.registry.items():
            if issubclass(cls, Interface) and cls.providedBy(ob):
                callback(self, ob, data)
            elif isinstance(ob, cls):
                callback(self, ob, data)
        return ret


###############################################################################
# decoding
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
        factory = self.resolve(data['__class__'])
        kw = self.decode(data.get('__kw__', dict()))
        name = data['__name__']
        if parent is not None:
            node = parent[name] = factory(**kw)
        else:
            node = factory(**kw)
            node.__name__ = name
        return node

    def decode(self, dct, parent=None):
        # return as is if not serialized by ``NodeEncoder``
        if not '__node_serializer__' in dct:
            return dct
        data = dct['__node_serializer__']
        # string value mapping to a function, class, module or singleton
        if isinstance(data, basestring):
            return self.resolve(data)
        # deserialize node
        ob = self.node_factory(data, parent=parent)
        for cls, callback in deserializer.registry.items():
            if issubclass(cls, Interface) and cls.providedBy(ob):
                callback(self, ob, data)
            elif isinstance(ob, cls):
                callback(self, ob, data)
        return ob


###############################################################################
# API
###############################################################################

def serialize(ob):
    """Serialize ob.

    Return JSON dump.
    """
    return json.dumps(ob, cls=NodeEncoder)


def deserialize(json_data, root=None):
    """Deserialize JSON dump.

    Return deserialized data.
    """
    data = json.loads(json_data)
    return NodeDecoder().decode(data, parent=root)


###############################################################################
# node serializer and deserializer
###############################################################################

@serializer(INode)
def serialize_node(encoder, node, data):
    children = list()
    for child in node.values():
        children.append(encoder.default(child))
    if children:
        data['__children__'] = children


@deserializer(INode)
def deserialize_node(decoder, node, data):
    children = data.get('__children__')
    if not children:
        return
    for child in children:
        decoder.decode(child, parent=node)


###############################################################################
# attributes serializer and deserializer
###############################################################################

@serializer(IAttributes)
def serialize_node_attributes(encoder, node, data):
    pass


@deserializer(IAttributes)
def deserialize_node_attributes(decoder, node, data):
    pass
