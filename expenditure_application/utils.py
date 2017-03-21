# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division

import calendar

import pytz
from datetime import datetime

DEFAULT_CLIENT_TIMEZONE = pytz.timezone('Asia/Shanghai')


def convert_timestamp_to_utc_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, pytz.utc)


def convert_datetime_to_client_timezone(dt, tzinfo=DEFAULT_CLIENT_TIMEZONE):
    if is_naive_datetime(dt):
        return convert_naive_datetime_to_aware(dt, tzinfo)
    else:
        return convert_aware_datetime_to_timezone(dt, tzinfo)


def convert_naive_datetime_to_aware(dt, tzinfo=DEFAULT_CLIENT_TIMEZONE):
    assert is_naive_datetime(dt)
    if hasattr(tzinfo, 'localize'):  # pytz
        converted = tzinfo.localize(dt)
    else:
        converted = dt.replace(tzinfo=tzinfo)
    return converted


def convert_aware_datetime_to_timezone(dt, tzinfo):
    assert not is_naive_datetime(dt)
    if dt.tzinfo is tzinfo:
        return dt
    converted = dt.astimezone(tzinfo)
    if hasattr(tzinfo, 'normalize'):  # pytz
        converted = tzinfo.normalize(converted)
    return converted


def is_naive_datetime(dt):
    return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None


def get_current_timestamp():
    """
    Caveat: the guaranteed precision of timestamp is 1 second
    """
    return calendar.timegm(datetime.now(pytz.utc).utctimetuple())
