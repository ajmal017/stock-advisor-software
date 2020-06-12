"""Author: Mark Hanegraaff -- 2020

Testing class for the strategies.macd_crossover_strategy module
"""
import unittest
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from connectors import intrinio_data
from datetime import datetime
from support import constants
from exception.exceptions import ValidationError, DataError
from strategies.macd_crossover_strategy import MACDCrossoverStrategy


class TestStrategiesMACDCrossover(unittest.TestCase):
    """
        Testing class for the strategies.macd_crossover_strategy module
    """

    '''
        Constructor Tests
    '''

    def test_init_no_config(self):
        with patch('support.constants.CONFIG_FILE_PATH', "./config/does_not_exist.ini"):
            ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

            with self.assertRaises(ValidationError):
                MACDCrossoverStrategy(ticker_file_path)

    def test_init_empty_config(self):
        with patch('support.constants.CONFIG_FILE_PATH', "./test/config-unittest-bad/empty-test-config.ini"):
            ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

            with self.assertRaises(ValidationError):
                MACDCrossoverStrategy(ticker_file_path)

    def test_init_incorrect_config(self):
        with patch('support.constants.CONFIG_FILE_PATH', "./test/config-unittest-bad/bad-test-config.ini"):
            ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR

            with self.assertRaises(ValidationError):
                MACDCrossoverStrategy(ticker_file_path)
