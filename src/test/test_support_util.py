"""Author: Mark Hanegraaff -- 2020
    Testing class for the support.util module
"""

import unittest
from unittest.mock import patch
import pandas as pd
from datetime import datetime, time, date, timezone
from exception.exceptions import ValidationError
from support import util


class TestSupportUtil(unittest.TestCase):
    """Author: Mark Hanegraaff -- 2020
        Testing class for the support.util module
    """

    '''
        get_business_date test cases
    '''

    def test_get_business_date_before_market_open(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T06:00:00+0000')):

            self.assertEqual(util.get_business_date(
                0, time(17, 0, 0)), date(2020, 6, 9))

    def test_get_business_date_during_market_hours(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T15:00:00+0000')):

            self.assertEqual(util.get_business_date(
                0, time(17, 0, 0)), date(2020, 6, 9))

    def test_get_business_date_after_market_close(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            self.assertEqual(util.get_business_date(
                0, time(17, 0, 0)), date(2020, 6, 10))

    def test_get_business_date_with_days_offset(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            self.assertEqual(util.get_business_date(
                -3, time(17, 0, 0)), date(2020, 6, 5))

    def test_get_business_date_with_huge_days_offset(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            self.assertEqual(util.get_business_date(
                100, time(17, 0, 0)), date(2020, 9, 18))

    '''
        datetime_to_iso_utc_string tests
    '''
    def test_datetime_to_iso_utc_string_valid(self):
        self.assertEqual(util.datetime_to_iso_utc_string(
            datetime(2020, 6, 19, 1, 2, 3, tzinfo=timezone.utc)), "2020-06-19T01:02:03+00:00"
        )

    def test_datetime_to_iso_utc_string_none(self):
        self.assertEqual(util.datetime_to_iso_utc_string(
            None), "None"
        )

    def test_datetime_to_iso_utc_string_invalid(self):
        with self.assertRaises(ValidationError):
            util.datetime_to_iso_utc_string(date(2020, 6, 19))
        