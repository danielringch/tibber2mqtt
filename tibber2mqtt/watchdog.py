import datetime, logging

from helpers import get_argument
from tibberlive import Tibberlive

class Watchdog:
    def __init__(self, config: dict):
        tolerance = int(get_argument(config, 'watchdog', 'tolerance'))
        self.__tolerance = datetime.timedelta(seconds=tolerance)

        self.__timeout = int(get_argument(config, 'watchdog', 'timeout'))

        self.__maximum_timeout = int(get_argument(config, 'watchdog', 'maximum_timeout'))

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
