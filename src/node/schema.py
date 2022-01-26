from contextlib import contextmanager
from node import compat
import uuid


_undefined = object()


@contextmanager
def scope_field(field, name, parent):
    """Context manager for setting field scope.

    Gets called by ``Schema.__getitem__`` and ``Schema.__setitem__``. Useful
    if custom field implementations want to gather information from the model.

    :param field: The field instance to scope.
    :param name: The field name in this scope.
    :param parent: The field containing model for this scope.
    """
    field.set_scope(name, parent)
    try:
        yield field
    finally:
        field.reset_scope()


class Field(object):
    """A schema field."""

    name = None
    """Name of the field while scoped."""

    parent = None
    """Parent of the field while scoped."""

    def __init__(
        self,
        type_,
        dump=_undefined,
        load=_undefined,
        default=_undefined,
    ):
        """Create schema field.

        :param type_: Type of the value for validation.
        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        """
        self.type_ = type_
        self.dump = dump
        if dump is not _undefined and load is _undefined:
            load = type_
        self.load = load
        self.default = default

    def serialize(self, value):
        """Serialize value.

        :param value: The value to serialize.
        :return: The serialized value.
        """
        if self.dump is not _undefined:
            return self.dump(value)
        return value

    def deserialize(self, value):
        """Deerialize value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """
        if self.load is not _undefined:
            return self.load(value)
        return value

    def validate(self, value):
        """Validate value.

        :param value: The value to validate.
        :raises Exception: If validation fails.
        """
        if not isinstance(value, self.type_):
            raise ValueError(u'{} is no {} type'.format(value, self.type_))

    def set_scope(self, name, parent):
        """Set scope of field. Handled by ``scope_field`` context manager.

        :param name: The field name.
        :param parent: The parent object.
        """
        self.name = name
        self.parent = parent

    def reset_scope(self):
        """Reset scope of field. Handled by ``scope_field`` context manager.
        """
        self.set_scope(None, None)


class IterableField(Field):
    """An iterable schema field."""

    def __init__(
        self,
        type_,
        dump=_undefined,
        load=_undefined,
        default=_undefined,
        value_type=_undefined,
        size=_undefined
    ):
        """Create iterable schema field.

        :param type_: Type of the value for validation.
        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        :param value_type: Field instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(IterableField, self).__init__(
            type_,
            dump=dump,
            load=load,
            default=default
        )
        self.value_type = value_type
        self.size = size

    def serialize(self, value):
        """Serialize value.

        :param value: The value to serialize.
        :return: The serialized value.
        """
        value_type = self.value_type
        if value_type is not _undefined:
            with scope_field(value_type, self.name, self.parent):
                value = self.type_(
                    [value_type.serialize(item) for item in value]
                )
        return super(IterableField, self).serialize(value)

    def deserialize(self, value):
        """Deerialize value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """
        value = super(IterableField, self).deserialize(value)
        value_type = self.value_type
        if value_type is not _undefined:
            with scope_field(value_type, self.name, self.parent):
                value = self.type_(
                    [value_type.deserialize(item) for item in value]
                )
        return value

    def validate(self, value):
        """Validate value.

        :param value: The value to validate.
        :raises Exception: If validation fails.
        """
        super(IterableField, self).validate(value)
        if self.size is not _undefined and len(value) != self.size:
            raise ValueError(u'{} has invalid size {} != {}'.format(
                value,
                len(value),
                self.size
            ))
        value_type = self.value_type
        if value_type is not _undefined:
            with scope_field(value_type, self.name, self.parent):
                for item in value:
                    value_type.validate(item)


class Bool(Field):

    def __init__(self, default=_undefined):
        super(Bool, self).__init__(type_=bool, default=default)


class Int(Field):

    def __init__(self, default=_undefined):
        super(Int, self).__init__(type_=int, default=default)


class Float(Field):

    def __init__(self, default=_undefined):
        super(Float, self).__init__(type_=float, default=default)


class Bytes(Field):

    def __init__(self, default=_undefined):
        super(Bytes, self).__init__(type_=bytes, default=default)


class Str(Field):

    def __init__(self, default=_undefined):
        super(Str, self).__init__(type_=compat.UNICODE_TYPE, default=default)


class Tuple(Field):

    def __init__(self, default=_undefined):
        super(Tuple, self).__init__(type_=tuple, default=default)


class List(Field):

    def __init__(self, default=_undefined):
        super(List, self).__init__(type_=list, default=default)


class Dict(Field):

    def __init__(self, default=_undefined):
        super(Dict, self).__init__(type_=dict, default=default)


class Set(Field):

    def __init__(self, default=_undefined):
        super(Set, self).__init__(type_=set, default=default)


class UUID(Field):

    def __init__(self, default=_undefined):
        super(UUID, self).__init__(type_=uuid.UUID, default=default)
