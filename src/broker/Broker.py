

class Broker(object):

    def __init__(self, cash: float):
        self.cash = cash
        self.original_cash = cash


    def buy(self, ticker: str, size: int, price: float, time_in_force: str = 'fok', typ: str = 'limit', timestamp = None, log_action = None ) -> bool:
        raise NotImplementedError


    def sell(self, ticker: str, size: int, price: float, time_in_force: str = 'day', typ: str = 'stop', timestamp = None, log_action = None) -> bool:
        raise NotImplementedError


    def cancel_order(self, order):
        raise NotImplementedError

    def _update_position_data(self, ticker: str, timestamp, price : float ):
        raise NotImplementedError

    def report(self):
        raise NotImplementedError
