BaseTester
----------

Used to write testing code for an interface contract.

A subclass must define ``iface_contract`` containing the functions names of
interface to be tested and a testing function for each contract function
prefixed with 'test_'::

    >>> from node.testing.base import BaseTester
    >>> class DummyTester(BaseTester):
    ...     iface_contract = ['func_a', 'func_b', 'func_c']
    ...     def test_func_a(self):
    ...         self.context.func_a()
    ...     def test_func_b(self):
    ...         self.context.func_b()
    ...     def test_func_c(self):
    ...         self.context.func_c()

Test implementations::

    >>> class FuncAImpl(object):
    ...     def func_a(self):
    ...         pass
    
    >>> class FuncBImpl(FuncAImpl):
    ...     def func_b(self):
    ...         raise Exception('func_b failed')

Tester object expects the implementation class on init, and optional a already
instantiated testing instance. If context is not given, it is instantiated
by given class without arguments::

    >>> tester = DummyTester(FuncBImpl)

Run and print combined results::

    >>> tester.run()
    >>> tester.combined
    ``func_a``: OK
    ``func_b``: failed: Exception('func_b failed',)
    ``func_c``: failed: AttributeError("'FuncBImpl' object has no attribute 'func_c'",)

Get results of testing as odict::

    >>> tester.results
    odict([('func_a', 'OK'), 
    ('func_b', "failed: Exception('func_b failed',)"), 
    ('func_c', 'failed: AttributeError("\'FuncBImpl\' object has no attribute \'func_c\'",)')])

Print classes which actually provides the function implementation::

    >>> tester.wherefrom
    func_a:  FuncAImpl
    func_b:  FuncBImpl
    func_c:  function not found on object

A tester can be forced to raise exceptions directly instead of collecting them::

    >>> tester.direct_error = True
    >>> tester.run()
    Traceback (most recent call last):
      ...
    Exception: func_b failed

If tester does define a function to test in ``iface_contract`` but not
implements the related testing function, ``run`` will fail::

    >>> class BrokenTester(BaseTester):
    ...     iface_contract = ['test_me']
    
    >>> tester = BrokenTester(FuncBImpl)
    >>> tester.run()
    Traceback (most recent call last):
      ...
    ContractError: ``BrokenTester`` does not provide ``test_test_me``
