"""Author: Mark Hanegraaff -- 2020
    Testing class for the services.recommendation_svc module
"""
import unittest
from unittest.mock import patch
from datetime import datetime
from exception.exceptions import ValidationError, AWSError
from services import recommendation_svc
from connectors import aws_service_wrapper
from model.recommendation_set import SecurityRecommendationSet
from support import constants


class TestServicesRecommendation(unittest.TestCase):

    """
        Testing class for the services.recommendation_svc module
    """

    
    '''
        sns publishing tests
    '''

    def test_notify_new_recommendation_with_boto_error(self):
        with patch.object(aws_service_wrapper, 'cf_read_export_value',
                          return_value="some_sns_arn"), \
            patch.object(aws_service_wrapper, 'sns_publish_notification',
                         side_effect=AWSError("test exception", None)):

            with self.assertRaises(AWSError):
                security_recommendation = SecurityRecommendationSet.from_parameters(datetime.now(), datetime.now(
                ), datetime.now(), datetime.now(), 'STRATEGY_NAME', 'US Equities', {'AAPL': 100})

                recommendation_svc.notify_new_recommendation(
                    security_recommendation, 'sa')
