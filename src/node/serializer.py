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

    def dottedname(self, ob):
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
        data['__class__'] = self.dottedname(ob)
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

    def __init__(self, parent=None):
        self.parent = parent

    def resolve(self, name):
        """Resolve dotted name to object.
        """
        components = name.split('.')
        ob = __import__(components[0])
        for comp in components[1:]:
            ob = getattr(ob, comp)
        return ob

    def instanciate_node(self, data):
        """Instanciate node by definitions from data.
        """
        factory = self.resolve(data['__class__'])
        kw = self(data.get('__kw__', dict()))
        name = data['__name__']
        parent = self.parent
        if parent is not None:
            node = parent[name] = factory(**kw)
        else:
            node = factory(**kw)
            node.__name__ = name
        return node

    def __call__(self, dct):
        # return as is if not serialized by ``NodeEncoder``
        if not '__node_serializer__' in dct:
            return dct
        data = dct['__node_serializer__']
        # a string value directly maps to a function, class, module or singleton
        if isinstance(data, basestring):
            return self.resolve(data)
        # deserialize node
        ob = self.instanciate_node(data)
        for cls, callback in serializer.registry.items():
            if issubclass(cls, Interface) and cls.providedBy(ob):
                callback(self, ob, data)
            elif isinstance(ob, cls):
                callback(self, ob, data)
        return ob


###############################################################################
# serializer and deserializer callbacks
###############################################################################

@serializer(INode)
def serialize_node(encoder, node, data):
    pass


@deserializer(INode)
def deserialize_node(decoder, parent, data):
    pass


@serializer(IAttributes)
def serialize_node_attributes(encoder, node, data):
    pass


@deserializer(IAttributes)
def deserialize_node_attributes(decoder, parent, data):
    pass
