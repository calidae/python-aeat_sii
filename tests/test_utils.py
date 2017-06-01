
from mock import MagicMock

from pyAEATsii import callback_utils


def _return_arg(x):
    return x


def _return_none(x):
    return None


def test_fixed_value():
    fixed_value = callback_utils.fixed_value('RETURN')
    assert fixed_value(None) == 'RETURN'


def test_coalesce_1():
    coalesce = callback_utils.coalesce([
        _return_arg
    ])
    assert coalesce('RETURN') == 'RETURN'


def test_coalesce_0():
    coalesce = callback_utils.coalesce([
    ])
    assert coalesce(None) is None


def test_coalesce_else():
    coalesce = callback_utils.coalesce([], else_='ELSE')
    assert coalesce(None) is 'ELSE'


def test_coalesce_2():
    coalesce = callback_utils.coalesce([
        _return_none, _return_none
    ], else_='ELSE')
    assert coalesce(None) is 'ELSE'


def test_coalesce_10():
    coalesce = callback_utils.coalesce([_return_none] * 10, else_='ELSE')
    assert coalesce(None) is 'ELSE'


def test_coalesce_self():
    class Mapper(object):
        coalesce = callback_utils.coalesce([_return_none] * 10, else_='ELSE')

        def call(self, x):
            return self.coalesce(x)

    mapper = Mapper()
    assert mapper.call('SOMETHING') is 'ELSE'


def test_coalesce_calls():
    first = MagicMock()
    second = MagicMock()
    last = MagicMock()
    first.return_value = None
    second.return_value = 'MOCK'

    coalesce = callback_utils.coalesce([first, second, last])
    value = coalesce('VALUE')

    assert first.called
    assert value is 'MOCK'
    assert not last.called
