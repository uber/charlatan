import calendar
import datetime
import functools
import itertools
import operator
import re
import collections

from charlatan import _compat

VALID_SIGNS = frozenset(['-', '+'])


def get_timedelta(delta):
    """Return timedelta from string.

    :param str delta:

    :rtype: :py:class:`datetime.timedelta` instance

    >>> get_timedelta("")
    datetime.timedelta(0)
    >>> get_timedelta("+1h")
    datetime.timedelta(0, 3600)
    >>> get_timedelta("+10h")
    datetime.timedelta(0, 36000)
    >>> get_timedelta("-10d")
    datetime.timedelta(-10)
    >>> get_timedelta("+1m")
    datetime.timedelta(30)
    >>> get_timedelta("-1y")
    datetime.timedelta(-365)
    >>> get_timedelta("+10d2h")
    datetime.timedelta(10, 7200)
    >>> get_timedelta("-10d2h")
    datetime.timedelta(-11, 79200)
    >>> get_timedelta("-21y2m1d24h")
    datetime.timedelta(-7727)
    >>> get_timedelta("+5M")
    datetime.timedelta(0, 300)

    """
    if not delta:
        return datetime.timedelta()
    sign = delta[0]
    assert sign in VALID_SIGNS
    delta = delta[1:]
    timedelta_kwargs = {}

    # re.split returns empty strings if the capturing groups matches the
    # start and the end of string.
    for part in filter(lambda p: p, re.split(r"(\d+\w)", delta)):
        amount, unit = re.findall(r"(\d+)([ymdhMs])", part)[0]
        units = {
            "s": "seconds",
            "M": "minutes",
            "h": "hours",
            "d": "days",
            "m": "months",
            "y": "years"
        }
        timedelta_kwargs[units[unit]] = int(amount)

    delta = extended_timedelta(**timedelta_kwargs)
    if sign == '-':
        return -delta
    else:
        return delta


def extended_timedelta(**kwargs):
    """Return a :py:class:`timedelta` object based on the arguments.

    :param integer years:
    :param integer months:
    :param integer days:
    :rtype: :py:class:`timedelta` instance

    Since :py:class:`timedelta`'s largest unit are days, :py:class:`timedelta`
    objects cannot be created with a number of months or years as an argument.
    This function lets you create :py:class:`timedelta` objects based on a
    number of days, months and years.

    >>> extended_timedelta(months=1)
    datetime.timedelta(30)
    >>> extended_timedelta(years=1)
    datetime.timedelta(365)
    >>> extended_timedelta(days=1, months=1, years=1)
    datetime.timedelta(396)
    >>> extended_timedelta(hours=1)
    datetime.timedelta(0, 3600)
    """
    number_of_days = {
        "days": 1,
        "months": 30,
        "years": 365}

    days = []
    kwargs_copy = kwargs.copy()  # So that we can remove values from kwargs
    for k in kwargs_copy:
        if k in number_of_days:
            days.append([number_of_days[k], kwargs.pop(k)])

    if days:
        add = int(functools.reduce(
            operator.add, itertools.starmap(operator.mul, days)))
        kwargs["days"] = kwargs.setdefault("days", 0) + add

    return datetime.timedelta(**kwargs)


def datetime_to_epoch_timestamp(a_datetime):
    """Return the epoch timestamp for the given datetime.

    :param datetime a_datetime: The datetime to translate
    :rtype: float

    >>> a_datetime = datetime.datetime(2013, 11, 21, 1, 33, 11, 160611)
    >>> datetime_to_epoch_timestamp(a_datetime)
    1384997591.160611
    """
    return (calendar.timegm(a_datetime.utctimetuple()) + a_datetime.microsecond / 1000000.0)  # noqa


def datetime_to_epoch_in_ms(a_datetime):
    """Return the epoch timestamp for the given datetime.

    :param datetime a_datetime: The datetime to translate
    :rtype: int

    >>> a_datetime = datetime.datetime(2013, 11, 21, 1, 33, 11, 160611)
    >>> datetime_to_epoch_timestamp(a_datetime)
    1384997591.160611
    >>> datetime_to_epoch_in_ms(a_datetime)
    1384997591161
    """
    seconds_in_float = datetime_to_epoch_timestamp(a_datetime)
    return int(round(seconds_in_float * 1000, 0))


# TODO: does not copy the function signature
# see http://stackoverflow.com/questions/2982974/copy-call-signature-to-decorator  # noqa


def copy_docstring_from(klass):
    """Copy docstring from another class, using the same function name."""
    def wrapper(func):
        func.__doc__ = getattr(klass, func.__name__).__doc__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapped

    return wrapper


def safe_iteritems(items):
    """Safely iterate over a dict or a list."""
    # For dictionaries, iterate over key, value and for lists iterate over
    # index, item
    if hasattr(items, 'items'):
        return _compat.iteritems(items)
    else:
        return enumerate(items)


def is_sqlalchemy_model(instance):
    """Return True if instance is an SQLAlchemy model instance."""
    from sqlalchemy.orm.util import class_mapper
    from sqlalchemy.orm.exc import UnmappedClassError

    try:
        class_mapper(instance.__class__)

    except UnmappedClassError:
        return False

    else:
        return True


def richgetter(obj, path):
    """Return a attrgetter + item getter."""
    for name in path.split("."):
        if isinstance(obj, collections.Mapping):
            obj = obj[name]
        elif isinstance(obj, collections.Sequence):
            obj = obj[int(name)]  # force int type for list indexes
        else:
            obj = getattr(obj, name)

    return obj


def deep_update(source, overrides):
    """Update a nested dictionary or similar mapping.

    Modify ``source`` in place.
    """
    # http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth  # noqa
    for key, value in _compat.iteritems(overrides):
        if isinstance(value, collections.Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]
    return source
