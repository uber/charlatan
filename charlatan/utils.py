import calendar
import datetime
import functools
import itertools
import operator
import re


def apply_delta(dt, delta):
    """Apply datetime delta in string format to a datetime object.

    :param datetime dt:
    :param str delta:

    :rtype: :py:class:`datetime.DateTime` instance

    >>> base = datetime.datetime(2012, 1, 1, 1, 1, 1)
    >>> apply_delta(base, "+1h")
    datetime.datetime(2012, 1, 1, 2, 1, 1)
    >>> apply_delta(base, "+10h")
    datetime.datetime(2012, 1, 1, 11, 1, 1)
    >>> apply_delta(base, "-10d")
    datetime.datetime(2011, 12, 22, 1, 1, 1)
    >>> apply_delta(base, "+1m")
    datetime.datetime(2012, 1, 31, 1, 1, 1)
    >>> apply_delta(base, "-1y")
    datetime.datetime(2011, 1, 1, 1, 1, 1)
    >>> apply_delta(base, "+10d2h")
    datetime.datetime(2012, 1, 11, 3, 1, 1)
    >>> apply_delta(base, "-10d2h")
    datetime.datetime(2011, 12, 21, 23, 1, 1)
    >>> apply_delta(base, "-21y2m1d24h")
    datetime.datetime(1990, 11, 5, 1, 1, 1)
    >>> apply_delta(base, "+5M")
    datetime.datetime(2012, 1, 1, 1, 6, 1)
    >>> apply_delta(base, "+4M30s")
    datetime.datetime(2012, 1, 1, 1, 5, 31)

    """

    sign = delta[0]
    delta = delta[1:]
    timedelta_kwargs = {}

    # re.split returns empty strings if the capturing groups matches the
    # start and the end of string.
    for part in filter(lambda p: p, re.split(r"(\d+\w)", delta)):
        amount, unit = re.findall(r"(\d+)([ymdhMs])", part)[0]

        operators = {"+": operator.add,
                     "-": operator.sub}
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

    dt = operators[sign](dt, delta)

    return dt


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
        add = int(reduce(operator.add, itertools.starmap(operator.mul, days)))
        kwargs["days"] = kwargs.setdefault("days", 0) + add

    return datetime.timedelta(**kwargs)


def datetime_to_epoch_timestamp(a_datetime):
    """Return the epoch timestamp for the given datetime

    :param datetime a_datetime: The datetime to translate
    :rtype: float

    >>> a_datetime = datetime.datetime(2013, 11, 21, 1, 33, 11, 160611)
    >>> datetime_to_epoch_timestamp(a_datetime)
    1384997591.160611
    """

    return (
        calendar.timegm(a_datetime.utctimetuple())
        + a_datetime.microsecond / 1000000.0
    )


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
