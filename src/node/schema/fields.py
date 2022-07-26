from node import compat
from node.schema.scope import scope_context
from node.schema.scope import ScopeContext
from node.schema.serializer import NodeSerializer
from node.utils import UNSET
from odict import odict
import datetime
import uuid


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


class DateTime(Field):

    def __init__(self, default=UNSET, serializer=UNSET):
        """Create DateTime schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        """
        super(DateTime, self).__init__(
            type_=datetime.datetime,
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
        self.type_ = odict


class Node(Field):

    def __init__(self, type_=UNSET, serializer=UNSET):
        """Create node schema field.

        :param type_: Type of the field value.
        :param serializer: ``NodeSerializer`` instance. Optional. If given,
        ``type_`` is taken from it and can be omitted in keyword arguments.
        """
        if serializer is not UNSET:
            type_ = serializer.type_
        elif type_ is not UNSET:
            serializer = NodeSerializer(type_)
        else:
            raise TypeError('Either ``type_`` or ``serializer`` must be given')
        super(Node, self).__init__(type_=type_, serializer=serializer)
