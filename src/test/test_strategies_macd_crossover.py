"""Author: Mark Hanegraaff -- 2020

Testing class for the strategies.macd_crossover_strategy module
"""
import unittest
from unittest.mock import patch
from intrinio_sdk.rest import ApiException
from connectors import intrinio_data
from datetime import datetime
from exception.exceptions import ValidationError, DataError
from strategies.price_dispersion_strategy import PriceDispersionStrategy


class TestStrategiesMACDCrossover(unittest.TestCase):
    """
        Testing class for the strategies.macd_crossover_strategy module
    """

    pass
