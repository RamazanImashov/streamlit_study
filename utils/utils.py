

from datetime import datetime


def format_datetime(value):
    if not isinstance(value, datetime):
        return value
    return value.strftime('%d.%m.%Y %H:%M:%S')
