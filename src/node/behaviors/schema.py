from contextlib import contextmanager
from node.utils import UNSET
from plumber import Behavior
from plumber import default
from plumber import plumb


@contextmanager
def scope_field(field, name, parent):
    field.set_scope(name, parent)
    try:
        yield field
    finally:
        field.reset_scope()


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
            except KeyError:
                if field.default is not UNSET:
                    return field.default
                raise

    @plumb
    def __setitem__(next_, self, name, value):
        field = self.schema.get(name)
        if not field:
            next_(self, name, value)
            return
        with scope_field(field, name, self):
            if not field.validate(value):
                raise ValueError(u'{} is no {}'.format(value, field.type_))
            next_(self, name, field.serialize(value))
