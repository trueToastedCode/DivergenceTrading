import logging
import ccxt
import json


class MyBinance:
    def __init__(self, key, secret, default_symbol):
        self.exchange = ccxt.binance({
            'apiKey': key,
            'secret': secret
        })
        self.exchange.load_markets()
        self.default_symbol = default_symbol

    @classmethod
    def create_with_key_file(cls, key_path, default_symbol):
        try:
            with open(key_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            logging.error(f'Binance key file "{key_path}" does not exist.\n'
                          f'Please created it and ensure it contains:\n'
                          '{\n'
                          '  "key": "<your key>",\n'
                          '  "secret": "<your secret>"\n'
                          '}')
            exit(1)
        return MyBinance(data['key'], data['secret'], default_symbol)

    def market_order(self, amount, side, symbol=None):
        """
        :param amount: amount
        :param side: sell/buy
        :param symbol: symbol
        :return: order
        """
        return self.exchange.create_order(
            symbol or self.default_symbol, 'market', side, amount, None)

    def oco_order(self, amount, side, price, stop_price, stop_limit_price,
                  symbol=None, stop_limit_time_in_force='GTC'):
        """
        :param amount: amount
        :param side: sell/buy
        :param price: price at which to sell/buy if market goes for you
        :param stop_price: trigger if market goes against you
        :param stop_limit_price: price at which to sell/buy when stop has been triggered
        :param symbol: symbol
        :param stop_limit_time_in_force: GTC/IOC/FOK
        :return: order
        """
        return self.exchange.private_post_order_oco({
            'symbol': symbol or self.default_symbol,
            'quantity': amount,
            'side': side,
            'price': price,
            'stopPrice': stop_price,
            'stopLimitPrice': stop_limit_price,
            'stopLimitTimeInForce': stop_limit_time_in_force
        })

    def get_free_balance(self, symbol):
        return float(self.exchange.fetch_balance().get(symbol).get('free'))

    def get_latest_price(self, symbol=None):
        return float(self.exchange.fetch_ticker(symbol or self.default_symbol).get('last'))

    def get_open_orders(self, symbol=None):
        return self.exchange.fetch_open_orders(symbol or self.default_symbol)

    def cancel_order(self, id, symbol=None):
        return self.exchange.cancel_order(id, symbol or self.default_symbol)
