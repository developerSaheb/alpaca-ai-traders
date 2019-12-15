from pandas import DataFrame

from src.util import DateUtil, CollectionUtil, Cacher
from src.data_factory import DataFactory, BaseDataFetcher
from datetime import datetime
from datetime import timedelta, date
from src.strategy import BaseStrategy
import multiprocessing as mp
import pandas as pd
from dask import delayed
import os
import time


def noop(x):
    pass


# TODO:  MAJOR BUG
# THERE IS A MAJOR BUG HERE
# Im replaying each ticker per day on different threads but sharing the same broker, the problem is each thread is replaying at a different speed
# So one thread will sell at 13:30 , and the other thread is only at 9:30 but is able to buy it because FUTURE FUNDS have freed up
# Proposed solution: God I dont know lock at the BAR level, wait for every thread to complete per bar,
# or try to implement the solution in the broker, only at time T add X funds, everytime a buy is placed, check the pending funds pool

class BacktestStrategy(object):

    def __init__(self, strategy: BaseStrategy, start_date: str, end_date: str, tickers: list, timespan='day',
                 start_date_fmt="%Y-%m-%d", end_date_fmt="%Y-%m-%d", live_mode: bool = False, MACD_SLOW: int = 21,
                 MACD_FAST: int = 9, MACD_SIGNAL: int = 9):
        # if not live_mode:
        # if isinstance(strategy.broker,AlpacaPaperBroker):
        #    raise Exception('You cannot have a Alpaca broker with a replay')
        self.timespan = timespan
        # Alpaca has bad data on these
        self.start_date = datetime.strptime(start_date, start_date_fmt)
        self.end_date = datetime.strptime(end_date, end_date_fmt)

        self.MACD_FAST = MACD_FAST
        self.MACD_SLOW = MACD_SLOW
        self.MACD_SIGNAL = MACD_SIGNAL
        self.start_str = start_date
        self.end_str = end_date
        self.tickers = tickers
        self.strategy = strategy
        self.live_mode = live_mode
        self.has_recorded = False
        self.data_fetcher = DataFactory.get_data_fetcher()
        # self.data_fetcher.load_cache()
        # print('cache loaded')
        self.aggs = {}
        self.all_dfs = {}
        print(
            'Live Mode is {}, Full Replay is {}, Full Replay Timespan is {}, Start={}, End={}'
                .format(live_mode,
                        self.strategy.full_replay,
                        self.strategy.full_replay_timespan,
                        self.start_str,
                        self.end_str))

    def _fetch_data(self, ticker, add_indicators=False):
        try:
            start_date = self.start_date.date()
            end_date = self.end_date.date()
            df = None
            if self.live_mode:
                start_date = (datetime.today() + timedelta(days=-120)).date()
                end_date = datetime.today().date()
                df = self.data_fetcher.get_aggs(ticker, start_date, end_date, timespan=self.timespan)

                # Get todays snapshot data
                try:
                    snapshot = self.data_fetcher.get_snapshot(ticker)
                    df = df.append(snapshot)
                except Exception as e:
                    print('skipping adding snapshot, exception' + str(e))
            else:
                df = self.data_fetcher.get_aggs(ticker, start_date, end_date, timespan=self.timespan)
                # if res is not None:
                #    df = self.aggs[ticker] = res

            if add_indicators and df is not None:
                DataFactory.add_indicators(df,
                                           macd_fast=self.MACD_FAST,
                                           macd_slow=self.MACD_SLOW,
                                           macd_signal=self.MACD_SIGNAL,
                                           indicators_to_include=self.strategy.indicators)
            return ticker, df
        except Exception as e:
            print('error in _fetch_data' + str(e))
            return None, None

    def run(self):

        start = time.time()
        pool = mp.Pool(mp.cpu_count())
        results = pool.map(self._fetch_data, self.tickers)
        pool.close()
        pool.join()
        self.all_dfs = {}
        for ticker, df in results:
            if ticker is not None and df is not None:
                # We check that the close price is less than $100 , over that is to expensive for us
                # Also ensure that the volume is sufficient to liquidate
                if len(df) and len(df['close']) and df['close'].values[-1] < 200.00 and \
                        len(df['volume']) and df['volume'].values[-1] > 100000:
                    self.all_dfs[ticker] = df
                    data_df = df.copy()
                    data_df = DataFactory.add_indicators(data_df, indicators_to_include=self.strategy.indicators);
                    data_df.to_csv(self.strategy.broker.reporter.path + ticker + '.df.csv')

        end = time.time()
        print('Total Tickers after filtering is {} took {} seconds'.format(len(self.all_dfs), end - start))
        # IF SINGLE THREADED
        # self.price_history = {}
        # for ticker in self.tickers:
        #     t, df = self._fetch_data(ticker)
        #     if t is not None and df is not None :
        #         self.price_history[ticker]= df
        # start = time.time()
        if self.live_mode:
            for ticker in self.tickers:
                final_df = self.all_dfs[ticker]
                self.strategy.update_position(ticker, final_df)
        else:
            # Prefetch the data into memory to see if this speeds things up

            # IF MULTI THREADED
            all_tickers = list(self.all_dfs.keys())
            print('Now starting replay')
            for i in range(DateUtil.days_between(self.start_date, self.end_date)):
                results = []
                for ticker in all_tickers:
                    result = delayed(self._replay_ticker_at_day)(ticker, i)
                    results.append(result)
                total = delayed(noop)(results)
                total.compute()
                end = time.time()
                print('Replayed {} tickers for {} pnl({}) took {} seconds'.format(all_tickers.__len__(),
                                                                                  self.start_date + timedelta(i),
                                                                                  self.strategy.broker.total_pnl,
                                                                                  end - start))

    def _replay_ticker_at_day(self,
                              ticker: str,
                              idx: int):
        strategy = self.strategy
        final_df = self.all_dfs[ticker]
        data_fetcher = self.data_fetcher

        # print('Replaying {} at index {}'.format(ticker, idx))
        if final_df is not None and ticker not in strategy.blocked_tickers:
            up_until_now_df = final_df.iloc[0:idx].copy()
            if not strategy.full_replay:
                if idx > strategy.MACD_SLOW:
                    cur_slice = up_until_now_df.copy()
                    try:
                        DataFactory.add_indicators(cur_slice, macd_fast=strategy.MACD_FAST,
                                                   macd_slow=strategy.MACD_SLOW,
                                                   indicators_to_include=strategy.indicators)
                        strategy.update_position(ticker, cur_slice)
                    except Exception as e:
                        raise Exception('{}-{}'.format(ticker, e))
                # print('{} - {}'.format(cur_slice['timestamp'] , cur_slice['close']))

            else:
                if idx > strategy.MACD_SLOW:
                    yesterdays_volume = up_until_now_df['volume'].values[-2]

                    cur_date = pd.to_datetime(up_until_now_df['timestamp'].values[-1]).date()
                    cur_aggs = data_fetcher.get_aggs(ticker, cur_date, cur_date + timedelta(1),
                                                     strategy.full_replay_timespan)
                    if cur_aggs is not None:
                        total_volume = 0
                        for cur_idx, cur_row in cur_aggs.iterrows():

                            # IF CACHE EXISTS USE IT
                            h = Cacher.create_hash('__', ticker, cur_date, cur_date + timedelta(1),
                                                   strategy.full_replay_timespan, *(sorted(strategy.indicators)))
                            cur_slice = Cacher.static_get_cache(h)
                            if cur_slice is not None:
                                pass
                            else:

                                cur_slice = up_until_now_df.copy()

                                # drop last row, this is our end of day closing price
                                cur_slice.drop(cur_slice.tail(1).index, inplace=True)
                                # Now add the minute by minute for the entire day, fully simulating
                                # What we do in live mode
                                cur_slice = cur_slice.append(cur_row, ignore_index=True)
                                total_volume += cur_slice['volume'].values[-1]
                                # Adjust the volume, the volume for the snapshots and for past data are
                                # volume for the bar not the total
                                if total_volume > yesterdays_volume:
                                    cur_slice.at[-1, 'volume'] = total_volume
                                    # cur_slice.iloc[-1]['volume'] = total_volume
                                else:
                                    cur_slice.at[len(cur_slice) - 1, 'volume'] = yesterdays_volume
                                    # cur_slice.iloc[-1]['volume'] = yesterdays_volume

                                DataFactory.add_indicators(cur_slice, macd_fast=strategy.MACD_FAST,
                                                           macd_slow=strategy.MACD_SLOW)
                                Cacher.set_cache(h, cur_slice)

                            # Now update
                            strategy.update_position(ticker, cur_slice)

        ret = ticker + '_finished'
        # print('{},'.format(ret), end="")
        return ret
