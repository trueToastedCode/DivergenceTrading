import socket
import time
import logging


def wait_connection(cooldown_s=1):
    was_offline = False
    while True:
        try:
            socket.create_connection(('1.1.1.1', 53))
            if was_offline:
                logging.info('Connection ok')
            return
        except OSError:
            if not was_offline:
                was_offline = True
                logging.error('Connection lost')
            time.sleep(cooldown_s)
