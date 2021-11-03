from contextlib import contextmanager
from node.behaviors import Nodify
from node.interfaces import IAttributes
from node.interfaces import INodeAttributes
from node.interfaces import ISchema
from node.interfaces import ISchemaAsAttributes
from node.utils import AttributeAccess
from node.schema import _undefined
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import plumb
from plumber import plumbing
from zope.interface import implementer


@contextmanager
def scope_field(field, name, parent):
    field.set_scope(name, parent)
    try:
        yield field
    finally:
        field.reset_scope()


@implementer(ISchema)
class Schema(Behavior):
    schema = default(dict())

    @plumb
    def __getitem__(next_, self, name):
        field = self.schema.get(name, self.schema.get('*'))
        if not field:
            return next_(self, name)
        with scope_field(field, name, self):
            try:
                return field.deserialize(next_(self, name))
            except KeyError as e:
                if field.default is not _undefined:
                    return field.default
                raise e

    @plumb
    def __setitem__(next_, self, name, value):
        field = self.schema.get(name, self.schema.get('*'))
        if not field:
            next_(self, name, value)
            return
        with scope_field(field, name, self):
            if not field.validate(value):
                raise ValueError(u'{} is no {}'.format(value, field.type_))
            next_(self, name, field.serialize(value))


@plumbing(Nodify, Schema)
@implementer(INodeAttributes)
class SchemaAttributes(object):

    def __init__(self, name=None, parent=None):
        self.__name__ = name
        self.__parent__ = parent
        self.schema = parent.schema

    def __setitem__(self, name, value):
        if name not in self.schema:
            raise KeyError(name)
        self.parent.storage[name] = value

    def __getitem__(self, name):
        if name not in self.schema:
            raise KeyError(name)
        return self.parent.storage[name]

    def __delitem__(self, name):
        if name not in self.schema:
            raise KeyError(name)
        del self.parent.storage[name]

    def __iter__(self):
        return iter(self.schema)


@implementer(IAttributes, ISchemaAsAttributes)
class SchemaAsAttributes(Behavior):
    schema = default(dict())
    attributes_factory = default(SchemaAttributes)
    attribute_access_for_attrs = default(False)

    @finalize
    @property
    def attrs(self):
        attrs = self.attributes_factory(name='__attrs__', parent=self)
        if self.attribute_access_for_attrs:
            attrs = AttributeAccess(attrs)
        return attrs

    @plumb
    def __setitem__(next_, self, name, value):
        if name in self.schema:
            raise KeyError('{} contained in schema. Use ``attrs``'.format(name))
        next_(self, name, value)

    @plumb
    def __getitem__(next_, self, name):
        if name in self.schema:
            raise KeyError('{} contained in schema. Use ``attrs``'.format(name))
        return next_(self, name)

    @plumb
    def __delitem__(next_, self, name):
        if name in self.schema:
            raise KeyError('{} contained in schema. Use ``attrs``'.format(name))
        next_(self, name)

    @plumb
    def __iter__(next_, self):
        schema = self.schema
        for name in next_(self):
            if name in schema:
                continue
            yield name
