import requests
import os
from http.cookies import SimpleCookie
from enum import Enum
import math


class Side(Enum):
    BUY = 'buy'


class Type(Enum):
    MARKET = 'market'


class PaperTrading:
    VIEW_HOST = 'https://www.tradingview.com'
    PAPER_HOST = 'https://papertrading.tradingview.com'
    
    def __init__(self, cookies, default_symbol):
        self.cookies = cookies
        self.default_symbol = default_symbol
        self.session = requests.session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://www.tradingview.com/'
        }

    @classmethod
    def create_paper_trading_with_cookie_file(cls, cookie_path: str, default_symbol: str):
        with open(cookie_path, 'r') as f:
            content = f.read()
        simple_cookie = SimpleCookie()
        simple_cookie.load(content)
        cookies = {
            'sessionid': simple_cookie.get('sessionid').value,
            'sessionid_sign': simple_cookie.get('sessionid_sign').value
        }
        return PaperTrading(cookies, default_symbol)

    @staticmethod
    def quantity_to_precision(quantity: float):
        return math.floor(quantity * 100000000) / 100000000

    @staticmethod
    def price_to_precision(price: float):
        return round(price, 2)

    def request(self, *args, **kwargs):
        response = self.session.request(*args, **kwargs)
        if response.status_code != 200:
            raise ValueError(f'{response.status_code} {response.reason}')
        return response

    def quote_token(self):
        payload = {'grabSession': True}
        response = self.request(
            'POST',
            f'{self.VIEW_HOST}/quote_token/',
            json=payload,
            cookies=self.cookies
        )
        return response.text[1:-1]

    def get_account(self):
        response = self.request(
            'POST',
            f'{self.PAPER_HOST}/trading/account/',
            json={},
            cookies=self.cookies
        )
        return response.json()

    def place_order(
        self,
        side: Side,
        type: Type,
        quantity: float,
        take_profit: float,
        stop_loss: float,
        symbol: str = None
    ):
        payload = {
            'symbol': symbol or self.default_symbol,
            'side': side.value,
            'type': type.value,
            'qty': quantity,
            'sl': stop_loss,
            'tp': take_profit
        }
        response = self.session.request(
            'POST',
            f'{self.PAPER_HOST}/trading/place/',
            json=payload,
            cookies=self.cookies
        )
        return response.json()
