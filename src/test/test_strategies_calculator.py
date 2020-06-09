"""Author: Mark Hanegraaff -- 2020
    Testing class for the strategies.calculator module
"""
import unittest
from unittest.mock import patch
from datetime import datetime
import pandas as pd
from connectors import intrinio_data
from exception.exceptions import CalculationError, ValidationError, DataError
from strategies import calculator


class TestStrategiesCalculator(unittest.TestCase):

    """
        Testing class for the strategies.calculator module
    """

    def test_mark_to_market_null_parameters(self):
        df_dict = {
            'ticker': ['a', 'b', 'c', 'd'],
            'analysis_price': [1, 2, 3, 4]
        }
        data_frame = pd.DataFrame(df_dict)
        with self.assertRaises(ValidationError):
            calculator.mark_to_market(data_frame, 'ticker', 'analysis_price', None)
            calculator.mark_to_market(None, 'ticker', 'analysis_price', datetime.now())

    def test_mark_to_market_df_invalid_columns(self):
        df_dict = {
            'a': ['a', 'b', 'c', 'd'],
            'b': [1, 2, 3, 4]
        }
        data_frame = pd.DataFrame(df_dict)
        with self.assertRaises(ValidationError):
            calculator.mark_to_market(data_frame, 'ticker', 'analysis_price', datetime.now())

    def test_mark_to_market_valid(self):
        df_dict = {
            'ticker': ['a'],
            'analysis_price': [10]
        }
        data_frame = pd.DataFrame(df_dict)
        with patch.object(intrinio_data, 'get_latest_close_price',
                          return_value=(datetime.now(), 20)):

            mmt_df = calculator.mark_to_market(data_frame, 'ticker', 'analysis_price', datetime.now())

            self.assertEqual(mmt_df['current_price'][0], 20)
            self.assertEqual(mmt_df['actual_return'][0], 1.0)

    def test_mark_to_market_price_exception(self):
        df_dict = {
            'ticker': ['a'],
            'analysis_price': [10]
        }
        data_frame = pd.DataFrame(df_dict)
        with patch.object(intrinio_data, 'get_latest_close_price',
                          side_effect=Exception("Not Found")):
            with self.assertRaises(DataError):
                calculator.mark_to_market(data_frame, 'ticker', 'analysis_price', datetime.now())
