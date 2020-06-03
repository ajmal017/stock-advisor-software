"""Author: Mark Hanegraaff -- 2020
"""

import logging
from datetime import datetime
from support import logging_definition, util
from strategies.base_strategy import BaseStrategy
from model.recommendation_set import SecurityRecommendationSet

log = logging.getLogger()


class MACDCrossoverStrategy(BaseStrategy):
    '''
        Describe the MACD Crossover Strategy
    '''

    STRATEGY_NAME = "MACD_CROSSOVER"

    def __init__(self):
        '''
            Defines the recommendation_set variable which must be an instance
            of the SecurityRecommendationSet class
        '''
        super().__init__()

    def generate_recommendation(self):
        '''
            TBD
        '''
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

        log.info("Displaying results of MACD strategy: %s" % util.format_dict(self.recommendation_set.model))

