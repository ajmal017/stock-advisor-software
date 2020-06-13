"""test_script.py

A general purpose test script. Nothing to see here.
"""
import argparse
import logging
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import pandas as pd

from support import logging_definition, util, constants
from connectors import connector_test, intrinio_data
from strategies.macd_crossover_strategy import MACDCrossoverStrategy
from model.ticker_list import TickerList
from support import constants

#
# Main script
#

log = logging.getLogger()


def main():
    '''
        Main testing script
    '''
    try:
        ticker_file_path = "%s/djia30.json" % constants.TICKER_DATA_DIR
        ticker_file = TickerList.from_local_file(ticker_file_path)
        macd_strategy = MACDCrossoverStrategy(ticker_file)
        # macd_strategy = MACDCrossoverStrategy(
        #    ticker_file_path, (datetime(2020, 6, 8), 50, 12, 26, 9))

        macd_strategy.generate_recommendation()
        macd_strategy.display_results()

    except Exception as e:
        log.error("Could run script, because, %s" % (str(e)))

if __name__ == "__main__":
    main()
