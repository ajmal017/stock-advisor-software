"""Author: Mark Hanegraaff -- 2020
"""

import logging
from datetime import datetime
from support import logging_definition, util
from strategies.base_strategy import BaseStrategy
from model.recommendation_set import SecurityRecommendationSet
from model.ticker_list import TickerList
from exception.exceptions import ValidationError
from connectors import intrinio_data, intrinio_util

log = logging.getLogger()


class MACDCrossoverStrategy(BaseStrategy):
    '''
        Describe the MACD Crossover Strategy
    '''

    STRATEGY_NAME = "MACD_CROSSOVER"

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

        dict_key = intrinio_util.date_to_string(self.analysis_date)

        current_price_dict = intrinio_data.get_daily_stock_close_prices(
            ticker_symbol, self.analysis_date, self.analysis_date
        )

        sma_dict = intrinio_data.get_sma_indicator(
            ticker_symbol, self.analysis_date, self.analysis_date, sma_period
        )

        macd_dict = intrinio_data.get_macd_indicator(
            ticker_symbol, self.analysis_date, self.analysis_date, macd_fast_period, macd_slow_period, macd_signal_period
        )

        try:
            current_price = current_price_dict[dict_key]
            sma_price = sma_dict[dict_key]

            macd_line = macd_dict[dict_key]['macd_line']
            signal_line = macd_dict[dict_key]['signal_line']
            macd_histogram = macd_dict[dict_key]['macd_histogram']
        except Exception as e:
            raise ValidationError(
                "Could not read pricing data for %s" % ticker_symbol, e)

        return (current_price, sma_price, macd_line, signal_line, macd_histogram)

    def _analyze_security(self, ticker_symbol: str, current_price: float, sma_price: float, macd_line: float, signal_line: float, macd_histogram: float):
        pass

    def generate_recommendation(self, sma_period: int, macd_fast_period: int, macd_slow_period: int, macd_signal_period: int):
        '''
            TBD
        '''

        for ticker_symbol in self.ticker_list.ticker_symbols:
            (current_price, sma_price, macd_line, signal_line,
             macd_histogram) = self._read_price_metrics(ticker_symbol, sma_period, macd_fast_period, macd_slow_period, macd_signal_period)

            log.info("%s --> (%.3f, %.3f, %.3f, %.3f, %.3f)" % (ticker_symbol, current_price, sma_price, macd_line, signal_line,
                                                                macd_histogram))

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
