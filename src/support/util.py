"""Author: Mark Hanegraaff -- 2020
"""
import json
from datetime import datetime, date
import pytz
import os
import pandas as pd
from datetime import datetime, timedelta, time
import pandas_market_calendars as mcal
from exception.exceptions import ValidationError, FileSystemError


def create_dir(dirname):
    """
        Creates the report directory if not already present
    """
    try:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    except Exception as e:
        raise FileSystemError("Can't create directory: %s" % dirname, e)


def format_dict(dict_string: dict):
    """
        formats a dictionary so that it can be printed to console

        Parameters
        ------------
        dict_string : dictionary to be formatted

    """
    return json.dumps(dict_string, indent=4)


def datetime_to_iso_utc_string(date: datetime):
    '''
        Converts a date object into an 8601 string using UTC
    '''
    if date is None:
        return "None"

    try:
        return date.astimezone(pytz.UTC).isoformat()
    except Exception as e:
        raise ValidationError("Could not convert date to string", e)


def trunc(date: datetime):
    '''
        truncates a date object and removes the time component
    '''
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def get_business_date(days_offset: int, cutover_time: time):
    '''
        Returs the current business by comparing the current date with the
        'NYSE' market calendar. The cutover time is used to determine the time
        in the day when the business date will cutover.

        For example if today is "06/19/2020 13:00:00" and the cutover time 
        is "17:00:00" it will return a value of "06/18/2020"

        Parameters
        ----------
        days_offset: int
            The number of days of offset the results. E.g. 0 will
            return the current date and 1 will return the next, and
            -1 will return the previous.
        cutover_time: time
            the business date cutover time.

    '''
    nyse_cal = mcal.get_calendar('NYSE')

    days_offset *= -1

    utcnow = pd.Timestamp.utcnow()
    utcnow_with_delta = utcnow - \
        pd.Timedelta(timedelta(days=days_offset))
    market_calendar = nyse_cal.schedule(
        utcnow_with_delta - timedelta(days=10), utcnow_with_delta + timedelta(days=10))

    market_calendar['market_close'] = market_calendar['market_close'].map(lambda d: pd.Timestamp(d.year, d.month,
                                                                                                 d.day, cutover_time.hour, cutover_time.minute, cutover_time.second).tz_localize('UTC'))
    market_calendar = market_calendar[market_calendar.market_close < (
        utcnow_with_delta)]

    try:
        return market_calendar.index[-1].to_pydatetime().date()
    except Exception as e:
        raise ValidationError("Could not retrieve Business Date", e)
