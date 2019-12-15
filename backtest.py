from src.strategy import BacktestStrategy
from src.strategy.impl import CharliesStrategy
from src.broker import PenAndPaperBroker
from src.util import CollectionUtil, Cacher
from src.util.StringUtil import StringUtil
from src.data_factory import DataFactory
import random

if __name__ == '__main__':
    # tickers = DataFactory.get_nasdaq100()
    # random.shuffle(all_tickers)
    # for tickers in CollectionUtil.chunks(all_tickers, 10):
    tickers = ['AMD', 'WMT', 'V', 'DELL', 'VMW']
    # tickers = list(DataFactory.get_nasdaq100()) + list(DataFactory.get_snp500())
    tickers = sorted(tickers)
    start_date = '2019-01-01'
    end_date = '2019-12-05'
    DataFactory.set_verbose(False)
    broker = PenAndPaperBroker(100000.00)
    strategy = CharliesStrategy(broker,
                                indicators=['macd', 'rsi', 'atr', 'vwma', 'mom'],
                                cash_per_position=10000,
                                full_replay=True,
                                full_replay_timespan='15minute')
    live_mode = False
    # Now the backtest
    replay = BacktestStrategy(strategy, start_date, end_date, tickers, live_mode=live_mode)
    replay.run()
    broker.report()
