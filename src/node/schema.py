from node import compat
from node.base import BaseNode
from node.utils import UNSET
import uuid


class Field(object):
    name = None
    parent = None

    def __init__(self, type_=UNSET, default=UNSET):
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
        if self.type_ is not UNSET:
            return isinstance(value, self.type_)
        return True


class Int(Field):

    def __init__(self, default=UNSET):
        super(Int, self).__init__(type_=int, default=default)


class Float(Field):

    def __init__(self, default=UNSET):
        super(Float, self).__init__(type_=float, default=default)


class Bytes(Field):

    def __init__(self, default=UNSET):
        super(Bytes, self).__init__(type_=bytes, default=default)


class Str(Field):

    def __init__(self, default=UNSET):
        super(Str, self).__init__(type_=compat.UNICODE_TYPE, default=default)


class Tuple(Field):

    def __init__(self, default=UNSET):
        super(Tuple, self).__init__(type_=tuple, default=default)


class List(Field):

    def __init__(self, default=UNSET):
        super(List, self).__init__(type_=list, default=default)


class Dict(Field):

    def __init__(self, default=UNSET):
        super(Dict, self).__init__(type_=dict, default=default)


class Set(Field):

    def __init__(self, default=UNSET):
        super(Set, self).__init__(type_=set, default=default)


class UUID(Field):

    def __init__(self, default=UNSET):
        super(UUID, self).__init__(type_=uuid.UUID, default=default)


class Node(Field):

    def __init__(self, type_=BaseNode, default=UNSET, factory=UNSET):
        super(Node, self).__init__(type_=type_, default=default)
        self.factory = self.default_factory if factory is UNSET else factory

    def default_factory(self, field):
        return field.type_(name=field.name, parent=field.parent)

    def deserialize(self, value):
        if not isinstance(value, self.type_):
            value = self.factory(self)
        return value
