"""
The SharedMock object has an interface similar to Python’s own unittest.mock.Mock.
The main difference is that the state of a SharedMock object is shared among subprocesses.
This allows you to easily test interactions of subprocesses with your mock instance.

Source: https://github.com/elritsch/python-sharedmock
"""

from multiprocessing.managers import BaseManager, BaseProxy
from unittest import mock
from pprint import pformat


class SharedMockObj:

    def __init__(self):
        self.call_parameters = []
        self._set_return_value(None)

    def __call__(self, *args, **kwargs):
        self.call_parameters.append({'args': args, 'kwargs': kwargs})
        return self.return_value

    def _get_call_parameters(self):
        return self.call_parameters

    def _set_return_value(self, value):
        self.return_value = value

    def call_count(self):
        return len(self.call_parameters)


class SharedMockProxy(BaseProxy):
    _exposed_ = ['__call__',
                 '_get_call_parameters',
                 '_set_return_value',
                 '_set_return_value_empty_dict',
                 'assert_has_calls',
                 'call_count'
                 ]

    def __setattr__(self, name, value):
        if name == 'return_value':
            self._callmethod('_set_return_value', args=(value,))
        else:
            # forward any unknown attributes to the super class
            super().__setattr__(name, value)

    def __call__(self, *args, **kwargs):
        return self._callmethod('__call__', args, kwargs)

    def assert_has_calls(self, expected_calls, same_order=True):
        calls = self.mock_calls
        if same_order:
            assert_calls_equal(expected_calls, calls)
        else:
            assert_calls_equal_unsorted(expected_calls, calls)

    @property
    def call_count(self):
        return self._callmethod('call_count')

    @property
    def mock_calls(self):
        call_parameters = self._callmethod('_get_call_parameters')

        calls = []
        for cur_call in call_parameters:
            args = cur_call['args']
            kwargs = cur_call['kwargs']
            calls.append(mock.call(*args, **kwargs))
        return calls


class SharedMockManager(BaseManager):

    def __init__(self):
        BaseManager.__init__(self)


SharedMockManager.register('Mock',
                           SharedMockObj,
                           SharedMockProxy)


def SharedMock():
    """
    SharedMock factory for convenience, in order to avoid using a context manager
    to get a SharedMock object.
    NB: Consequently, this does leak the manager resource. I wonder whether there's
    a way to clean that up..?
    """
    manager = SharedMockManager()
    manager.start()
    return manager.Mock()


def assert_calls_equal(expected, actual):
    """
    Check whether the given mock object (or mock method) calls are equal and
    return a nicely formatted message.
    """
    if not expected == actual:
        raise_calls_differ_error(expected, actual)


def raise_calls_differ_error(expected, actual):
    """
    Raise an AssertionError with pretty print format for the given expected
    and actual mock calls in order to ensure consistent print style for better
    readability.
    """
    expected_str = pformat(expected)
    actual_str = pformat(actual)
    msg = '\nMock calls differ!\nExpected calls:\n{}\nActual calls:\n{}'.format(
        expected_str,
        actual_str
    )
    raise AssertionError(msg)


def assert_calls_equal_unsorted(expected, actual):
    """
    Raises an AssertionError if the two iterables do not contain the same items.
    The order of the items is ignored
    """
    for expected in expected:
        if expected not in actual:
            raise_calls_differ_error(expected, actual)

