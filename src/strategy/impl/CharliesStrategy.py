from src.broker import Broker, Position
from src.strategy import BaseStrategy
from pandas import DataFrame
import pandas as pd


class CharliesStrategy(BaseStrategy):

    def __init__(self, broker: Broker,
                 indicators: list,
                 sell_threshold=0.05,
                 buy_threshold=-0.10,
                 cash_per_position=20000,
                 full_replay: bool = False,
                 full_replay_timespan: str = 'hour'):
        super().__init__(broker=broker, indicators=indicators, full_replay=full_replay,
                         full_replay_timespan=full_replay_timespan)
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.cash_per_position = cash_per_position

    def update_position(self, ticker: str, df: DataFrame):
        super().update_position(ticker, df)
        pos: Position = self.broker.get_position(ticker)
        if len(df) >= 2 and df.count()['macd'] > 4:
            price = df['close'].values[-1]
            timestamp = df['timestamp'].values[-1]
            fast = df['macd'].values[-1]
            fast_m1 = df['macd'].values[-2]
            fast_m2 = df['macd'].values[-3]
            #mom = df['mom'].values[-1]
            share_size = round(self.cash_per_position / price) - 1
            if pos.total_shares == 0:
                # If we should look at buying
                if fast < self.buy_threshold and fast_m1 < self.buy_threshold:
                    if fast > fast_m1 > fast_m2:
                        res, order = self.broker.buy(ticker, size=share_size, price=price, timestamp=timestamp)
                        # if not res:
                        # print('miss({})'.format(ticker))

            elif pos.total_shares > 0:
                if fast > self.sell_threshold:
                    # Its decreasing
                    if fast < fast_m1 :
                        print(
                            'SELL_SIGNAL {} at {} was {} on {} '.format(ticker, price, pos.last_buy_price, timestamp))
                        self.broker.sell(ticker, size=pos.total_shares, price=price, timestamp=timestamp,log_action='sell_from_signal')


                percent_change = (price - pos.last_buy_price) / pos.last_buy_price

                # if percent_change < -0.05:
                #     print(
                #         'SELL_LOSS {} at {} was {} on {} change {}'.format(ticker, price, pos.last_buy_price, timestamp,
                #                                                            percent_change))
                #     self.broker.sell(ticker, size=pos.total_shares, price=price, timestamp=timestamp,log_action='sell_from_loss')

                # Now if the profit is over 3%, then sell when the price drops 1% off the high
                if percent_change > 0.03:
                    # Calculate drop from high
                    distance_from_high = pos.highest_since_buy - price
                    one_percent_from_top = pos.highest_since_buy * 0.01
                    if distance_from_high > one_percent_from_top:
                        print('SELL_FROM_HIGH_SIGNAL {} at {} was {} on {}, distance_from_high={}, one_percent_from_top={}'.format(ticker, price, pos.last_buy_price, timestamp,distance_from_high, one_percent_from_top))
                        self.broker.sell(ticker, size=pos.total_shares, price=price, timestamp=timestamp,log_action='sell_from_high')


