from contextlib import contextmanager
from node import compat
from node.utils import UNSET
from odict import odict
try:
    from urllib import quote
    from urllib import unquote
except ImportError:
    from urllib.parse import quote
    from urllib.parse import unquote
import base64
import json
import pickle
import uuid


@contextmanager
def scope_context(context, name, parent):
    """Context manager for setting scope on context.

    Useful if ``Field`` or ``FieldSerializer`` implementations want to gather
    information from related model.

    :param context: ``ScopeContext`` instance.
    :param name: The field name in this scope.
    :param parent: The field containing model for this scope.
    """
    context.name = name
    context.parent = parent
    try:
        yield context
    finally:
        context.name = context.parent = None


class ScopeContext(object):
    """A scoped context.
    """

    name = None
    """Name of the field while scoped."""

    parent = None
    """The field containing model while scoped."""


class Field(ScopeContext):
    """A schema field."""

    def __init__(self, type_, default=UNSET, serializer=UNSET):
        """Create schema field.

        :param type_: Type of the field value.
        :param default: Default value of the field. Optional.
        :param serializer: ``FieldSerializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        self.type_ = type_
        self.default = default
        self.serializer = serializer

    def serialize(self, value):
        """Serialize value.

        :param value: The value to serialize.
        :return: The serialized value.
        """
        serializer = self.serializer
        if serializer is not UNSET:
            with scope_context(serializer, self.name, self.parent):
                return serializer.dump(value)
        return value

    def deserialize(self, value):
        """Deserialize value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """
        serializer = self.serializer
        if serializer is not UNSET:
            with scope_context(serializer, self.name, self.parent):
                return serializer.load(value)
        return value

    def validate(self, value):
        """Validate value.

        :param value: The value to validate.
        :raises Exception: If validation fails.
        """
        if not isinstance(value, self.type_):
            raise ValueError(u'{} is no {} type'.format(value, self.type_))


class IterableField(Field):
    """An iterable schema field."""

    def __init__(
        self,
        type_,
        default=UNSET,
        serializer=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create iterable schema field.

        :param type_: Type of the field value.
        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(IterableField, self).__init__(
            type_,
            default=default,
            serializer=serializer
        )
        self.value_type = value_type
        self.size = size

    def serialize(self, value):
        """Serialize value.

        :param value: The value to serialize.
        :return: The serialized value.
        """
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_context(value_type, self.name, self.parent):
                value = self.type_(
                    [value_type.serialize(item) for item in value]
                )
        return super(IterableField, self).serialize(value)

    def deserialize(self, value):
        """Deserialize value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """
        value = super(IterableField, self).deserialize(value)
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_context(value_type, self.name, self.parent):
                value = [value_type.deserialize(item) for item in value]
        return self.type_(value)

    def validate(self, value):
        """Validate value.

        :param value: The value to validate.
        :raises Exception: If validation fails.
        """
        super(IterableField, self).validate(value)
        if self.size is not UNSET and len(value) != self.size:
            raise ValueError(u'{} has invalid size {} != {}'.format(
                value,
                len(value),
                self.size
            ))
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_context(value_type, self.name, self.parent):
                for item in value:
                    value_type.validate(item)


class Bool(Field):

    def __init__(self, default=UNSET, serializer=UNSET):
        """Create bool schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(Bool, self).__init__(
            type_=bool,
            default=default,
            serializer=serializer
        )


class Int(Field):

    def __init__(self, default=UNSET, serializer=UNSET):
        """Create int field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(Int, self).__init__(
            type_=int,
            default=default,
            serializer=serializer
        )


class Float(Field):

    def __init__(self, default=UNSET, serializer=UNSET):
        """Create float schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(Float, self).__init__(
            type_=float,
            default=default,
            serializer=serializer
        )


class Bytes(Field):

    def __init__(self, default=UNSET, serializer=UNSET):
        """Create bytes schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(Bytes, self).__init__(
            type_=bytes,
            default=default,
            serializer=serializer
        )


class Str(Field):

    def __init__(self, default=UNSET, serializer=UNSET):
        """Create str schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(Str, self).__init__(
            type_=compat.UNICODE_TYPE,
            default=default,
            serializer=serializer
        )


