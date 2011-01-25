from plumber import (
    plumb,
    Part,
)

# XXX: currently won't work, as the decode function is missing
# check the one in bda.ldap.strcodec
# XXX: It feels here it would be nice to be able to get an instance of a
# plumbing to configure the codec.
class Unicode(Part):
    """Plumbing element to ensure unicode for keys and string values.
    """
    
    @plumb
    def __delitem__(_next, self, key):
        if isinstance(key, str):
            key = decode(key)
        _next(key)

    @plumb
    def __getitem__(_next, self, key):
        if isinstance(key, str):
            key = decode(key)
        return _next(key)

    @plumb
    def __setitem__(_next, self, key, val):
        if isinstance(key, str):
            key = decode(key)
        if isinstance(val, str):
            val = decode(val)
        return _next(key, val)
