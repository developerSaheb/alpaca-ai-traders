import re
from datetime import timedelta

from pandas import DataFrame
from src.util import AlpacaUtil, StringUtil, DateUtil
from src.finta_interface import Indicator
import pandas as pd
import pandas_datareader as pdr
# import pandas_ta as ta
from src.util.FileUtil import FileUtil as fu
from src.util import Cacher

# The idea here is to be able to switch between Polygon and Yahoo ( and whateveelse )
# with a BaseDataFetcher that defines the abstract methods to complete
# as well as the pandas.DataFrame format for ohlcv
# {
# 'timestamp',
# 'open',
# 'high',
# 'low',
# 'close',
# 'volume'
# }
IS_VERBOSE = False


class BaseDataFetcher(Cacher):

    def __init__(self):
        super().__init__()
        self.start_date = None
        self.end_date = None

    def get_aggs(self, ticker: str, start_date: str, end_date: str, timespan: str = 'day') -> DataFrame:
        h = self.create_hash(ticker, start_date, end_date, timespan)
        df = self.get_cache(h)
        return df

    # Get todays OHLC for the ticker at a given moment when the market is open
    # Adjust the dataframe to look like historic_agg
    def get_snapshot(self, ticker) -> DataFrame:
        raise NotImplementedError

    def _prefetch(self, ticker):
        for day in DateUtil.date_range(self.start_date, self.end_date):
            start = day.date()
            end = (day + timedelta(1)).date()
            h = self.create_hash(ticker, day, day + timedelta(1), self.timespan)

            aggs = self.get_aggs(ticker=ticker,
                                 start_date=start,
                                 end_date=end,
                                 timespan=self.timespan)
            self.memory_cache[h] = aggs


