from node import compat
import uuid


_undefined = object()


class Field(object):
    """A schema field.

    Describes the data type and default value of node values.

    Supports optional serialization and deserialization of node values.

    By default, ``serialize`` and ``deserialize`` functions return value as is.
    They are meant as hooks, e.g. if underlying storage only supports string
    values, or if binary data should end up at different physical storage, etc.
    In such cases, subclasses must be created implementing the concrete
    handling.
    """
    name = None
    parent = None

    def __init__(self, type_=_undefined, default=_undefined):
        self.type_ = type_
        self.default = default

    def set_scope(self, name, parent):
        self.name = name
        self.parent = parent

    def reset_scope(self):
        self.set_scope(None, None)

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value

    def validate(self, value):
        if self.type_ is not _undefined:
            return isinstance(value, self.type_)
        return True


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
