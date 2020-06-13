"""Author: Mark Hanegraaff -- 2020
"""
from abc import ABC, abstractmethod
import logging
import configparser
from support import constants
from exception.exceptions import ValidationError
from model.ticker_list import TickerList


class BaseStrategy(ABC):
    '''
        Base class for all trading strategies. Acts as an interface and
        ensures that certain method signatures exist.

        Attributes:
            STRATEGY_NAME: The display name associated with this strategy
            CONFIG_SECTION: The name of the configuration section in
                /config/strategies.ini

    '''

    STRATEGY_NAME = ""
    CONFIG_SECTION = ""

    def __init__(self, ticker_list: TickerList):
        '''
            Defines the recommendation_set variable which must be an instance
            of the SecurityRecommendationSet class

            Parameters
            ----------
            ticker_list: TickerList
                Ticker List object containing securitues to analyze
        '''
        if (ticker_list == None):
            raise ValidationError("No Ticker List was supplied", None)

        self.recommendation_set = None
        self.config = configparser.ConfigParser(allow_no_value=True)

        self.ticker_list = ticker_list

        try:
            self.config_file = open(constants.CONFIG_FILE_PATH)
            self.config.read_file(self.config_file)
        except Exception as e:
            raise ValidationError("Could not load Strategy Configuration", e)

        # make sure the file is not empty. If it is, raise an exception
        if len(self.config.sections()) == 0:
            self.config_file.close()
            raise ValidationError(
                "Strategy Configuration [%s] is empty" % constants.CONFIG_FILE_PATH, None)

    @abstractmethod
    def generate_recommendation(self):
        '''
            Generates a recommendation object and sets the value of the

            self.recommendation_set

            member variable
        '''
        pass

    @abstractmethod
    def display_results(self):
        pass