class DataFactory(Cacher):

    @staticmethod
    def set_verbose(b):
        global IS_VERBOSE
        IS_VERBOSE = b

    @staticmethod
    def get_nasdaq():
        return pdr.get_nasdaq_symbols(5, 10)

    # Or https://us.spdrs.com/site-content/xls/SPY_All_Holdings.xls?fund=SPY&docname=All+Holdings&onyx_code1=&onyx_code2=
    @staticmethod
    def get_snp500():
        Cacher.make_dirs()
        h = Cacher.create_hash('snp500')
        c = Cacher.static_get_cache(h)
        if c is not None:
            if IS_VERBOSE:
                print('cached(get_snp500)')
            return c['Symbol'].values
        else:
            if IS_VERBOSE:
                print('fetching(get_snp500)')
            data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            table = data[0]
            Cacher.set_cache(h, table)
            return table['Symbol'].values

    @staticmethod
    def get_nasdaq100():
        global IS_VERBOSE
        Cacher.make_dirs()
        h = Cacher.create_hash('nasdaq100')
        c = Cacher.static_get_cache(h)
        if c is not None:
            if IS_VERBOSE:
                print('cached(get_nasdaq100)')
            return c['Ticker'].values
        else:
            if IS_VERBOSE:
                print('fetching(get_nasdaq100)')
            data = pd.read_html('https://en.wikipedia.org/wiki/NASDAQ-100#Components')
            table = data[2]
            Cacher.set_cache(h, table)
            return table['Ticker'].values

    @staticmethod
    def get_data_fetcher(_type: str = 'polygon') -> BaseDataFetcher:
        if _type == 'polygon':
            return PolygonDataFetcher()
        elif _type == 'yahoo':
            return YahooDataFetcher()

    @staticmethod
    def add_indicators(df: DataFrame,
                       macd_fast: int = 9, macd_slow: int = 21,
                       indicators_to_include: list = ['macd'],
                       verbose=False) -> DataFrame:

        res = Indicator.get_macd(df, macd_fast, macd_slow)
        df['macd'] = res['MACD']
        df['macd_signal'] = res['SIGNAL']
        #print('results')
        #print(df)
        return df
        # old_columns = list(df.columns)
        # new_columns = []
        # if verbose:
        #     for c in indicators_to_include:
        #         print(
        #             'From a python console, type help(df.ta.{}) to get more info on this indicator.  To access. use df[\'{}\'] to access its value '.format(
        #                 c, c))
        #
        # if 'atr' in indicators_to_include:
        #     df.ta.atr(append=True)
        #     new_columns.append('atr')
        # if 'adx' in indicators_to_include:
        #     df.ta.adx(append=True)
        #     new_columns.append('adx')
        #     new_columns.append('dmp_14')
        #     new_columns.append('dmn_14')
        # if 'ao' in indicators_to_include:
        #     df.ta.ao(append=True)
        #     new_columns.append('ao')
        # if 'bop' in indicators_to_include:
        #     df.ta.bop(append=True)
        #     new_columns.append('bop')
        # if 'cci' in indicators_to_include:
        #     df.ta.cci(append=True)
        #     new_columns.append('cci')
        # if 'cmf' in indicators_to_include:
        #     df.ta.cmf(append=True)
        #     new_columns.append('cmf')
        # if 'decreasing' in indicators_to_include:
        #     df.ta.decreasing(append=True)
        #     new_columns.append('decreasing')
        # if 'dema' in indicators_to_include:
        #     df.ta.dema(append=True)
        #     new_columns.append('dema')
        # if 'ema' in indicators_to_include:
        #     if len(df) > macd_fast:
        #         df.ta.ema(length=macd_fast, append=True)
        #         new_columns.append('ema_fast')
        #     if len(df) > macd_slow:
        #         df.ta.ema(length=macd_slow, append=True)
        #         new_columns.append('ema_slow')
        # if 'cross' in indicators_to_include:
        #     df.ta.cross('EMA_{}'.format(macd_fast), 'EMA_{}'.format(macd_slow), append=True)
        #     new_columns.append('ema_cross')
        # if 'efi' in indicators_to_include:
        #     df.ta.efi(append=True)
        #     new_columns.append('efi')
        # if 'fisher' in indicators_to_include:
        #     df.ta.fisher(append=True)
        #     new_columns.append('fisher')
        # if 'increasing' in indicators_to_include:
        #     df.ta.increasing(append=True)
        #     new_columns.append('increasing')
        # if 'hma' in indicators_to_include:
        #     df.ta.hma(append=True)
        #     new_columns.append('hma')
        # if 'kama' in indicators_to_include:
        #     df.ta.kama(append=True)
        #     new_columns.append('kma')
        # if 'log_return' in indicators_to_include:
        #     df.ta.log_return(append=True)
        #     new_columns.append('log_return')
        # if 'macd' in indicators_to_include:
        #     df.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal, min_periods=None, append=True)
        #     new_columns.append('macd_fast')
        #     new_columns.append('macd_slow')
        #     new_columns.append('macd_signal')
        # if 'mad' in indicators_to_include:
        #     df.ta.mad(length=macd_fast, append=True)
        #     new_columns.append('mad_fast')
        #     df.ta.mad(length=macd_slow, append=True)
        #     new_columns.append('mad_slow')
        # if 'mfi' in indicators_to_include:
        #     df.ta.mfi(append=True)
        #     new_columns.append('mfi')
        # if 'mom' in indicators_to_include:
        #     df.ta.mom(append=True)
        #     new_columns.append('mom')
        # if 'natr' in indicators_to_include:
        #     df.ta.natr(append=True)
        #     new_columns.append('natr')
        # if 'nvi' in indicators_to_include:
        #     df.ta.nvi(append=True)
        #     new_columns.append('nvi')
        # if 'pvi' in indicators_to_include:
        #     df.ta.pvi(append=True)
        #     new_columns.append('pvi')
        # if 'pvt' in indicators_to_include:
        #     df.ta.pvt(append=True)
        #     new_columns.append('pvt')
        # if 'qstick' in indicators_to_include:
        #     df.ta.qstick(append=True)
        #     new_columns.append('qstick')
        # if 'roc' in indicators_to_include:
        #     df.ta.roc(length=macd_fast, append=True)
        #     new_columns.append('roc_fast')
        #     df.ta.roc(length=macd_slow, append=True)
        #     new_columns.append('roc_slow')
        # if 'rsi' in indicators_to_include:
        #     df.ta.rsi(append=True)
        #     new_columns.append('rsi')
        # if 'rvi' in indicators_to_include:
        #     df.ta.rvi(append=True)
        #     new_columns.append('rvi')
        #     new_columns.append('rvi_s')
        # if 'skew' in indicators_to_include:
        #     df.ta.skew(length=macd_fast, append=True)
        #     new_columns.append('skew_fast')
        #     df.ta.skew(length=macd_slow, append=True)
        #     new_columns.append('skew_slow')
        # if 'slope' in indicators_to_include:
        #     df.ta.slope(append=True)
        #     new_columns.append('slope')
        # if 'stdev' in indicators_to_include:
        #     df.ta.stdev(length=macd_fast, append=True)
        #     new_columns.append('stdev_fast')
        #     df.ta.stdev(length=macd_slow, append=True)
        #     new_columns.append('stdev_slow')
        # if 'stoch' in indicators_to_include:
        #     df.ta.stoch(append=True)
        #     new_columns.append('stockf_14')
        #     new_columns.append('stochf_3')
        #     new_columns.append('stoch_5')
        #     new_columns.append('stoch_3')
        # if 't3' in indicators_to_include:
        #     df.ta.t3(append=True)
        #     new_columns.append('t3')
        # if 'trix' in indicators_to_include:
        #     df.ta.trix(append=True)
        #     new_columns.append('trix')
        # if 'true_range' in indicators_to_include:
        #     df.ta.true_range(append=True)
        #     new_columns.append('true_range')
        # if 'tsi' in indicators_to_include:
        #     df.ta.tsi(append=True)
        #     new_columns.append('tsi')
        # if 'uo' in indicators_to_include:
        #     df.ta.uo(append=True)
        #     new_columns.append('uo')
        # if 'variance' in indicators_to_include:
        #     df.ta.variance(append=True)
        #     new_columns.append('variance')
        # if 'vortex' in indicators_to_include:
        #     df.ta.vortex(append=True)
        #     new_columns.append('vortex_p14')
        #     new_columns.append('vortex_m14')
        # if 'vwap' in indicators_to_include:
        #     df.ta.vwap(append=True)
        #     new_columns.append('vwap')
        # if 'vwma' in indicators_to_include:
        #     df.ta.vwma(append=True)
        #     new_columns.append('vwma')
        # if 'willr' in indicators_to_include:
        #     df.ta.willr(append=True)
        #     new_columns.append('willr')
        # if 'wma' in indicators_to_include:
        #     df.ta.wma(append=True)
        #     new_columns.append('wma')
        # if 'zlma' in indicators_to_include:
        #     df.ta.zlma(append=True)
        #     new_columns.append('zlma')
        # if 'zscore' in indicators_to_include:
        #     df.ta.zscore(append=True)
        #     new_columns.append('zcore')
        #
        # # print(df.columns)
        # # print(old_columns + new_columns)
        # df.columns = old_columns + new_columns
        # return df


