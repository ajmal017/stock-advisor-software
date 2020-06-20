"""Author: Mark Hanegraaff -- 2020
"""
import json
from datetime import datetime
import pytz
import os
import pandas as pd
from datetime import datetime, timedelta
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


def date_to_iso_string(date: datetime):
    '''
        Converts a date object into an 8601 string usin local timezone
    '''
    if date is None:
        return "None"

    try:
        return date.astimezone().isoformat()
    except Exception as e:
        raise ValidationError("Could not convert date to string", e)


def date_to_iso_utc_string(date: datetime):
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


def get_business_date(days_offset: int, hours_offset: int):
    '''
        Retuns the latest market 'closed' date used
        to retrieve the latest EOD data. The offsets are used 
        to adjust the results when EOD data is on a delay

        e.g. days_offet = 0
            2020/06/10 10:00PM --> June 10th 
            2020/06/10 11:00AM --> June 9th 

        e.g. days_offet = 2
            2020/06/10 10:00PM --> June 8th 
            2020/06/10 11:00AM --> June 5th 

        Parameters
        ----------
        days_offset: int
            the number of days to offset the result
        hours_offset: int
            the number of hours to offset the close time
    '''
    nyse_cal = mcal.get_calendar('NYSE')

    utcnow = pd.Timestamp.utcnow()
    utcnow_with_delta = utcnow - \
        pd.Timedelta(timedelta(days=days_offset, hours=hours_offset))
    market_calendar = nyse_cal.schedule(
        utcnow - timedelta(days=10), utcnow + timedelta(days=10))
    print(market_calendar)
    market_calendar = market_calendar[market_calendar.market_close < (
        utcnow_with_delta)]
    print(market_calendar)

    try:
        return market_calendar.index[-1].to_pydatetime()
    except Exception as e:
        raise ValidationError("Could not retrieve Business Date", e)