class UUID(Field):

    def __init__(self, default=UNSET, serializer=UNSET):
        """Create UUID schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(UUID, self).__init__(
            type_=uuid.UUID,
            default=default,
            serializer=serializer
        )


class Tuple(IterableField):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create tuple schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(Tuple, self).__init__(
            type_=tuple,
            default=default,
            serializer=serializer,
            value_type=value_type,
            size=size
        )


class List(IterableField):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create list schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(List, self).__init__(
            type_=list,
            default=default,
            serializer=serializer,
            value_type=value_type,
            size=size
        )


class Set(IterableField):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create set schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(Set, self).__init__(
            type_=set,
            default=default,
            serializer=serializer,
            value_type=value_type,
            size=size
        )


class Dict(Field):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        key_type=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create dict schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param key_type: ``Field`` instance defining the key type of the
        iterable. Optional.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(Dict, self).__init__(
            type_=dict,
            default=default,
            serializer=serializer
        )
        self.key_type = key_type
        self.value_type = value_type
        self.size = size

    def serialize(self, value):
        """Serialize value.

        :param value: The value to serialize.
        :return: The serialized value.
        """
        key_type = self.key_type
        if key_type is not UNSET:
            with scope_context(key_type, self.name, self.parent):
                new_value = self.type_()
                for key, val in value.items():
                    new_value[key_type.serialize(key)] = val
                value = new_value
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_context(value_type, self.name, self.parent):
                for key, val in value.items():
                    value[key] = value_type.serialize(val)
        return super(Dict, self).serialize(value)

    def deserialize(self, value):
        """Deserialize value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """
        value = super(Dict, self).deserialize(value)
        key_type = self.key_type
        if key_type is not UNSET:
            with scope_context(key_type, self.name, self.parent):
                new_value = self.type_()
                for key, val in value.items():
                    new_value[key_type.deserialize(key)] = val
                value = new_value
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_context(value_type, self.name, self.parent):
                for key, val in value.items():
                    value[key] = value_type.deserialize(val)
        return value

    def validate(self, value):
        """Validate value.

        :param value: The value to validate.
        :raises Exception: If validation fails.
        """
        super(Dict, self).validate(value)
        if self.size is not UNSET and len(value) != self.size:
            raise ValueError(u'{} has invalid size {} != {}'.format(
                value,
                len(value),
                self.size
            ))
        key_type = self.key_type
        if key_type is not UNSET:
            with scope_context(key_type, self.name, self.parent):
                for key in value:
                    key_type.validate(key)
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_context(value_type, self.name, self.parent):
                for val in value.values():
                    value_type.validate(val)


class ODict(Dict):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        key_type=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create ordered dict schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param key_type: ``Field`` instance defining the key type of the
        iterable. Optional.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(ODict, self).__init__(
            default=default,
            serializer=serializer,
            key_type=key_type,
            value_type=value_type,
            size=size
        )
        self.type_=odict


class Node(Field):

    def __init__(self, type_, serializer=UNSET):
        """Create node schema field.

        :param type_: Type of the field value.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(Node, self).__init__(type_=type_, serializer=serializer)

    def deserialize(self, value):
        """Deserialize node from value.

        The ``load`` callable respective the ``type_`` gets passed ``name``
        and ``parent`` as keyword arguments.

        :param value: The value to deserialize.
        :return: The deserialized node.
        """
        if isinstance(value, self.type_):
            return value
        elif self.serializer is not UNSET:
            # XXX: hook to parent?
            return self.serializer.load(value, name=self.name, parent=self.parent)
        else:
            # XXX: hook to parent?
            return self.type_(name=self.name, parent=self.parent)


class FieldSerializer(ScopeContext):
    """Field serializer.
    """

    def dump(self, value):
        """Serialize given value.

        :param value: The value to serialize.
        :return: The serialized value.
        """
        raise NotImplementedError(
            'Abstract ``FieldSerializer`` does not implement ``dump``'
        )

    def load(self, value):
        """Deserialize given value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """
        raise NotImplementedError(
            'Abstract ``FieldSerializer`` does not implement ``load``'
        )


