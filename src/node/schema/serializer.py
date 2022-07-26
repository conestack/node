from node.schema.scope import ScopeContext
from odict import odict
try:  # pragma: no cover
    from urllib import quote
    from urllib import unquote
except ImportError:  # pragma: no cover
    from urllib.parse import quote
    from urllib.parse import unquote
import base64
import datetime
import json
import pickle
import uuid


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


class DateTimeSerializer(FieldSerializer):
    """Serializer for datetime instances.

    Converts value to string on serialization.
    Creates datetime instance of string on deserialization.
    """

    format = '%Y-%m-%dT%H:%M:%S.%f'

    def dump(self, value):
        """Dump datetime value as string.

        :param value: The datetime object to serialize.
        :return: Datetime as string.
        """
        return datetime.datetime.strftime(value, self.format)

    def load(self, value):
        """Load datetime value from string.

        :param value: The datetime string to deserialize.
        :return: Datetime object.
        """
        return datetime.datetime.strptime(value, self.format)


datetime_serializer = DateTimeSerializer()


class NodeSerializer(FieldSerializer):
    """Serializer for handling node instances."""

    def __init__(self, type_):
        """Create NodeSerializer instance.

        :param type_: The node type.
        """
        self.type_ = type_

    def dump(self, value):
        """Dump value as is.

        :param value: The node instance to serialize.
        :return: The node instance.
        """
        return value

    def load(self, value):
        """Load value from parent.

        :param value: Value to deserialize node instance from.
        :return: The node instance.
        """
        if isinstance(value, self.type_):
            return value
        name = self.name
        parent = self.parent
        value = parent[name] = self.type_(name=name, parent=parent)
        return value
