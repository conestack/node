from contextlib import contextmanager
from node import compat
try:
    from urllib import quote
    from urllib import unquote
except ImportError:
    from urllib.parse import quote
    from urllib.parse import unquote
import uuid


_undefined = object()


class IterJoin(object):
    """Join iterable into string."""

    def __init__(self, coding=u'utf-8'):
        """Create IterJoin instance.

        :param coding: Coding to use. defaults to 'utf-8'
        """
        self.coding = coding

    def __call__(self, value):
        """Join iterable value to string.

        :param value: The iterable to join. Must contain strings as values.
        :return: Items of iterable joined by ',' as string. If items contain
        commas themself, they get quoted.
        """
        return u','.join([quote(item) for item in value]).encode(self.coding)


iter_join = IterJoin()


class IterSplit(object):
    """Split string into iterable."""

    def __init__(self, coding=u'utf-8'):
        """Create IterSplit instance.

        :param coding: Coding to use. defaults to 'utf-8'
        """
        self.coding = coding

    def __call__(self, value):
        """Split string into iterable.

        :param value: The string to split.
        :return: List of strings split by ',' from value.
        """
        if not isinstance(value, compat.UNICODE_TYPE):
            value = value.decode(self.coding)
        return [unquote(item) for item in value.split(u',')]


iter_split = IterSplit()


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
                value = [value_type.deserialize(item) for item in value]
        return self.type_(value)

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

    def __init__(self, dump=_undefined, load=_undefined, default=_undefined):
        """Create bool field.

        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        """
        super(Bool, self).__init__(
            type_=bool,
            dump=dump,
            load=load,
            default=default
        )


class Int(Field):

    def __init__(self, dump=_undefined, load=_undefined, default=_undefined):
        """Create int field.

        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        """
        super(Int, self).__init__(
            type_=int,
            dump=dump,
            load=load,
            default=default
        )


class Float(Field):

    def __init__(self, dump=_undefined, load=_undefined, default=_undefined):
        """Create float field.

        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        """
        super(Float, self).__init__(
            type_=float,
            dump=dump,
            load=load,
            default=default
        )


class Bytes(Field):

    def __init__(self, dump=_undefined, load=_undefined, default=_undefined):
        """Create bytes field.

        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        """
        super(Bytes, self).__init__(
            type_=bytes,
            dump=dump,
            load=load,
            default=default
        )


class Str(Field):

    def __init__(self, dump=_undefined, load=_undefined, default=_undefined):
        """Create str field.

        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        """
        super(Str, self).__init__(
            type_=compat.UNICODE_TYPE,
            dump=dump,
            load=load,
            default=default
        )


class UUID(Field):

    def __init__(self, dump=_undefined, load=_undefined, default=_undefined):
        """Create UUID field.

        :param dump: Callable for serialization. Supposed to be used if value
        needs to be converted to a different format for serialization. Optional.
        :param load: Callable for deserialization. Supposed to be used if value
        needs to be parsed from a foreign format. Optional. If dump is set and
        load is omitted, type_ is used instead.
        :param default: Default value of the field. Optional.
        """
        super(UUID, self).__init__(
            type_=uuid.UUID,
            dump=dump,
            load=load,
            default=default
        )


class Tuple(IterableField):

    def __init__(
        self,
        dump=_undefined,
        load=_undefined,
        default=_undefined,
        value_type=_undefined,
        size=_undefined
    ):
        """Create tuple schema field.

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
        super(Tuple, self).__init__(
            type_=tuple,
            dump=dump,
            load=load,
            default=default,
            value_type=value_type,
            size=size
        )


class List(IterableField):

    def __init__(
        self,
        dump=_undefined,
        load=_undefined,
        default=_undefined,
        value_type=_undefined,
        size=_undefined
    ):
        """Create list schema field.

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
        super(List, self).__init__(
            type_=list,
            dump=dump,
            load=load,
            default=default,
            value_type=value_type,
            size=size
        )


class Set(IterableField):

    def __init__(
        self,
        dump=_undefined,
        load=_undefined,
        default=_undefined,
        value_type=_undefined,
        size=_undefined
    ):
        """Create set schema field.

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
        super(Set, self).__init__(
            type_=set,
            dump=dump,
            load=load,
            default=default,
            value_type=value_type,
            size=size
        )


class Dict(Field):

    def __init__(self, dump=_undefined, load=_undefined, default=_undefined):
        super(Dict, self).__init__(
            type_=dict,
            dump=dump,
            load=load,
            default=default
        )
