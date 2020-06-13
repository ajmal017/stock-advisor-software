"""Author: Mark Hanegraaff -- 2020

Testing class for the strategies.macd_crossover_strategy module
"""
import unittest
from unittest.mock import patch
from datetime import datetime
from support import constants
import pandas as pd
from exception.exceptions import ValidationError
from strategies.macd_crossover_strategy import MACDCrossoverStrategy
from connectors import intrinio_data


class TestStrategiesMACDCrossover(unittest.TestCase):
    """
        Testing class for the strategies.macd_crossover_strategy module
    """

    '''
        Constructor Tests
    '''

    def test_init_no_config(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch('support.constants.CONFIG_FILE_PATH', "./config/does_not_exist.ini"):
            with self.assertRaises(ValidationError):
                MACDCrossoverStrategy(ticker_file_path)

    def test_init_empty_config(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch('support.constants.CONFIG_FILE_PATH', "./test/config-unittest-bad/empty-test-config.ini"):
            with self.assertRaises(ValidationError):
                MACDCrossoverStrategy(ticker_file_path)

    def test_init_incorrect_config(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch('support.constants.CONFIG_FILE_PATH', "./test/config-unittest-bad/bad-test-config.ini"):
            with self.assertRaises(ValidationError):
                MACDCrossoverStrategy(ticker_file_path)

    '''
        _get_business_date tests
    '''

    def test_get_business_date_before_market_open(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T06:00:00+0000')):

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

            self.assertEqual(macd_strategy._get_business_date(
                0, 0), datetime(2020, 6, 9))

    def test_get_business_date_during_market_hours(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T15:00:00+0000')):

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

            self.assertEqual(macd_strategy._get_business_date(
                0, 0), datetime(2020, 6, 9))

    def test_get_business_date_after_market_close(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

            self.assertEqual(macd_strategy._get_business_date(
                0, 0), datetime(2020, 6, 10))

    def test_get_business_date_with_hours_offset(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

            self.assertEqual(macd_strategy._get_business_date(
                0, 2), datetime(2020, 6, 10))

    def test_get_business_date_with_days_offset(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

            self.assertEqual(macd_strategy._get_business_date(
                3, 0), datetime(2020, 6, 5))

    def test_get_business_date_with_huge_days_offset(self):
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        with patch.object(pd.Timestamp, 'utcnow',
                          return_value=pd.Timestamp('2020-06-10T23:00:00+0000')):

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

            with self.assertRaises(ValidationError):
                macd_strategy._get_business_date(100, 0)

    '''
        _analyze_security tests
    '''

    def test_analyze_security_1(self):
        '''
            Current price above SMA
            MACD Above Signal line
        '''
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

        macd_strategy = MACDCrossoverStrategy(
            ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

        current_price = 100
        sma_list = [97, 99, 98]
        macd_lines = [10, 10, 10]
        signal_lines = [9, 9, 9]

        self.assertTrue(macd_strategy._analyze_security(
            current_price, sma_list, macd_lines, signal_lines))


    def test_analyze_security_2(self):
        '''
            Current price below SMA
            MACD Above Signal line
        '''
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

        macd_strategy = MACDCrossoverStrategy(
            ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

        current_price = 80
        sma_list = [97, 99, 98]
        macd_lines = [10, 10, 10]
        signal_lines = [9, 9, 9]

        self.assertFalse(macd_strategy._analyze_security(
            current_price, sma_list, macd_lines, signal_lines))

    def test_analyze_security_3(self):
        '''
            Current price above SMA
            MACD Above below Signal line (consistently)
        '''
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

        macd_strategy = MACDCrossoverStrategy(
            ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

        current_price = 100
        sma_list = [97, 99, 98]
        macd_lines = [9, 9, 9]
        signal_lines = [10, 10, 10]

        self.assertFalse(macd_strategy._analyze_security(
            current_price, sma_list, macd_lines, signal_lines))


    def test_analyze_security_4(self):
        '''
            Current price above SMA
            MACD dips below signal line beyond what the threshold allows
        '''
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

        macd_strategy = MACDCrossoverStrategy(
            ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

        current_price = 100
        sma_list = [97, 99, 98]
        macd_lines = [9, 11, 9]
        signal_lines = [10, 10, 10]

        self.assertFalse(macd_strategy._analyze_security(
            current_price, sma_list, macd_lines, signal_lines))

    def test_analyze_security_5(self):
        '''
            Current price above SMA
            MACD dips below signal within threshold for one day
        '''
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

        macd_strategy = MACDCrossoverStrategy(
            ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

        current_price = 100
        sma_list = [97, 99, 98]
        macd_lines = [8, 11, 8]
        signal_lines = [8.5, 10, 9]

        self.assertTrue(macd_strategy._analyze_security(
            current_price, sma_list, macd_lines, signal_lines))

    def test_analyze_security_6(self):
        '''
            Current price above SMA
            MACD dips below signal within threshold for 3 days
        '''
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

        macd_strategy = MACDCrossoverStrategy(
            ticker_file_path, (datetime(2020, 6, 10), 50, 12, 26, 9))

        current_price = 100
        sma_list = [97, 99, 98]
        macd_lines = [8, 8, 8]
        signal_lines = [8.5, 8.6, 8.7]

        self.assertFalse(macd_strategy._analyze_security(
            current_price, sma_list, macd_lines, signal_lines))

    '''
        _read_price_metrics tests
    '''

    def test_read_price_metrics(self):
        with patch.object(intrinio_data, 'get_daily_stock_close_prices',
            return_value={
            "2020-06-08": 54.74
        }), \
        patch.object(intrinio_data, 'get_sma_indicator',
            return_value={
            "2020-06-08": 43.80299999999999,
            "2020-06-05": 43.48459999999999,
            "2020-06-04": 43.16879999999999,
            "2020-06-03": 42.895599999999995,
            "2020-06-02": 42.53980000000001,
            "2020-06-01": 42.248400000000004
        }), \
        patch.object(intrinio_data, 'get_macd_indicator',
            return_value={
            "2020-06-08": {
                "macd_histogram": 0.9111766583116911,
                "macd_line": 2.085415403516656,
                "signal_line": 1.1742387452049647
            },
            "2020-06-05": {
                "macd_histogram": 0.6835851903469985,
                "macd_line": 1.6300297709740406,
                "signal_line": 0.9464445806270421
            },
            "2020-06-04": {
                "macd_histogram": 0.41855248391063227,
                "macd_line": 1.1941007669509247,
                "signal_line": 0.7755482830402924
            },
            "2020-06-03": {
                "macd_histogram": 0.35465430132495446,
                "macd_line": 1.0255644633875889,
                "signal_line": 0.6709101620626344
            },
            "2020-06-02": {
                "macd_histogram": 0.1990324206406321,
                "macd_line": 0.7812790073720279,
                "signal_line": 0.5822465867313958
            },
            "2020-06-01": {
                "macd_histogram": 0.12213848547005757,
                "macd_line": 0.6546269670412954,
                "signal_line": 0.5324884815712378
            }
        }):

            ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 8), 50, 12, 26, 9))

            (current_price, sma_list, macd_lines, signal_lines) = macd_strategy._read_price_metrics('AAPL')

            self.assertEqual(current_price, 54.74)
            self.assertListEqual(sma_list, [43.80299999999999, 43.48459999999999, 43.16879999999999])
            self.assertListEqual(macd_lines, [2.085415403516656, 1.6300297709740406, 1.1941007669509247])
            self.assertListEqual(signal_lines, [1.1742387452049647, 0.9464445806270421, 0.7755482830402924])

    
    def test_read_price_metrics(self):
        with patch.object(intrinio_data, 'get_daily_stock_close_prices',
            return_value={
            "2020-06-08": 54.74
        }), \
        patch.object(intrinio_data, 'get_sma_indicator',
            return_value={
            "2020-06-08": 43.80299999999999
        }), \
        patch.object(intrinio_data, 'get_macd_indicator',
            return_value={
            "2020-06-08": {
                "macd_histogram": 0.9111766583116911,
                "macd_line": 2.085415403516656,
                "signal_line": 1.1742387452049647
            }
        }):

            ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

            macd_strategy = MACDCrossoverStrategy(
                ticker_file_path, (datetime(2020, 6, 8), 50, 12, 26, 9))

            with self.assertRaises(ValidationError):
                macd_strategy._read_price_metrics('AAPL')