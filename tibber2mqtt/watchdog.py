import datetime

from logger import *
from helpers import get_argument

class Watchdog:
    def __init__(self, config: dict):
        tolerance = int(get_argument(config, 'watchdog', 'tolerance'))
        self.__tolerance = datetime.timedelta(seconds=tolerance)

        timeout = int(get_argument(config, 'watchdog', 'timeout'))
        self.__timeout = datetime.timedelta(seconds=timeout)
        self.__current_timeout = self.__timeout

        maximum_timeout = int(get_argument(config, 'watchdog', 'maximum_timeout'))
        self.__maximum_timeout = datetime.timedelta(seconds=maximum_timeout)

        self.__lost_at = None

    def check(self, last_timestamp):
        now = datetime.datetime.now()
        if last_timestamp + self.__tolerance < now:
            if self.__lost_at is None:
                logger.log('Lost tibber live data.')
                self.__lost_at = now
                return True
            seconds_until_reconnect = (self.__current_timeout - (now - self.__lost_at)).total_seconds()
            if seconds_until_reconnect <= 0:
                return False
            else:
                logger.log(f'{round(seconds_until_reconnect)}s until reconnect.')
        else:
            self.__reset_timeout()
            self.__lost_at = None
        return True
            
    def subscription_success(self, success):
        self.__lost_at = None
        if success:
            self.__reset_timeout()
        else:
            self.__timeout = min (self.__timeout * 2, self.__maximum_timeout)
            logger.log(f'Reconnect attempt in {round(self.__timeout.total_seconds())} seconds.')

    def __reset_timeout(self):
        self.__current_timeout = self.__timeout