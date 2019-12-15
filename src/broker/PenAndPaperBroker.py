from src.broker import Position
from src.broker.Broker import Broker
from alpaca_trade_api.entity import Entity
import os
from collections import defaultdict
from src.util import TradeLogger
from .Position import Position

class PenAndPaperBroker(Broker):
    def __init__(self, cash):
        super().__init__(cash)
        self.log_path = os.path.dirname(__file__) + '{}..{}tradelogs'.format(os.sep, os.sep)
        self.log_header = 'TIME,TICKER,ACTION,SIZE,PRICE,PNL'
        self.log_format = '{},{},{},{},{},{}'
        self.reporter = TradeLogger(self.log_path, self.log_header)
        self.pnl_per_position = defaultdict(float)
        self.total_pnl = 0
        self.positions = defaultdict(Position)
        self.prev_log_msg = ''

    def buy(self, ticker: str, size: int, price: float, time_in_force: str = 'ioc', typ: str = 'limit', timestamp=None,
            log_action=None):
        total = size * price
        if total >= self.cash:
            return False, Entity({})

        pos = self.get_position(ticker)
        buy_price = size * price

        if self.cash - buy_price <= 0:
            #print('miss_{}'.format(ticker), end="")
            pass
        else:
            pos.pending_buy_shares += size
            pos.pending_buy_price = price

        # For pen and paper we update it right away since we're faking it
        # in AlpacaBroker we do it on update
        self.update_trade('buy', ticker, size, price, timestamp, log_action=log_action)
        return True, Entity({'id': ticker})

    def sell(self, ticker: str, size: int, price: float, time_in_force: str = 'day', typ: str = 'stop', timestamp=None,
             log_action=None):
        pos = self.get_position(ticker)
        pos.pending_sell_shares += size
        pos.pending_sell_price = price

        # For pen and paper we update it right away since we're faking it
        self.update_trade('sell', ticker, size, price, timestamp, log_action=log_action)
        pos: Position = self.get_position(ticker)
        pos.last_buy_price = 0
        pos.highest_since_buy = 0

        return True, Entity({'id': ticker})

    def update_trade(self, side: str, ticker: str, size: int, price: float, timestamp: None, log_action : str  = None):
        pos = self.get_position(ticker)
        pnl = 0
        if log_action is None :
            log_action = side

        if side == 'buy':
            pos.total_shares += size
            pos.pending_buy_shares -= size
            pos.pending_buy_price = 0
            pos.last_buy_price = price
            self.cash -= price * size

            print('{} :: Bought {} of {} for {} at {}'.format(timestamp, size, ticker, size * price, price))
            if pos.average_buy_price == 0:
                pos.average_buy_price = price
            else:
                pos.average_buy_price = (pos.average_buy_price + price) / 2
        elif side == 'sell':
            pos.last_sell_price = price
            pos.pending_sell_shares -= size
            pos.total_shares -= size
            pos.sell_history.append((ticker, size, price))
            close = price

            original_price = pos.last_buy_price
            buy_price = (original_price * size)
            sell_price = (size * close)
            pnl = sell_price - buy_price
            pos.last_pnl = pnl

            self.cash += sell_price
            self.pnl_per_position[ticker] += pnl
            self.total_pnl += pnl
            print(
                '{} :: Sold {} of {} at {}  for {} was {} (pnl{})'.format(timestamp, size, ticker, price, size * price,
                                                                          original_price, pnl))

        self.reporter.log(ticker, self.log_format.format(timestamp, ticker, log_action, size, price, pnl))

    def get_positions_value(self):
        return self.get_total_value(positions_only=True)

    def get_total_value(self, positions_only=False) -> float:
        ttl = 0
        for ticker in self.positions.keys():
            pos = self.get_position(ticker)
            if len(pos.price_history) >= 1:
                ttl += pos.price_history[-1] * pos.total_shares
            else:
                ttl += pos.average_buy_price * pos.total_shares
        if positions_only:
            return round(ttl, 2)

        else:
            return round(ttl + self.cash, 2)

    def get_open_positions(self) -> list:
        ret = []
        for p in self.positions.keys():
            if self.positions[p].total_shares > 0:
                ret.append(p)
        return ret

    def get_position(self, symbol) -> Position:
        position = None
        if symbol in self.positions:
            position = self.positions[symbol]
        else:
            position = Position(symbol)
            self.positions[symbol] = position
        return position

    def cancel_order(self, order):
        raise NotImplementedError

    def _update_position_data(self, ticker: str, timestamp, price: float):
        pos = self.get_position(ticker)
        pos.timestamp = timestamp
        if pos.last_buy_price:
            pos.highest_since_buy = max(pos.highest_since_buy, pos.last_buy_price, price)
            # print('BuyPrice={},Highest={},Price={}'.format(pos.last_buy_price, pos.highest_since_buy, price))
        pos.price_history.append(price)

    def report(self):
        ending_value = self.cash + self.get_positions_value()
        open_position_gain = ending_value - self.original_cash
        return_to_date = (self.total_pnl + open_position_gain) / self.original_cash
        print('\nStarting Cash: {}'.format(self.original_cash))
        print('Ending Cash: {}'.format(self.cash))
        print('Ending Position Value: {} - {}'.format(self.get_positions_value(), self.get_open_positions()))
        print('Ending Account Value : {}'.format(ending_value))
        print('Ending PNL: {}'.format(self.total_pnl))
        print('Return to date: {}'.format(return_to_date))
        print('\nPositions with PNL:')
        for p in self.pnl_per_position.keys():
            print('{}={}'.format(p, self.pnl_per_position[p]))
