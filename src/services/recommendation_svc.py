"""Author: Mark Hanegraaff -- 2020

This module contains supporting logic for reccomendation service script.
It exists solely so that the code may be tested. otherwise it would
be organized along with the service itself.
"""
import logging
from connectors import aws_service_wrapper
from support import constants

log = logging.getLogger()


def notify_new_recommendation(recommendation_set: object, app_ns: str):
    '''
        Sends an SNS notification indicating that a new recommendation has been generated

        Parameters
        ----------
        recommendation_set: object
            the SecurityRecommendationSet object repr
        app_ns: str
            The application namespace supplied to the command line
            used to identify the appropriate CloudFormation exports
    '''

    recommnedation_month = parser.parse(
        recommendation_set.model['valid_to'])

    formatted_ticker_message = ""
    for security in recommendation_set.model['securities_set']:
        formatted_ticker_message += "Ticker Symbol: %s\n" % security[
            'ticker_symbol']

    sns_topic_arn = aws_service_wrapper.cf_read_export_value(
        constants.sns_app_notifications_topic_arn(app_ns))
    subject = "New Stock Recommendation Available"
    message = "A New Stock Recommendation is available for the month of %s\n" % recommnedation_month.strftime(
        "%B, %Y")
    message += "\n\n"
    message += formatted_ticker_message

    log.info("Publishing Recommendation set to SNS topic: %s" %
             sns_topic_arn)
    aws_service_wrapper.sns_publish_notification(
        sns_topic_arn, subject, message)
