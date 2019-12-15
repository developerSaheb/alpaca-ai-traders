import alpaca_trade_api as tradeapi


#Put it at this level so we're always reusing the instance
api = tradeapi.REST()


class AlpacaUtil(object):

    @staticmethod
    def get_api():
        return api

    @staticmethod
    def get_trade_api():
        return tradeapi
