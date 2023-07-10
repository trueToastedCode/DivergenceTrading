import logging
import time

import ccxt.base.errors
from periodic_simpletime import get_next_periodic_dt

from .cache_processing.cache_processing import CacheProcessing
from ..signal import *
from ..binance.my_binance import MyBinance
from ..binance.klines_client import KlinesClient
from ..binance.make_trading_cache import make_trading_cache
from ..wait_connection import wait_connection


class MyStrategy:
    @classmethod
    async def create(cls, config):
        self = MyStrategy()
        self.config = config
        self.my_binance = MyBinance.create_with_key_file(
            **config.Args.create_my_binance_with_key_file())
        self.klines_client = await KlinesClient.create(
            **config.Args.klines_cache())
        self.cache_processing = CacheProcessing(
            **config.Args.trading_cache_init())
        self.trading_cache = await make_trading_cache(
            **config.Args.make_trading_cache(self.klines_client, self.cache_processing))
        self.last_oco_ids = None
        return self

    def long(self):
        logging.info('Received a long signal, try to open position')

        # abort long if position is open
        if self.last_oco_ids:
            try:
                orders = self.my_binance.get_open_orders()
            except Exception as e:
                logging.error(e)
                return
            for order in orders:
                if order['id'] in self.last_oco_ids:
                    logging.info('Position still open, abort')
                    return
            self.last_oco_ids = None

        # fetch and verify balance
        try:
            balance = self.my_binance.get_free_balance(self.config.CCXT_SYMBOL_B)
        except Exception as e:
            logging.error(e)
            return
        if balance < self.config.MIN_BALANCE:
            logging.error(f'Balance is {balance}, expected at least {self.config.MIN_BALANCE}')
            return

        # amount, stop-loss take-profit
        df = self.trading_cache.df

        amount = (balance * self.config.AMOUNT_USE) / df.Close[-1]
        amount = self.my_binance.exchange.amount_to_precision(self.config.CCXT_SYMBOL, amount)

        stop_loss = df.Close[-1] - self.config.SLAT_RATIO * df.ATR[-1]
        stop_loss = self.my_binance.exchange.price_to_precision(self.config.CCXT_SYMBOL, stop_loss)

        take_profit = df.Close[-1] + self.config.SLAT_RATIO * df.ATR[-1] * self.config.TPSL_RATIO
        take_profit = self.my_binance.exchange.price_to_precision(self.config.CCXT_SYMBOL, take_profit)

        logging.info(f'Opening Long [ amount: {amount}, tp: {take_profit}, sl: {stop_loss} ]')

        # market order
        logging.debug(f'Market buy [ amount: {amount} ]')
        try:
            market_order = self.my_binance.market_order(amount, 'buy')
        except Exception as e:
            logging.error(e)
            return
        logging.debug(f'Market buy ok')

        # wait for order to be filled
        logging.debug(f'Awaiting order to be filled...')
        while True:
            time.sleep(0.5)
            try:
                market_order_status = self.my_binance.fetch_order(market_order['info']['orderId'])
            except Exception as e:
                logging.error(e)
                wait_connection()
                continue
            status = market_order_status['info']['status'].upper()
            if status == 'NEW':
                logging.debug('The order has been accepted by the engine')
                continue
            elif status == 'PARTIALLY_FILLED':
                logging.warning('The order has been partially filled')
                break
            elif status == 'FILLED':
                logging.debug('The order has been completed')
                break
            elif status == 'CANCELED':
                logging.error('The order has been canceled by the user')
                return
            elif status == 'PENDING_CANCEL':
                logging.error('The order is currently unused.')
                return
            elif status == 'REJECTED':
                logging.error('The order was not accepted by the engine and not processed.')
                return
            elif status == 'EXPIRED':
                logging.error('The order was canceled according to the order type\'s rules or by the exchange.')
                return
            elif status == 'EXPIRED_IN_MATCH':
                logging.error('The order was expired by the exchange due to STP.')
                return
            else:
                logging.error(f'Order has unexpected status: {status}')
                return
        logging.debug(f'Order filled')

        # oco order
        amount = self.my_binance.exchange.amount_to_precision(
            self.config.CCXT_SYMBOL,
            float(market_order_status['info']['executedQty'])
        )
        logging.debug(f'Making oco order [ amount: {amount}, tp: {take_profit}, sl: {stop_loss} ]')

        is_funds_error = False
        while True:
            try:
                oco_order = self.my_binance.oco_order(amount, 'sell', take_profit, stop_loss, stop_loss)
                break
            except ccxt.base.errors.InsufficientFunds:
                if is_funds_error:
                    raise RuntimeError('Insufficient funds')
                logging.warning('Insufficient funds, try with with free balance instead of executed quantity again')
                is_funds_error = True
                amount = self.my_binance.exchange.amount_to_precision(
                    self.config.CCXT_SYMBOL,
                    self.my_binance.get_free_balance(self.config.CCXT_SYMBOL_A)
                )
        self.last_oco_ids = [item['orderId'] for item in oco_order['orders']]

        logging.info('Open Long ok')

    async def run(self):
        while True:
            next_dt = get_next_periodic_dt(self.config.PERIOD)
            try:
                df = await self.klines_client.fetch_klines_with_next_periodic_dt(next_dt)
            except Exception as e:
                logging.error(e)
                wait_connection()
                continue

            new_data_int_idx = self.trading_cache.concat(df)
            df = self.trading_cache.df

            if new_data_int_idx == len(df):
                logging.warning('No data has been added to cache, skipping interval')
                continue

            self.cache_processing.process_cache(df, new_data_int_idx)

            if df.index[-1] != next_dt - self.config.TIMEFRAME:
                logging.warning('Latest cache index doesn\'t match expected Datetime, ignoring signals')
                continue

            signal = df.TotalSignal[-1]
            if signal == LONG_SIGNAL:
                self.long()
            else:
                logging.debug('Received a nothing to do signal')
