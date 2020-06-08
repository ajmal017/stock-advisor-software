"""Author: Mark Hanegraaff -- 2020
"""

import logging
from datetime import datetime, timedelta
from collections import OrderedDict
from support import logging_definition, util
from strategies.base_strategy import BaseStrategy
from model.recommendation_set import SecurityRecommendationSet
from model.ticker_list import TickerList
from exception.exceptions import ValidationError, DataError
from connectors import intrinio_data, intrinio_util

log = logging.getLogger()


class MACDCrossoverStrategy(BaseStrategy):
    '''
        This strategy uses the MACD indicator to detect whether a stock is
        rallying or crashing. A rally is identified when a stock price
        is above the moving average for at least 3 days, and when the macd line
        crosses over the signa like.

        Attributes
        ----------
        MACD_SIGNAL_CROSSOVER_THRESHOLD: int
            a buffer used to prevent stocks from flipping when the macd line
            trends closely with the signal line.
    '''

    STRATEGY_NAME = "MACD_CROSSOVER"
    MACD_SIGNAL_CROSSOVER_THRESHOLD = 1.0

    def __init__(self, ticker_list_path: str, analysis_date: datetime):
        '''
            Defines the recommendation_set variable which must be an instance
            of the SecurityRecommendationSet class
        '''
        super().__init__()

        self.ticker_list = TickerList.from_local_file(ticker_list_path)
        self.analysis_date = analysis_date

    def _read_price_metrics(self, ticker_symbol: str, sma_period: int, macd_fast_period: int, macd_slow_period: int, macd_signal_period: int):
        '''
            TBD
        '''

        lookback_days = 3

        lookback_date = self.analysis_date - timedelta(days=7)

        dict_key = intrinio_util.date_to_string(self.analysis_date)

        current_price_dict = intrinio_data.get_daily_stock_close_prices(
            ticker_symbol, self.analysis_date, self.analysis_date
        )

        # Get last 3 days of the moving average
        sma_dict = intrinio_data.get_sma_indicator(
            ticker_symbol, lookback_date, self.analysis_date, sma_period
        )
        if not dict_key in sma_dict:
            raise DataError("Unable to download Simple moving average for (%s, %s)" % (
                ticker_symbol, dict_key))
        sma_ordered_dict = OrderedDict(sorted(sma_dict.items(), reverse=True))
        sma_list = [sma_ordered_dict.popitem(
            last=False)[1] for _ in range(0, lookback_days)]

        # Get last 3 days of macd and singal values
        macd_dict = intrinio_data.get_macd_indicator(
            ticker_symbol, lookback_date, self.analysis_date, macd_fast_period, macd_slow_period, macd_signal_period
        )

        if not dict_key in macd_dict:
            raise DataError("Unable to download MACD values for (%s, %s)" % (
                ticker_symbol, dict_key))

        macd_line_dict = OrderedDict(
            sorted(macd_dict.items(), reverse=True))
        signal_line_dict = OrderedDict(
            sorted(macd_dict.items(), reverse=True))
        
        try:
            current_price = current_price_dict[dict_key]

            macd_lines = [macd_line_dict.popitem(
                last=False)[1]['macd_line'] for _ in range(0, lookback_days)]
            signal_lines = [signal_line_dict.popitem(
                last=False)[1]['signal_line'] for _ in range(0, lookback_days)]

        except Exception as e:
            raise ValidationError(
                "Could not read pricing data for %s" % ticker_symbol, e)

        return (current_price, sma_list, macd_lines, signal_lines)

    def _analyze_security(self, ticker_symbol: str, current_price: float, sma_list: list, macd_lines: float, signal_lines: float):
        '''
            TBD
        '''

        # Price must have ben above sma for 3 days
        for sma_price in sma_list:
            if current_price < sma_price:
                return False

        latest_macd = macd_lines[0]
        latest_signal = signal_lines[0]

        if (latest_macd > latest_signal):
            return True
        elif latest_macd > (latest_signal - self.MACD_SIGNAL_CROSSOVER_THRESHOLD):
            for i in range(0, len(macd_lines)):
                if macd_lines[i] > signal_lines[i]:
                    return True
        
        return False

    def generate_recommendation(self, sma_period: int, macd_fast_period: int, macd_slow_period: int, macd_signal_period: int):
        '''
            TBD
        '''

        for ticker_symbol in self.ticker_list.ticker_symbols:
            (current_price, sma_list, macd_lines, signal_lines) = self._read_price_metrics(
                ticker_symbol, sma_period, macd_fast_period, macd_slow_period, macd_signal_period)

            buy_sell_indicator = self._analyze_security(
                ticker_symbol, current_price, sma_list, macd_lines, signal_lines)

            log.info("%s: (%.3f, %s, %s, %s) --> %s" % (ticker_symbol, current_price, ["{0:0.2f}".format(i) for i in sma_list], ["{0:0.2f}".format(i) for i in macd_lines], ["{0:0.2f}".format(i) for i in signal_lines],
                                                                  buy_sell_indicator))

        self.recommendation_set = SecurityRecommendationSet.from_parameters(
            datetime.now(), datetime.now(), datetime.now(), datetime.now(), self.STRATEGY_NAME,
            "US_EQUITIES", {
                "AAPL": 100
            }
        )

    def display_results(self):
        '''
            TBD
        '''

        log.info("Displaying results of MACD strategy: %s" %
                 util.format_dict(self.recommendation_set.model))
