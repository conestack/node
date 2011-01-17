from plumber import plumbing


# XXX: currently won't work, as the decode function is missing
# check the one in bda.ldap.strcodec
# XXX: It feels here it would be nice to be able to get an instance of a
# plumbing to configure the codec.
class Unicode(object):
    """Plumbing element to ensure unicode for keys and string values
    """
    @plumbing
    def __delitem__(cls, _next, self, key):
        if isinstance(key, str):
            key = decode(key)
        _next(key)

    @plumbing
    def __getitem__(cls, _next, self, key):
        if isinstance(key, str):
            key = decode(key)
        return _next(key)

    @plumbing
    def __setitem__(cls, _next, self, key, val):
        if isinstance(key, str):
            key = decode(key)
        if isinstance(val, str):
            val = decode(val)
        return _next(key, val)
