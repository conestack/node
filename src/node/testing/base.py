from odict import odict


def create_tree(class_):
        root = class_()
        for i in range(3):
            root['child_%i' % i] = class_()
            for j in range(2):
                root['child_%i' % i]['subchild_%i' % j] = class_()
        return root


class ResultWriter(object):

    def __init__(self, results, name=None):
        self.name = name
        self.results = results

    def success(self):
        self.results[self.name] = 'OK'

    def failed(self, exc):
        self.results[self.name] = 'failed: %s' % (repr(exc),)


class ContractError(Exception):
    pass


class BaseTester(object):
    # list of interface contract attributes to test.
    # test functions always are named 'test_[contractname]'.
    # execution is in order, so you might depend tests to prior happened
    # context manipulation.
    iface_contract = []

    direct_error = False

    def __init__(self, class_, context=None):
        """
        ``class_``
            class object for creating children in test.
        ``context``
            an optional root context to test against, If None, an instance of
            class_ is created as root.
        """
        self._results = odict()
        self.class_ = class_
        self.context = context
        if self.context is None:
            self.context = class_()
        self._results = odict()

    @property
    def results(self):
        return self._results

    @property
    def combined(self):
        for key, val in sorted(self.writer().results.iteritems()):
            print '``%s``: %s' % (key, val)

    @property
    def wherefrom(self):
        for name in sorted(self.iface_contract):
            print name + ": ",
            if name in self.class_.__dict__:
                print self.class_.__name__
            else:
                for base in self.class_.__bases__:
                    if name in base.__dict__:
                        print base.__name__
                        continue
                    print "function not found on object"

    def run(self):
        for name in self.iface_contract:
            func = getattr(self, 'test_%s' % name, None)
            if func is None:
                msg = '``%s`` does not provide ``test_%s``' % (
                    self.__class__.__name__, name)
                raise ContractError(msg)
            writer = self.writer(name)
            if self.direct_error:
                func()
                writer.success()
                continue
            try:
                func()
                writer.success()
            except Exception, e:
                writer.failed(e)

    def writer(self, key=None):
        return ResultWriter(self._results, name=key)