class TypeSerializer(FieldSerializer):
    """Serializer for arbitrary types.

    Converts value to string on serialization.
    Creates instance of type from string on deserialization.
    """

    def __init__(self, type_):
        """Create TypeSerializer instance.

        :param type_: Type to create at deserialization.
        """
        self.type_ = type_

    def dump(self, value):
        """Convert value to string.

        :param value: The value to convert. Must implement ``__str__``
        :return: Converted value as string.
        """
        return str(value)

    def load(self, value):
        """Create instance of ``type_`` from string.

        :param value: The string to convert. Gets passed to ``type_`` as only
        argument. ``type_`` must support creation from string.
        :return: Instance of ``type_``.
        """
        return self.type_(value)


int_serializer = TypeSerializer(int)
float_serializer = TypeSerializer(float)
uuid_serializer = TypeSerializer(uuid.UUID)


class IterableSerializer(FieldSerializer):
    """Serializer for iterables.

    Joins iterable into comma separated strings on serialization.
    Splits comma separated string into iterable on deserialization.
    """

    def __init__(self, type_):
        """Create IterableSerializer instance.

        :param type_: Type to create at deserialization.
        """
        self.type_ = type_

    def dump(self, value):
        """Join iterable value to string.

        :param value: The iterable to join. Must contain strings as values.
        :return: Items of iterable joined by ',' as string.
        """
        items = sorted([quote(item) for item in value])
        return u','.join(items)

    def load(self, value):
        """Split string into iterable.

        :param value: The string to split.
        :return: Instance of ``type_`` containing strings split by ',' from
        value.
        """
        return self.type_([unquote(item) for item in value.split(u',')])


list_serializer = IterableSerializer(list)
tuple_serializer = IterableSerializer(tuple)
set_serializer = IterableSerializer(set)


class MappingSerializer(FieldSerializer):
    """Serializer for mappings.

    Joins mapping key/value pairs into string on serialization.
    Splits string into mapping on deserialization.
    """

    def __init__(self, type_):
        """Create MappingSerializer instance.

        :param type_: Type to create at deserialization.
        """
        self.type_ = type_

    def dump(self, value):
        """Join dict key/value pairs into string.

        :param value: The dict to join. Keys and values must be strings.
        :return: Items of dict joined by ';' as string. Key/value pairs are
        joined by ','.
        """
        return u';'.join([
            u'{key},{value}'.format(key=quote(key), value=quote(val))
            for key, val in value.items()
        ])

    def load(self, value):
        """Split string into dict.

        :param value: The string to split.
        :return: Dict from value. Items of dict are split by ';'. Key/value
        pairs are split by ','.
        """
        ret = self.type_()
        for item in value.split(u';'):
            key, val = item.split(u',')
            ret[unquote(key)] = unquote(val)
        return ret


dict_serializer = MappingSerializer(dict)
odict_serializer = MappingSerializer(odict)


class Base64Serializer(FieldSerializer):
    """Serializer for encoding/decoding values with base64 coding."""

    coding = 'utf-8'

    def dump(self, value):
        """Encode value with base64.

        :param value: The value to encode.
        :return: Base64 encoded value.
        """
        return base64.b64encode(value.encode(self.coding)).decode()

    def load(self, value):
        """Encode base64 encoded value.

        :param value: The base64 encoded string.
        :return: Decoded value.
        """
        return base64.b64decode(value).decode(self.coding)


base64_serializer = Base64Serializer()


class JSONSerializer(FieldSerializer):
    """Serializer dumpin/loading values as JSON."""

    def dump(self, value):
        """Dump value as JSON string.

        :param value: The value to serialize.
        :return: JSON string.
        """
        return json.dumps(value)

    def load(self, value):
        """Load value from JSON string.

        :param value: The JSON string to deserialize.
        :return: Value loaded from JSON.
        """
        return json.loads(value)


json_serializer = JSONSerializer()


class PickleSerializer(FieldSerializer):
    """Serializer dumpin/loading values as pickels."""

    def dump(self, value):
        """Dump value as pickle.

        :param value: The object to serialize.
        :return: Pickled object.
        """
        return pickle.dumps(value)

    def load(self, value):
        """Load value from pickle.

        :param value: The object pickle to deserialize.
        :return: Object loaded from pickle.
        """
        return pickle.loads(value)


pickle_serializer = PickleSerializer()
