"""securities_recommendation_svc.py

Securities Recommendation Service Main script.

Complete documentation can be found here:
https://github.com/hanegraaff/stock-advisor-software

"""
import argparse
import logging
import traceback
import pandas as pd
from datetime import datetime, timedelta
from connectors import aws_service_wrapper, connector_test
from exception.exceptions import ValidationError, AWSError
from strategies.price_dispersion_strategy import PriceDispersionStrategy
from strategies.macd_crossover_strategy import MACDCrossoverStrategy
from services import recommendation_svc
from model.recommendation_set import SecurityRecommendationSet
from support import constants, logging_definition
from support.configuration import Configuration


log = logging.getLogger()

logging.getLogger('boto3').setLevel(logging.WARN)
logging.getLogger('botocore').setLevel(logging.WARN)
logging.getLogger('s3transfer').setLevel(logging.WARN)
logging.getLogger('urllib3').setLevel(logging.WARN)


def parse_params():
    """
        Parse command line parameters, performs validation
        and returns a sanitized version of it.

        Returns
        ----------
        A tuple containing the application paramter values
        (environment, ticker_file_name, output_size, month, year, current_price_date, app_ns)
    """

    description = """ Reads a list of US Equity ticker symbols and recommends a subset of them
                  based on the degree of analyst target price agreement,
                  specifically it will select stocks with the lowest agreement and highest
                  predicted return.

                  The input parameters consist of a file with a list of of ticker symbols,
                  and the month and year period for the recommendations.
                  The output is a JSON data structure with the final selection.

                  When running this script in "production" mode, the analysis period
                  is determined at runtime, and the system wil plug into the AWS infrastructure
                  to read inputs and store outputs.
              """
    log.info("Parsing command line parameters")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-app_namespace", help="Application namespace used to identify AWS resources", type=str, required=True)

    args = parser.parse_args()
    app_ns = args.app_namespace

    return app_ns


def main():
    """
        Main function for this script
    """
    try:
        app_ns = parse_params()

        log.info("Parameters:")
        log.info("Application Namespace: %s" % app_ns)

        # test all connectivity upfront, so if there any issues
        # the problem becomes more apparent
        connector_test.test_aws_connectivity()
        connector_test.test_intrinio_connectivity()

        configuration = Configuration.try_from_s3(
            constants.STRATEGY_CONFIG_FILE_NAME, app_ns)

        strategies = [
            PriceDispersionStrategy.from_configuration(configuration, app_ns),
            MACDCrossoverStrategy.from_configuration(configuration, app_ns)
        ]

        for strategy in strategies:
            recommendation_set = None

            try:
                recommendation_set = SecurityRecommendationSet.from_s3(
                    app_ns, strategy.S3_RECOMMENDATION_SET_OBJECT_NAME)
            except AWSError as awe:
                if not awe.resource_not_found():
                    raise awe
                log.info("No recommendation set was found in S3.")

            if recommendation_set == None  \
                    or not recommendation_set.is_current(datetime.now()):

                strategy.generate_recommendation()
                strategy.display_results()

                recommendation_set = strategy.recommendation_set

                recommendation_set.save_to_s3(
                    app_ns, strategy.S3_RECOMMENDATION_SET_OBJECT_NAME)
                recommendation_svc.notify_new_recommendation(
                    recommendation_set, app_ns)
            else:
                log.info(
                    "Recommendation set is still valid. There is nothing to do")
    except Exception as e:
        stack_trace = traceback.format_exc()
        log.error("Could run script, because: %s" % (str(e)))
        log.error(stack_trace)

        aws_service_wrapper.notify_error(e, "Securities Recommendation Service",
                                            stack_trace, app_ns)

if __name__ == "__main__":
    main()
