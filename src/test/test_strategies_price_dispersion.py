"""Author: Mark Hanegraaff -- 2020

Testing class for the strategies.price_dispersion module
"""
import unittest
import pandas as pd
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from connectors import intrinio_data
from datetime import datetime
from exception.exceptions import ValidationError, DataError
from strategies.price_dispersion_strategy import PriceDispersionStrategy
from model.ticker_list import TickerList


class TestStrategiesPriceDispersion(unittest.TestCase):
    """
        Testing class for the strategies.price_dispersion module
    """

    def test_init_no_tickers(self):
        with self.assertRaises(ValidationError):
            PriceDispersionStrategy(None, pd.Period('2020-02'), datetime(2020, 6, 10), 3)

    def test_init_empty_ticker_list(self):
        with self.assertRaises(ValidationError):
            PriceDispersionStrategy(TickerList.from_dict(
                {
                    "list_name": "DOW30",
                    "list_type": "US_EQUITIES",
                    "comparison_symbol": "DIA",
                    "ticker_symbols":[]
                }
            ), pd.Period('2020-02'), datetime(2020, 6, 10), 3)

    def test_init_too_few_tickers(self):
        with self.assertRaises(ValidationError):
            PriceDispersionStrategy(TickerList.from_dict(
                {
                    "list_name": "DOW30",
                    "list_type": "US_EQUITIES",
                    "comparison_symbol": "DIA",
                    "ticker_symbols":['AAPL']
                }), pd.Period('2020-02'), datetime(2020, 6, 10), 3)

    def test_init_output_size_too_small(self):
        with self.assertRaises(ValidationError):
            PriceDispersionStrategy(TickerList.from_dict({
                    "list_name": "DOW30",
                    "list_type": "US_EQUITIES",
                    "comparison_symbol": "DIA",
                    "ticker_symbols":['AAPL', 'V']
                    }), pd.Period('2020-02'), datetime(2020, 6, 10), 0)

    def test_init_enough_tickers(self):
        PriceDispersionStrategy(TickerList.from_dict({
                    "list_name": "DOW30",
                    "list_type": "US_EQUITIES",
                    "comparison_symbol": "DIA",
                    "ticker_symbols":['AAPL', 'V']
                }), pd.Period('2020-02'), datetime(2020, 6, 10), 3)

    def test_api_exception(self):
        with patch.object(intrinio_data.COMPANY_API, 'get_company_historical_data',
                          side_effect=ApiException("Not Found")):

            strategy = PriceDispersionStrategy(TickerList.from_dict({
                    "list_name": "DOW30",
                    "list_type": "US_EQUITIES",
                    "comparison_symbol": "DIA",
                    "ticker_symbols":['AAPL', 'V']
                }), pd.Period('2020-02'), datetime(2020, 6, 10), 3)

            with self.assertRaises(DataError):
                strategy._load_financial_data()
