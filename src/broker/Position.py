# This is all for the PenAndPaperBroker and backtesting

class Position(object):
    def __init__(self, ticker):
        self.ticker = ticker
        self.timestamp = 0
        self.total_shares = 0
        self.average_buy_price = 0
        self.highest_since_buy = 0
        self.last_buy_price = 0

        self.last_sell_price = 0
        self.last_pnl = 0

        self.pending_sell_shares = 0
        self.pending_sell_price = 0

        self.pending_buy_shares = 0
        self.pending_buy_price = 0

        self.price_history = []
        self.buy_history = []
        self.sell_history = []

    def current_value(self):
        last = self.price_history[-1]
        return last * self.total_shares
