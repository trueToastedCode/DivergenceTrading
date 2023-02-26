import asyncio
import logging
import os
from datetime import datetime

import config
from src.strategy.my_strategy import MyStrategy


async def main():
    logging.info('Init...')
    strategy = await MyStrategy.create(config)
    logging.info('Init ok, start trading')
    try:
        await strategy.run()
    finally:
        await strategy.klines_client.close_connection()
    # successful trading should never break the trading loop
    logging.error('Broke trading loop, position(s) might still be open')


if __name__ == '__main__':
    if not os.path.isdir('log'):
        os.mkdir('log')
    logging.basicConfig(
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%Y/%d/%m %H:%M:%S',
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(f'log/{int((datetime.utcnow()).timestamp())}.txt'),
            logging.StreamHandler()
        ]
    )
    asyncio.run(main())
