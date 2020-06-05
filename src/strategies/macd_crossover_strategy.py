"""Author: Mark Hanegraaff -- 2020
"""

import logging
from datetime import datetime
from support import logging_definition, util
from strategies.base_strategy import BaseStrategy
from model.recommendation_set import SecurityRecommendationSet
from model.ticker_list import TickerList

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



    def generate_recommendation(self):
        '''
            TBD
        '''

        for symbol in self.ticker_list.ticker_symbols:
            log.info(symbol)

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
