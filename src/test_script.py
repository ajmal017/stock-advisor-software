"""test_script.py

A general purpose test script. Nothing to see here.
"""
import argparse
import logging
from datetime import datetime

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
        macd_strategy = MACDCrossoverStrategy(ticker_file_path, datetime.now())

        macd_strategy.generate_recommendation()
        macd_strategy.display_results()


    except Exception as e:
        log.error("Could run script, because, %s" % (str(e)))
        raise e

if __name__ == "__main__":
    main()
