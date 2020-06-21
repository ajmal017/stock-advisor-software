"""Author: Mark Hanegraaff -- 2020
    Testing class for the support.util module
"""

import unittest
from unittest.mock import patch
import pandas as pd
from datetime import datetime
from exception.exceptions import ValidationError
from support import util


class TestSupportUtil(unittest.TestCase):
    """Author: Mark Hanegraaff -- 2020
        Testing class for the support.util module
    """

    '''
        Date coversion util
    '''

    def test_date_to_iso_string_with_error(self):
        with self.assertRaises(ValidationError):
            util.date_to_iso_string("not a date")

    def test_date_to_iso_string_none(self):
        self.assertEqual(util.date_to_iso_string(None), "None")

    def test_datetime_to_iso_utc_string_with_error(self):
        with self.assertRaises(ValidationError):
            util.datetime_to_iso_utc_string("not a date")

    def test_datetime_to_iso_utc_string_none(self):
        self.assertEqual(util.datetime_to_iso_utc_string(None), "None")

    '''
        get_business_date test cases
    '''

    def test_get_business_date_before_market_open(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T06:00:00+0000')):

            self.assertEqual(util.get_business_date(
                0, 0), datetime(2020, 6, 9))

    def test_get_business_date_during_market_hours(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T15:00:00+0000')):

            self.assertEqual(util.get_business_date(
                0, 0), datetime(2020, 6, 9))

    def test_get_business_date_after_market_close(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            self.assertEqual(util.get_business_date(
                0, 0), datetime(2020, 6, 10))

    def test_get_business_date_with_hours_offset(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            self.assertEqual(util.get_business_date(
                0, 2), datetime(2020, 6, 10))

    def test_get_business_date_with_days_offset(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            self.assertEqual(util.get_business_date(
                3, 0), datetime(2020, 6, 5))

    def test_get_business_date_with_huge_days_offset(self):
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            with self.assertRaises(ValidationError):
                util.get_business_date(100, 0)
