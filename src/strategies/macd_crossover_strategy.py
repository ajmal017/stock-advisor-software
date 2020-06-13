"""Author: Mark Hanegraaff -- 2020
"""

import logging
import pandas as pd
import dateutil.parser as parser
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
from collections import OrderedDict
from support import util
from strategies.base_strategy import BaseStrategy
from strategies import calculator
from model.recommendation_set import SecurityRecommendationSet
from exception.exceptions import ValidationError, DataError
from connectors import intrinio_data, intrinio_util

log = logging.getLogger()


class MACDCrossoverStrategy(BaseStrategy):
    '''
        This strategy uses a combination of SMA and MACD indicator to detect whether 
        a stock is rallying or crashing. A rally is identified when a stock price
        is above the moving average, and when the macd line
        crosses over the signal line. When this happens, the security will be
        included in the recommendation set, otherwise it will not.

        Attributes
        ----------
        MACD_SIGNAL_CROSSOVER_FACTOR: float
            A factor used to calculate the threshold to determine when
            the signal has dipped too far below the signal line.
    '''

    STRATEGY_NAME = "MACD_CROSSOVER"
    CONFIG_SECTION = "macd_conversion_strategy"
    MACD_SIGNAL_CROSSOVER_FACTOR = 0.1

    def __init__(self, ticker_list, override_params: tuple=None):
        '''
            Initializes the strategy.

            When running in production only the ticker_list_path must be supplied.
            The analysis date ill be determined at runtime, and strategy parameters 
            will be read from configuration.

            When running a backtest then all parameters, including the analysis
            must be passed in the override_params tuple

            Parameters
            ----------
            ticker_list: TickerList
                Ticker List object containing securitues to analyze
            override_params: tuple
                A tuple containing the all strategy parameters override
                analysis_date: datetime
                    Analysis (price) date
                sma_period: int
                    The Simple Moving average perdiod in days, e.g. 50
                macd_fast_period: int
                    MACD fast moving period in days, e.g. 12
                macd_slow_period: int
                    MACD slow moving period in days, e.g. 24
                macd_signal_period: int
                    MACD signal period in days, e.g. 9
        '''
        super().__init__(ticker_list)

        pd.options.display.float_format = '{:.3f}'.format

        self.raw_dataframe = None

        if override_params == None:
            try:
                config_params = dict(self.config[self.CONFIG_SECTION])

                self.sma_period = int(config_params['sma_period'])
                self.macd_fast_period = int(config_params['macd_fast_period'])
                self.macd_slow_period = int(config_params['macd_slow_period'])
                self.macd_signal_period = int(
                    config_params['macd_signal_period'])
                self.analysis_date = self._get_business_date(4, 0)
            except Exception as e:
                raise ValidationError(
                    "Could not read MACD Crossover Strategy configuration parameters", e)
            finally:
                self.config_file.close()

        else:
            try:
                (analysis_date, sma_period, macd_fast_period,
                 macd_slow_period, macd_signal_period) = override_params
            except Exception as e:
                raise ValidationError(
                    "Could not initialize MACD Crossover Strategy", e)
            finally:
                self.config_file.close()

            self.analysis_date = analysis_date
            self.sma_period = sma_period
            self.macd_fast_period = macd_fast_period
            self.macd_slow_period = macd_slow_period
            self.macd_signal_period = macd_signal_period

    def _get_business_date(self, days_offset: int, hours_offset: int):
        '''
            Retuns the latest market 'closed' date used
            to retrieve the latest EOD data. The offsets are used 
            to adjust the results when EOD data is on a delay

            e.g. days_offet = 0
                2020/06/10 10:00PM --> June 10th 
                2020/06/10 11:00AM --> June 9th 

            e.g. days_offet = 2
                2020/06/10 10:00PM --> June 8th 
                2020/06/10 11:00AM --> June 5th 

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
            pd.Timedelta(timedelta(days=days_offset, hours=hours_offset))
        market_calendar = nyse_cal.schedule(
            utcnow - timedelta(days=10), utcnow + timedelta(days=10))
        market_calendar = market_calendar[market_calendar.market_close < (
            utcnow_with_delta)]

        try:
            return market_calendar.index[-1]
        except Exception as e:
            raise ValidationError("Could not retrieve Business Date", e)

    def _read_price_metrics(self, ticker_symbol: str):
        '''
            Helper function that downloads the necessary data to perfom the MACD Crossover calculation.
            Most data includes a short history to help filter out false signals.

            Returns
            -------
            A Tuple with the following elements:
            current_price: float
                The Current price for the ticker symbol
            sma_list: list
                The part 3 days of Simple Moving average prices
            macd_lines: list
                The past 3 days of MACD values
            signal_lines
                The past 3 days of MACD Singal values

        '''

        lookback_days = 3

        lookback_date = self.analysis_date - timedelta(days=7)

        dict_key = intrinio_util.date_to_string(self.analysis_date)

        current_price_dict = intrinio_data.get_daily_stock_close_prices(
            ticker_symbol, self.analysis_date, self.analysis_date
        )

        # Get last 3 days of the moving average
        sma_dict = intrinio_data.get_sma_indicator(
            ticker_symbol, lookback_date, self.analysis_date, self.sma_period
        )
        if not dict_key in sma_dict:
            raise DataError("Unable to download Simple moving average for (%s, %s)" % (
                ticker_symbol, dict_key))
        sma_ordered_dict = OrderedDict(sorted(sma_dict.items(), reverse=True))

        # Get last 3 days of macd and singal values
        macd_dict = intrinio_data.get_macd_indicator(
            ticker_symbol, lookback_date, self.analysis_date, self.macd_fast_period, self.macd_slow_period, self.macd_signal_period
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

            sma_list = [sma_ordered_dict.popitem(
                last=False)[1] for _ in range(0, lookback_days)]

            macd_lines = [macd_line_dict.popitem(
                last=False)[1]['macd_line'] for _ in range(0, lookback_days)]
            signal_lines = [signal_line_dict.popitem(
                last=False)[1]['signal_line'] for _ in range(0, lookback_days)]

        except Exception as e:
            raise ValidationError(
                "Could not read pricing data for %s" % ticker_symbol, e)

        return (current_price, sma_list, macd_lines, signal_lines)

    def _analyze_security(self, current_price: float, sma_list: list, macd_lines: float, signal_lines: float):
        '''
            Helper function that, based on the analysis data, determines whether
            a positive MACD crossover has occurred or not.

            The basic idea is that the if price is above the SMA, and MACD is above the
            signal the stock is rallying. A rally triggers a buy signal, while a crash
            triggers a sell.

            But identifying crossovers isn't so obvious; sometimes these value trend closely to each other
            and so it may be necessary to look at historical data too.

            To account for that, the method includes a threshold to prevent the buy/sell signal 
            from flipping too frequently when values are close. 

            Specifically before identifying a crash:
            1) Ensure that if current price < SMA it has been so for at least the
                past 3 days.
            2) Ensure that if macd dips below the signal, but it still close to it
                (within a threshold) it has been so for at least the past 3 days

            Returns
            -------
            True if the security is rallying, otherwise False
        '''

        # Price must have ben above sma for 3 days
        for sma_price in sma_list:
            if current_price < sma_price:
                return False

        latest_macd = macd_lines[0]
        latest_signal = signal_lines[0]

        crossover_threshold = abs(
            latest_macd * self.MACD_SIGNAL_CROSSOVER_FACTOR)

        if (latest_macd > latest_signal):
            return True
        elif latest_macd > (latest_signal - crossover_threshold):
            for i in range(0, len(macd_lines)):
                if macd_lines[i] > signal_lines[i]:
                    return True

        return False

    def generate_recommendation(self):
        '''
            Analyzes all securitues supplied in the ticker list and returns a SecurityRecommendationSet
            object containing all stocks with a positive MACD crossover. These are stocks
            that are rallying and have positive momentum behind them.

            internally sets the self.recommendation_set object

        '''

        analysis_data = {
            'ticker_symbol': [],
            'price': [],
            'sma': [],
            'macd': [],
            'signal': [],
            'divergence': [],
            'recommendation': []
        }

        recommended_securities = {}

        for ticker_symbol in self.ticker_list.ticker_symbols:
            (current_price, sma_list, macd_lines, signal_lines) = self._read_price_metrics(
                ticker_symbol)

            buy_sell_indicator = self._analyze_security(
                current_price, sma_list, macd_lines, signal_lines)

            analysis_data['ticker_symbol'].append(ticker_symbol)
            analysis_data['price'].append(current_price)
            analysis_data['sma'].append(sma_list[0])
            analysis_data['macd'].append(macd_lines[0])
            analysis_data['signal'].append(signal_lines[0])
            analysis_data['divergence'].append(macd_lines[0] - signal_lines[0])
            if buy_sell_indicator == True:
                analysis_data['recommendation'].append("BUY")
                recommended_securities[ticker_symbol] = current_price
            else:
                analysis_data['recommendation'].append("SELL")

            # log.info("%s: (%.3f, %s, %s, %s) --> %s" % (ticker_symbol, current_price, ["{0:0.2f}".format(i) for i in sma_list], ["{0:0.2f}".format(i) for i in macd_lines], ["{0:0.2f}".format(i) for i in signal_lines],
            #                                                      buy_sell_indicator))

        self.raw_dataframe = pd.DataFrame(analysis_data)
        self.raw_dataframe = self.raw_dataframe.sort_values(
            ['recommendation', 'divergence'], ascending=(True, False))

        self.recommendation_set = SecurityRecommendationSet.from_parameters(
            datetime.now(), datetime.now(), datetime.now(), datetime.now(), self.STRATEGY_NAME,
            "US_EQUITIES", recommended_securities
        )

    def display_results(self):
        '''
            Display the final recommendation and the intermediate results of the strategy
        '''

        log.info("Displaying results of MACD strategy")
        log.info("Analysis Date: %s" % self.analysis_date.strftime("%Y-%m-%d"))
        log.info("SMA Period: %d, MACD Parameters: (%d, %d, %d)" % (
            self.sma_period, self.macd_fast_period, self.macd_slow_period, self.macd_signal_period))
        print(self.raw_dataframe.to_string(index=False))
        log.info(util.format_dict(self.recommendation_set.model))
