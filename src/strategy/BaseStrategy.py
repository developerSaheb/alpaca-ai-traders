from pandas import DataFrame
from src.broker import Broker


# Overrideing this class, and the update_position() method
# will be all you need for doing the backtesting / replay
# update_position(ticker,data) will be called for every timeframe
# you have chosen in BacktestStrategy
# the broker you can change to Alpaca for a live broker 
class BaseStrategy(object):

    def __init__(self,
                 broker: Broker,
                 indicators: list,
                 full_replay: bool = False,
                 full_replay_timespan: str = 'hour'):
        self.broker: Broker = broker
        self.indicators = indicators
        self.pnl = 0
        self.blocked_tickers = ['TCOM', 'NLOK']
        self.full_replay = full_replay
        self.full_replay_timespan = full_replay_timespan
        self.MACD_SLOW = 21
        self.MACD_FAST = 9
        self.MACD_SIGNAL = 9
        self.indicators = indicators

    # The full list of indicators that will be delivered to the ticker are below
    # you can access it as df[INDICATOR_NAME] , like df['rsi'].values
    # will give you a list of previous rsi values, with the last element
    # the latest/current rsi
    # df.ta.macd(fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL, min_periods=None, append=True)
    # df.ta.rsi(append=True)
    # df.ta.rvi(append=True)
    # df.ta.increasing(append=True)
    # df.ta.decreasing(append=True)
    # df.ta.atr(append=True)
    # df.ta.adx(append=True)
    # df.ta.ao(append=True)
    # df.ta.bop(append=True)
    # df.ta.cci(append=True)
    # df.ta.cmf(append=True)
    # df.ta.dema(append=True)
    # df.ta.ema(length=MACD_FAST, append=True)
    # df.ta.ema(length=MACD_SLOW, append=True)
    # df.ta.cross('EMA_{}'.format(MACD_FAST), 'EMA_{}'.format(MACD_SLOW), append=True)
    # df.ta.efi(append=True)
    # df.ta.fisher(append=True)
    # df.ta.hma(append=True)
    # df.ta.kama(append=True)
    # df.ta.log_return(append=True)
    # df.ta.macd(length=MACD_FAST, append=True)
    # df.ta.macd(length=MACD_SLOW, append=True)
    # df.ta.mom(append=True)
    # df.ta.natr(append=True)
    # df.ta.nvi(append=True)
    # df.ta.pvi(append=True)
    # df.ta.pvt(append=True)
    # df.ta.qstick(append=True)
    # df.ta.roc(length=MACD_FAST, append=True)
    # df.ta.roc(length=MACD_SLOW, append=True)
    # df.ta.skew(length=MACD_FAST, append=True)
    # df.ta.skew(length=MACD_SLOW, append=True)
    # df.ta.slope(append=True)
    # df.ta.stdev(length=MACD_FAST, append=True)
    # df.ta.stdev(length=MACD_SLOW, append=True)
    # df.ta.stoch(append=True)
    # df.ta.t3(append=True)
    # df.ta.trix(append=True)
    # df.ta.true_range(append=True)
    # df.ta.tsi(append=True)
    # df.ta.uo(append=True)
    # df.ta.variance(append=True)
    # df.ta.vortex(append=True)
    # df.ta.vwap(append=True)
    # df.ta.vwma(append=True)
    # df.ta.willr(append=True)
    # df.ta.wma(append=True)
    # df.ta.zlma(append=True)
    # df.ta.zscore(append=True)

    # This method gets called for every timeframe you have chosen,
    # so once a day or every 15/10/5/1 mins etc
    def update_position(self, ticker: str, df: DataFrame) -> None:
        # This is needed for the replay , not used in live_mode
        # Just keep track of prices
        price = df['close'].values[-1]
        timestamp = df['timestamp'].values[-1]
        self.broker._update_position_data(ticker, timestamp, price)
