"""Author: Mark Hanegraaff -- 2020
"""
from abc import ABC, abstractmethod
import logging


class BaseStrategy(ABC):
    '''
        Base class for all trading strategies. Acts as an interface and
        ensures that certain method signatures exist.

        Attributes:
            STRATEGY_NAME: The display name associated with this strategy
            
    '''

    STRATEGY_NAME = ""

    def __init__(self):
        '''
            Defines the recommendation_set variable which must be an instance
            of the SecurityRecommendationSet class
        '''
        self.recommendation_set = None

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

