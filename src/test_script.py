"""test_script.py

A general purpose test script. Nothing to see here.
"""
import argparse
import logging
import logging
from datetime import datetime, timedelta
from datetime import date, time
import pandas_market_calendars as mcal
import pandas as pd

from support import logging_definition, util, constants
from connectors import connector_test, intrinio_data
from strategies.macd_crossover_strategy import MACDCrossoverStrategy
from strategies.price_dispersion_strategy import PriceDispersionStrategy
from model.ticker_list import TickerList
from support import constants
from support.configuration import Configuration
from exception.exceptions import ValidationError

#
# Main script
#

log = logging.getLogger()


def get_business_date(days_offset: int, cutover_time: time):
    '''
        Parameters
        ----------
        days_offset: int
            the number of days to offset the result
        hours_offset: int
            the number of hours to offset the close time
    '''
    nyse_cal = mcal.get_calendar('NYSE')

    utcnow = pd.Timestamp.utcnow()
    utcnow_with_delta = utcnow - \
        pd.Timedelta(timedelta(days=days_offset))
    market_calendar = nyse_cal.schedule(
        utcnow - timedelta(days=10 + days_offset), utcnow + timedelta(days=10))

    market_calendar['market_close'] = market_calendar['market_close'].map(lambda d: pd.Timestamp(d.year, d.month, 
            d.day, cutover_time.hour, cutover_time.minute, cutover_time.second).tz_localize('UTC'))
    market_calendar= market_calendar[market_calendar.market_close < (
        utcnow_with_delta)]

    print(market_calendar)

    try:
        return market_calendar.index[-1].to_pydatetime()
    except Exception as e:
        raise ValidationError("Could not retrieve Business Date", e)



def get_valid_date_range(current_date: date, cutover_time: time):
    '''
        given a date (e.g. today), returns the previous and next market close
    '''
    nyse_cal= mcal.get_calendar('NYSE')

    market_calendar= nyse_cal.schedule(
        current_date - timedelta(days=5), current_date + timedelta(days=5))

    valid_from_index=market_calendar.index.get_loc(
        str(current_date), method = 'ffill')
    valid_to_index=market_calendar.index.get_loc(
        str(current_date + timedelta(days=1)), method = 'bfill')

    valid_from=market_calendar.iloc[
        valid_from_index].market_close.to_pydatetime().replace(hour=cutover_time.hour, minute=cutover_time.minute, second=cutover_time.second)
    valid_to = market_calendar.iloc[
        valid_to_index].market_close.to_pydatetime().replace(hour=cutover_time.hour, minute=cutover_time.minute, second=cutover_time.second)

    return (valid_from, valid_to)


def main():
    '''
        Main testing script
    '''
    try:

        '''ticker_list = TickerList.from_local_file(
            "%s/djia30.json" % (constants.APP_DATA_DIR))

        config = Configuration.try_from_s3(
            constants.STRATEGY_CONFIG_FILE_NAME, 'sa')

        macd_strategy = MACDCrossoverStrategy.from_configuration(config, 'sa')
        # macd_strategy = MACDCrossoverStrategy(
        #    ticker_list, datetime(2020, 6, 12), 50, 12, 16, 9)
        macd_strategy.generate_recommendation()
        macd_strategy.display_results()

        pd_strategy = PriceDispersionStrategy.from_configuration(config, 'sa')
        # pd_strategy = PriceDispersionStrategy(
        #    ticker_list, '2020-05', datetime(2020, 6, 12), 3)
        pd_strategy.generate_recommendation()
        pd_strategy.display_results()'''

        (valid_from, valid_to) = get_valid_date_range(date(2020, 6, 19), time(20, 0, 0))
        print(valid_from, valid_to)

        print(get_business_date(0, time(20, 0, 0)))
    except Exception as e:
        log.error("Could run script, because, %s" % (str(e)))
        raise e

if __name__ == "__main__":
    main()
