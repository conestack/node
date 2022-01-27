from abc import ABC
from abc import abstractmethod
from contextlib import contextmanager
from node import compat
from node.utils import UNSET
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
        default=UNSET,
        serializer=UNSET,
        dump=UNSET,
        load=UNSET,
    ):
        """Create schema field.

        :param type_: Type of the field value.
        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        """
        dump = serializer.dump if serializer is not UNSET else dump
        load = serializer.load if serializer is not UNSET else load
        if dump is not UNSET and load is UNSET:
            load = type_
        self.type_ = type_
        self.default = default
        self.dump = dump
        self.load = load

    def serialize(self, value):
        """Serialize value.

        :param value: The value to serialize.
        :return: The serialized value.
        """
        if self.dump is not UNSET:
            return self.dump(value)
        return value

    def deserialize(self, value):
        """Deserialize value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """
        if self.load is not UNSET:
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
        default=UNSET,
        serializer=UNSET,
        dump=UNSET,
        load=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create iterable schema field.

        :param type_: Type of the field value.
        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(IterableField, self).__init__(
            type_,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load
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
            with scope_field(value_type, self.name, self.parent):
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
            with scope_field(value_type, self.name, self.parent):
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
            with scope_field(value_type, self.name, self.parent):
                for item in value:
                    value_type.validate(item)


class Bool(Field):

    def __init__(
            self,
            default=UNSET,
            serializer=UNSET,
            dump=UNSET,
            load=UNSET
        ):
        """Create bool schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        """
        super(Bool, self).__init__(
            type_=bool,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
        )


class Int(Field):

    def __init__(
            self,
            default=UNSET,
            serializer=UNSET,
            dump=UNSET,
            load=UNSET
        ):
        """Create int field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        """
        super(Int, self).__init__(
            type_=int,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
        )


class Float(Field):

    def __init__(
            self,
            default=UNSET,
            serializer=UNSET,
            dump=UNSET,
            load=UNSET
        ):
        """Create float schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        """
        super(Float, self).__init__(
            type_=float,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
        )


class Bytes(Field):

    def __init__(
            self,
            default=UNSET,
            serializer=UNSET,
            dump=UNSET,
            load=UNSET
        ):
        """Create bytes schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        """
        super(Bytes, self).__init__(
            type_=bytes,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
        )


class Str(Field):

    def __init__(
            self,
            default=UNSET,
            serializer=UNSET,
            dump=UNSET,
            load=UNSET
        ):
        """Create str schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        """
        super(Str, self).__init__(
            type_=compat.UNICODE_TYPE,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
        )


class UUID(Field):

    def __init__(
            self,
            default=UNSET,
            serializer=UNSET,
            dump=UNSET,
            load=UNSET
        ):
        """Create UUID schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        """
        super(UUID, self).__init__(
            type_=uuid.UUID,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
        )


class Tuple(IterableField):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        dump=UNSET,
        load=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create tuple schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(Tuple, self).__init__(
            type_=tuple,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
            value_type=value_type,
            size=size
        )


class List(IterableField):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        dump=UNSET,
        load=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create list schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(List, self).__init__(
            type_=list,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
            value_type=value_type,
            size=size
        )


class Set(IterableField):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        dump=UNSET,
        load=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create set schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(Set, self).__init__(
            type_=set,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
            value_type=value_type,
            size=size
        )


class Dict(Field):

    def __init__(
        self,
        default=UNSET,
        serializer=UNSET,
        dump=UNSET,
        load=UNSET,
        key_type=UNSET,
        value_type=UNSET,
        size=UNSET
    ):
        """Create dict schema field.

        :param default: Default value of the field. Optional.
        :param serializer: ``Serializer`` instance. Supposed to be used if
        field value needs to be converted for serialization. Optional.
        :param dump: Callable for field value serialization. Optional. Taken
        from ``serializer`` if given.
        :param load: Callable for field value deserialization. Optional. Taken
        from ``serializer`` if given. If ``dump`` is set and ``load`` is
        omitted, ``type_`` is used instead.
        :param key_type: ``Field`` instance defining the key type of the
        iterable. Optional.
        :param value_type: ``Field`` instance defining the value type of the
        iterable. Optional.
        :param size: The allowed size of the iterable. Optional.
        """
        super(Dict, self).__init__(
            type_=dict,
            default=default,
            serializer=serializer,
            dump=dump,
            load=load,
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
            with scope_field(key_type, self.name, self.parent):
                new_value = dict()
                for key, val in value.items():
                    new_value[key_type.serialize(key)] = val
                value = new_value
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_field(value_type, self.name, self.parent):
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
            with scope_field(key_type, self.name, self.parent):
                new_value = dict()
                for key, val in value.items():
                    new_value[key_type.deserialize(key)] = val
                value = new_value
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_field(value_type, self.name, self.parent):
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
            with scope_field(key_type, self.name, self.parent):
                for key in value:
                    key_type.validate(key)
        value_type = self.value_type
        if value_type is not UNSET:
            with scope_field(value_type, self.name, self.parent):
                for val in value.values():
                    value_type.validate(val)


class Serializer(ABC):
    """Field serializer.
    """

    @abstractmethod
    def dump(self, value):
        """Serialize given value.

        :param value: The value to serialize.
        :return: The serialized value.
        """

    @abstractmethod
    def load(self, value):
        """Deserialize given value.

        :param value: The value to deserialize.
        :return: The deserialized value.
        """


class IterJoin(object):
    """Join iterable into string."""

    def __init__(self, coding=u'utf-8'):
        """Create IterJoin instance.

        :param coding: Coding to use. defaults to 'utf-8'.
        """
        self.coding = coding

    def __call__(self, value):
        """Join iterable value to string.

        :param value: The iterable to join. Must contain strings as values.
        :return: Items of iterable joined by ',' as string.
        """
        return u','.join([quote(item) for item in value]).encode(self.coding)


iter_join = IterJoin()


class IterSplit(object):
    """Split string into iterable."""

    def __init__(self, coding=u'utf-8'):
        """Create IterSplit instance.

        :param coding: Coding to use. defaults to 'utf-8'.
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


class IterSerializer(Serializer):
    """Serializer utilizing IterJoin and IterSplit.
    """

    def __init__(self, coding='utf-8'):
        """Create IterSerializer instance.

        :param coding: Coding to use. defaults to 'utf-8'.
        """
        self.dumper = IterJoin(coding=coding)
        self.loader = IterSplit(coding=coding)

    def dump(self, value):
        """Join iterable value to string.

        :param value: The iterable to join. Must contain strings as values.
        :return: Items of iterable joined by ',' as string.
        """
        return self.dumper(value)

    def load(self, value):
        """Split string into iterable.

        :param value: The string to split.
        :return: List of strings split by ',' from value.
        """
        return self.loader(value)


iter_serializer = IterSerializer()


class DictJoin(object):
    """Join dict key/value pairs into string."""

    def __init__(self, coding=u'utf-8'):
        """Create DictJoin instance.

        :param coding: Coding to use. defaults to 'utf-8'.
        """
        self.coding = coding

    def __call__(self, value):
        """Join dict key/value pairs into string.

        :param value: The dict to join. Keys and values must be strings.
        :return: Items of dict joined by ';' as string. Key/value pairs are
        joined by ','.
        """
        return u';'.join([
            u'{key},{value}'.format(key=quote(key), value=quote(val))
            for key, val in value.items()
        ]).encode(self.coding)


dict_join = DictJoin()


class DictSplit(object):
    """Split string into dict."""

    def __init__(self, coding=u'utf-8'):
        """Create DictSplit instance.

        :param coding: Coding to use. defaults to 'utf-8'.
        """
        self.coding = coding

    def __call__(self, value):
        """Split string into dict.

        :param value: The string to split.
        :return: Dict from value. Items of dict are split by ';'. Key/value
        pairs are split by ','.
        """
        if not isinstance(value, compat.UNICODE_TYPE):
            value = value.decode(self.coding)
        ret = {}
        for item in value.split(';'):
            key, val = item.split(',')
            ret[unquote(key)] = unquote(val)
        return ret


dict_split = DictSplit()


class DictSerializer(Serializer):
    """Serializer utilizing DictJoin and DictSplit.
    """

    def __init__(self, coding='utf-8'):
        """Create DictSerializer instance.

        :param coding: Coding to use. defaults to 'utf-8'.
        """
        self.dumper = DictJoin(coding=coding)
        self.loader = DictSplit(coding=coding)

    def dump(self, value):
        """Join dict key/value pairs into string.

        :param value: The dict to join. Keys and values must be strings.
        :return: Items of dict joined by ';' as string. Key/value pairs are
        joined by ','.
        """
        return self.dumper(value)

    def load(self, value):
        """Split string into dict.

        :param value: The string to split.
        :return: Dict from value. Items of dict are split by ';'. Key/value
        pairs are split by ','.
        """
        return self.loader(value)


dict_serializer = DictSerializer()


class Base64Serializer(Serializer):
    """Serializer for encoding/decoding values with base64 coding."""

    def __init__(self, type_=compat.UNICODE_TYPE, coding='utf-8'):
        """Create Base64Serializer instance.

        :param type_: Value type. Either unicode type or ``bytes``. Defaults to
        unicode type.
        :param coding: Coding to use for encoding values if ``type_`` is
        unicode type.
        Defaults to 'utf-8'.
        """
        self.type_ = type_
        self.coding = coding

    def dump(self, value):
        """Encode value with base64.

        :param value: The value to encode.
        :return: Base64 encoded value.
        """
        if self.type_ is compat.UNICODE_TYPE:
            value = value.encode(self.coding)
        return base64.b64encode(value)

    def load(self, value):
        """Encode base64 encoded value.

        :param value: The base64 encoded string.
        :return: Decoded value.
        """
        value = base64.b64decode(value)
        if self.type_ is compat.UNICODE_TYPE:
            value = value.decode(self.coding)
        return value


base64_serializer = Base64Serializer()


class JSONSerializer(Serializer):
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


class PickleSerializer(Serializer):
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