class PolygonDataFetcher(BaseDataFetcher):

    def __init__(self):
        super().__init__()
        self.api = AlpacaUtil.get_api()

    def get_aggs(self, ticker: str, start_date: str, end_date: str, timespan='day') -> DataFrame:
        # print('polygon_get_aggs')
        df = super().get_aggs(ticker, start_date, end_date, timespan)
        if df is None:
            if IS_VERBOSE:
                print('polygon_get_aggs_cache_was_null')
            res = None

            # Now parse out the multiplier if applicable
            multiplier = 1

            m = re.match(r"^\d+", timespan)
            if m is not None:
                multiplier = int(m.group())
                timespan = timespan[m.end():]

            try:
                if IS_VERBOSE:
                    print('fetching({}_{}-{}_{})'.format(ticker, start_date, end_date, timespan))

                res = self.api.polygon.historic_agg_v2(ticker,
                                                       multiplier=multiplier,
                                                       _from=start_date,
                                                       to=end_date,
                                                       timespan=timespan)
            except Exception as e:
                print('Error in get_aggs {}'.format(e))

            if res is not None:
                df = res.df
                df.reset_index(level=0, inplace=True)
                h = self.create_hash(ticker, start_date, end_date, timespan)
                self.set_cache(h, df)
                self.set_memory_cache(h, df)
        else:
            if IS_VERBOSE:
                print('cache({}_{}-{}_{})'.format(ticker, start_date, end_date, timespan))
        return df

    def get_snapshot(self, ticker: str) -> DataFrame:
        today_str = StringUtil.get_today_string()
        snapshot = self.api.polygon.snapshot(ticker)
        del snapshot.ticker['day']['vw']
        day_snapshot = snapshot.ticker['day']
        df = pd.DataFrame(day_snapshot, index=[today_str])
        alias = {
            't': 'timestamp',
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
        }
        df.reset_index(level=0, inplace=True)
        df.columns = [alias[c] for c in df.columns]
        return df


class YahooDataFetcher(BaseDataFetcher):
    def get_aggs(self, ticker: str, start_date: str, end_date: str, timespan='day') -> DataFrame:
        df = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
        # normalize to STD_FORMAT

        df.columns = [c.lower() for c in df.columns]
        del df['adj close']
        df.index = df.index.rename('timestamp')
        df.reset_index(level=0, inplace=True)
        return df

    def get_snapshot(self, ticker) -> DataFrame:
        start_date = end_date = StringUtil.get_today_string()
        df = pdr.get_data_yahoo(ticker, start=start_date, end=end_date)
        df.columns = [c.lower() for c in df.columns]
        del df['adj close']
        df.index = df.index.rename('timestamp')
        df.reset_index(level=0, inplace=True)
        return df
