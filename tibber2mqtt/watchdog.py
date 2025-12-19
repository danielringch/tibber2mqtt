import datetime, logging

from config import get_config_key
from tibberlive import Tibberlive

class Watchdog:
    def __init__(self, config: dict):
        tolerance = get_config_key(config, int, None, 'watchdog', 'tolerance')
        self.__tolerance = datetime.timedelta(seconds=tolerance)

        self.__timeout = get_config_key(config, int, None, 'watchdog', 'timeout')

        self.__maximum_timeout = get_config_key(config, int, None, 'watchdog', 'maximum_timeout')

        self.__current_timeout = None

    def check(self, tibber: Tibberlive):
        if (not tibber.connected) or ((tibber.last_data + self.__tolerance) < datetime.datetime.now()):
            logging.error('Lost tibber live data.')
            self.__current_timeout = self.__timeout \
                    if not self.__current_timeout \
                    else min(self.__maximum_timeout, 2 * self.__current_timeout)
            logging.debug(f'{round(self.__current_timeout)} s until reconnect.')
        else:
            self.__current_timeout = None

        return self.__current_timeout
