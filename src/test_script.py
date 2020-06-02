"""test_script.py

A general purpose test script. Nothing to see here.
"""
import argparse
import logging
from datetime import datetime

from support import logging_definition, util
from connectors import connector_test, intrinio_data

#
# Main script
#

log = logging.getLogger()


def main():
    '''
        Main testing script
    '''
    try:
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2020, 5, 29)

        print(util.format_dict(intrinio_data.get_macd_indicator(
            'AAPL', start_date, end_date, 12, 26, 9)))
    except Exception as e:
        log.error("Could run script, because, %s" % (str(e)))

if __name__ == "__main__":
    main()
