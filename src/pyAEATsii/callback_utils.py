
__all__ = [
    'fixed_value',
    'coalesce',
]


from itertools import ifilter


class _FixedValue(object):

    def __init__(self, value):
        self._value = value

    def __call__(self, *args, **kwargs):
        return self._value


def fixed_value(value):
    return _FixedValue(value)


class _Coalesce(object):

    def _filter(self, x):
        return x is not None

    def __init__(self, callbacks, else_=None):
        self._callbacks = callbacks
        self._else = else_

    def __call__(self, invoice):
        results = (
            callback(invoice)
            for callback in self._callbacks
        )
        try:
            return next(ifilter(
                self._filter, results
            ))
        except StopIteration:
            return self._else


def coalesce(callbacks, else_=None):
    return _Coalesce(callbacks, else_=else_)
