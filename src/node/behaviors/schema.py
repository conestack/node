from node.behaviors import Nodify
from node.interfaces import IAttributes
from node.interfaces import INodeAttributes
from node.interfaces import ISchema
from node.interfaces import ISchemaAsAttributes
from node.interfaces import ISchemaProperties
from node.schema import Field
from node.schema import scope_field
from node.utils import AttributeAccess
from node.utils import UNSET
from plumber import Behavior
from plumber import default
from plumber import finalize
from plumber import plumb
from plumber import plumber
from plumber import plumbing
from zope.interface import implementer


@implementer(ISchema)
class Schema(Behavior):
    schema = default(dict())

    @plumb
    def __getitem__(next_, self, name):
        field = self.schema.get(name)
        if not field:
            return next_(self, name)
        with scope_field(field, name, self):
            try:
                return field.deserialize(next_(self, name))
            except KeyError as e:
                return field.default

    @plumb
    def __setitem__(next_, self, name, value):
        field = self.schema.get(name)
        if not field:
            next_(self, name, value)
            return
        if value is UNSET:
            del self[name]
            return
        with scope_field(field, name, self):
            field.validate(value)
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


@plumber.metaclasshook
def schema_properties_metclass_hook(cls, name, bases, dct):
    """Plumber metaclass hook handling proper post initialization of
    ``SchemaProperty`` instances on plumbing classes.
    """
    if not ISchemaProperties.implementedBy(cls):
        return
    for key, val in dct.items():
        if isinstance(val, Field):
            setattr(cls, key, SchemaProperty(key, val))


class SchemaProperty(object):
    """Descriptor object for schema properties.

    If a class gets plumbed with ``node.behaviors.SchemaProperties`` behavior,
    all class members holding a ``node.schema.Field`` instance get replaced by
    a ``SchemaProperty``.

    This descriptor used field validation and serialization for accessing
    and writing to the related object.

    The related object must be a mapping type and at least implement
    ``__getitem__``, ``__setitem__`` and ``__delitem__``.
    """

    def __init__(self, name, field):
        """Create schema property instance.

        :param name: The property name.
        :param field: The related ``node.schema.Field`` instance.
        """
        self.name = name
        self.field = field

    def __get__(self, obj, type_=None):
        """Get field value.

        :param obj: The related object.
        :param type_: The related object type. Not used.
        :return: If property gets accessed on class directly, field default
        value is returned. Otherwise read raw value from related object and
        return deserialized value. If related object not holds a value by
        field name, default value gets returned.
        """
        field = self.field
        if obj is None:
            return field.default
        name = self.name
        with scope_field(field, name, obj):
            try:
                return field.deserialize(obj[name])
            except KeyError as e:
                return field.default

    def __set__(self, obj, value):
        """Set field value.

        :param obj: The related object.
        :param value: The field value to set. If value is ``UNSET``, it gets
        deleted from related object. Otherwise validate given value and
        serialize it on related object.
        """
        if value is UNSET:
            del obj[self.name]
            return
        name = self.name
        field = self.field
        with scope_field(field, name, self):
            field.validate(value)
            obj[name] = field.serialize(value)

    def __delete__(self, obj):
        """Delete field value from related object.

        :param obj: The related object.
        """
        del obj[self.name]


@implementer(ISchemaProperties)
class SchemaProperties(Behavior):
    """Plumbing behavior to provide schema fields as class properties.

    If a class gets plumbed with this behavior, all members which are an
    instance of ``node.schema.Field`` get replaced by a
    ``node.behaviors.SchemaProperty`` instance, which provides access to this
    object's data while taking validation and serialization into account.

    A class using this behavior must be a mapping type and at least implement
    ``__getitem__``, ``__setitem__`` and ``__delitem__``.

    Example usage:

    .. code-block:: python

        from node import schema
        from node.behaviors import SchemaProperties
        from node.utils import UNSET
        from plumber import plumbing

        @plumbing(SchemaProperties)
        class ObjectWithSchemaProperties(dict):
            title = schema.Str(default=u'No Title')
            description = schema.Str()

        obj = ObjectWithSchemaProperties()

        # values not set yet, defaults are returned.
        assert(obj.title == u'No Title')
        assert(obj.description is UNSET)
        assert(list(obj.keys()) == [])

        # when setting values, the get set on the mapping.
        obj.title = u'Title'
        obj.description = u'Description'
        assert(obj['title'] == u'Title')
        assert(obj['description'] == u'Description')

        # when setting values with UNSET, value gets deleted from mapping.
        obj.description = UNSET
        assert('description' not in obj)
    """
